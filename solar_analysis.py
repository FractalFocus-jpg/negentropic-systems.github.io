import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta

print("=" * 60)
print("KAPPA-FRAMEWORK: SOLAR WEATHER VALIDATION")
print("Real-time NOAA Space Weather Data")
print("=" * 60)

# Fetch solar wind data
print("\nFetching solar wind data from NOAA...")
try:
    response = requests.get('https://services.swpc.noaa.gov/products/solar-wind/mag-1-day.json')
    mag_data = response.json()
    
    # Parse magnetic field data
    columns = mag_data[0]
    data = mag_data[1:]
    
    df = pd.DataFrame(data, columns=columns)
    df['time_tag'] = pd.to_datetime(df['time_tag'])
    df = df.set_index('time_tag')
    
    # Convert to numeric
    for col in ['bx_gsm', 'by_gsm', 'bz_gsm', 'bt']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    print(f"Loaded {len(df)} measurements")
    print(f"Time range: {df.index[0]} to {df.index[-1]}")
    
    # Calculate solar wind kappa
    # Beta: magnetic field variance (energy input)
    # D: deviation from typical values
    # Rho: stability of field direction
    
    # Beta: Total field strength variance
    df['beta'] = df['bt'].rolling('1H').std()  # 1-hour rolling std
    
    # D: Bz component (southward = storm potential)
    # Negative Bz = geomagnetic storm risk
    df['D'] = abs(df['bz_gsm']) / 10.0  # Normalize to typical range
    
    # Rho: Field stability (low variance = high stability)
    field_variance = df['bt'].rolling('3H').var()
    df['rho'] = 1.0 / (1.0 + field_variance)  # High variance = low rho
    
    # Kappa calculation
    df['kappa'] = (df['beta'] * df['D']) / (df['rho'] + 0.01)
    
    # Get current values
    current = df.iloc[-1]
    
    print(f"\n{'='*60}")
    print("CURRENT SOLAR CONDITIONS")
    print(f"{'='*60}")
    print(f"Time: {df.index[-1]}")
    print(f"Total Field (Bt): {current['bt']:.2f} nT")
    print(f"Bz Component: {current['bz_gsm']:.2f} nT")
    print(f"Beta: {current['beta']:.3f}")
    print(f"D: {current['D']:.3f}")
    print(f"Rho: {current['rho']:.3f}")
    print(f"Kappa: {current['kappa']:.4f}")
    
    # Interpretation
    kappa_recent = df['kappa'].dropna().iloc[-24:]  # Last 24 hours
    kappa_threshold = kappa_recent.quantile(0.8)
    
    print(f"\nKappa threshold (80th percentile, 24h): {kappa_threshold:.4f}")
    
    if current['kappa'] > kappa_threshold:
        print("\n[!] STATUS: ELEVATED")
        print("   Kappa above threshold - elevated geomagnetic activity possible")
        if current['bz_gsm'] < -5:
            print("   Strong southward Bz - storm conditions likely")
    else:
        print("\n[OK] STATUS: STABLE")
        print("   Kappa normal - quiet geomagnetic conditions")
    
    # Fetch Kp forecast
    print(f"\n{'='*60}")
    print("NOAA Kp FORECAST")
    print(f"{'='*60}")
    
    try:
        kp_response = requests.get('https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json')
        kp_data = kp_response.json()
        
        print("Next 3 days:")
        for item in kp_data[1:4]:  # First 3 forecasts
            date = item[0]
            kp = item[1]
            print(f"  {date}: Kp = {kp}")
    except:
        print("  (Kp forecast unavailable)")
    
    # Save data
    df.to_csv('solar_wind_kappa.csv')
    print(f"\n✓ Data saved to: solar_wind_kappa.csv")
    
    # Prediction log
    with open('solar_predictions.log', 'a') as f:
        f.write(f"{datetime.now()}: kappa={current['kappa']:.4f}, Bz={current['bz_gsm']:.2f}")
        if current['kappa'] > kappa_threshold:
            f.write(" [ELEVATED]")
        f.write("\n")
    
    print(f"✓ Prediction logged")
    
except Exception as e:
    print(f"Error: {e}")
    print("Could not fetch NOAA data")

print(f"\n{'='*60}")
print("Solar kappa-framework: Active monitoring")
print(f"{'='*60}")
