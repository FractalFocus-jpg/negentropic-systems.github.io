import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import yfinance as yf
from sklearn.metrics import precision_score, recall_score
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("KAPPA-FRAMEWORK VALIDATION: CRYPTOCURRENCY")
print("Bitcoin & Ethereum Analysis")
print("=" * 60)

# Download crypto data
print("\nDownloading BTC-USD data...")
btc = yf.download('BTC-USD', start='2015-01-01', end='2026-03-12', progress=False)
print(f"BTC: {len(btc)} days")

print("Downloading ETH-USD data...")
eth = yf.download('ETH-USD', start='2015-01-01', end='2026-03-12', progress=False)
print(f"ETH: {len(eth)} days")

def analyze_crypto(data, name):
    """Analyze cryptocurrency with kappa framework"""
    print(f"\n{'='*60}")
    print(f"{name} ANALYSIS")
    print(f"{'='*60}")
    
    # Prepare data - handle MultiIndex columns from yfinance
    data = data.copy()
    
    # Flatten MultiIndex if present
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [' '.join(col).strip() if col[1] not in ['nan', 'NaN'] else col[0] 
                        for col in data.columns.values]
        # Find Close column
        close_col = [c for c in data.columns if 'Close' in c][0]
    else:
        close_col = 'Close'
    
    data['Close'] = pd.to_numeric(data[close_col], errors='coerce')
    data['returns'] = data['Close'].pct_change()
    
    # Calculate kappa (crypto-specific: higher volatility, faster mean reversion)
    window = 14  # Shorter window for crypto
    trend_period = 30
    
    # Beta: rolling volatility
    beta = data['returns'].rolling(window).std() * np.sqrt(365)  # Crypto trades 365 days
    
    # D: deviation from trend
    trend = data['Close'].rolling(trend_period).mean()
    D = abs(data['Close'] - trend) / trend
    
    # Rho: mean reversion (crypto has strong mean reversion after big moves)
    def safe_autocorr(x):
        if len(x) < 2:
            return 0
        try:
            return x.autocorr(lag=1)
        except:
            return 0
    
    autocorr = data['returns'].rolling(window).apply(safe_autocorr)
    rho = 1 - abs(autocorr)
    
    # Kappa
    data['kappa'] = (beta * D) / (rho + 0.001)
    
    # Define high volatility for crypto (>10% daily move)
    data['volatility'] = data['returns'].rolling(window).std() * np.sqrt(365)
    vol_threshold = data['volatility'].quantile(0.85)
    data['high_vol'] = (data['volatility'] > vol_threshold).astype(int)
    
    print(f"Volatility threshold (85th percentile): {vol_threshold:.1%}")
    print(f"High volatility days: {data['high_vol'].sum()} ({data['high_vol'].mean():.1%})")
    
    # Split: Train on 2015-2023, Test on 2024-2026
    train = data[data.index < '2024-01-01'].copy()
    test = data[data.index >= '2024-01-01'].copy()
    
    if len(train) == 0 or len(test) == 0:
        print("Insufficient data for train/test split")
        return None
    
    # Adaptive threshold
    train_kappa_90th = train['kappa'].quantile(0.90)
    kappa_threshold = max(0.1, train_kappa_90th)  # Crypto has higher baseline kappa
    
    print(f"Kappa threshold (90th percentile): {kappa_threshold:.4f}")
    
    # Predict
    test['kappa_signal'] = (test['kappa'] > kappa_threshold).astype(int)
    test['prediction'] = test['kappa_signal'].shift(1)
    test_clean = test.dropna(subset=['prediction', 'high_vol'])
    
    if len(test_clean) == 0:
        print("No test data after cleaning")
        return None
    
    y_true = test_clean['high_vol']
    y_pred = test_clean['prediction']
    
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    baseline = y_true.mean()
    
    print(f"\nHOLD-OUT VALIDATION (2024-2026):")
    print(f"  Precision: {precision:.1%}")
    print(f"  Recall: {recall:.1%}")
    print(f"  Baseline: {baseline:.1%}")
    print(f"  Improvement: {precision-baseline:+.1%}")
    
    return {
        'name': name,
        'precision': precision,
        'recall': recall,
        'baseline': baseline,
        'kappa_threshold': kappa_threshold,
        'data': data
    }

# Analyze both
targets = [
    (btc, 'Bitcoin (BTC-USD)'),
    (eth, 'Ethereum (ETH-USD)')
]

results = []
for data, name in targets:
    try:
        result = analyze_crypto(data, name)
        if result:
            results.append(result)
    except Exception as e:
        print(f"Error analyzing {name}: {e}")

# Summary
print(f"\n{'='*60}")
print("CRYPTO VALIDATION SUMMARY")
print(f"{'='*60}")

for r in results:
    status = "SUCCESS" if r['precision'] > r['baseline'] else "NEEDS WORK"
    print(f"\n{r['name']}:")
    print(f"  Precision: {r['precision']:.1%} (baseline: {r['baseline']:.1%})")
    print(f"  Status: {status}")

# Plot
if results:
    fig, axes = plt.subplots(len(results), 1, figsize=(12, 4*len(results)))
    if len(results) == 1:
        axes = [axes]
    
    for i, r in enumerate(results):
        ax = axes[i]
        data = r['data']
        
        ax_twin = ax.twinx()
        ax.plot(data.index, data['Close'], color='blue', alpha=0.7, label='Price')
        ax_twin.plot(data.index, data['kappa'], color='red', alpha=0.5, label='kappa')
        ax_twin.axhline(y=r['kappa_threshold'], color='red', linestyle='--', alpha=0.3)
        
        ax.set_ylabel('Price (USD)', color='blue')
        ax_twin.set_ylabel('kappa', color='red')
        ax.set_title(f"{r['name']} - Price vs kappa")
        ax.legend(loc='upper left')
        ax_twin.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig('crypto_validation_results.png', dpi=150)
    print("\nSaved: crypto_validation_results.png")

print(f"\n{'='*60}")
print("NEXT: Forex analysis (EUR/USD)")
print(f"{'='*60}")
