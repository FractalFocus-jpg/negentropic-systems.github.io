import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from sklearn.metrics import precision_score, recall_score, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("KAPPA-FRAMEWORK VALIDATION: S&P 500")
print("Date: 2026-03-12")
print("=" * 60)

# Load data
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, 'sp500.csv')
# Skip first 2 rows (multi-level header from yfinance)
df = pd.read_csv(data_path, index_col=0, parse_dates=True, skiprows=[1,2])
print(f"\nLoaded {len(df)} rows of data")
print(f"Date range: {df.index[0]} to {df.index[-1]}")
print(f"Columns: {list(df.columns)}")

# Ensure Close is numeric
df['Close'] = pd.to_numeric(df['Close'], errors='coerce')

# Calculate returns
df['returns'] = df['Close'].pct_change()

# KAPPA-PARAMETER DEFINITIONS
def compute_kappa(data, window=20):
    """
    kappa = beta * D / rho
    
    beta (amplification): Rolling volatility (annualized)
    D (drift): Deviation from trend / trend
    rho (return authority): Mean reversion strength (1 - |autocorr|)
    """
    # beta: rolling volatility
    beta = data['returns'].rolling(window).std() * np.sqrt(252)
    
    # Trend: 50-day moving average
    trend = data['Close'].rolling(50).mean()
    
    # D: deviation from trend (normalized)
    D = abs(data['Close'] - trend) / trend
    
    # rho: mean reversion (1 - autocorrelation)
    def safe_autocorr(x):
        if len(x) < 2:
            return 0
        try:
            return x.autocorr(lag=1)
        except:
            return 0
    
    autocorr = data['returns'].rolling(window).apply(safe_autocorr)
    rho = 1 - abs(autocorr)
    
    # kappa calculation
    kappa = (beta * D) / (rho + 0.001)  # small epsilon to avoid div by zero
    
    return kappa, beta, D, rho

print("\nCalculating kappa parameters...")
df['kappa'], df['beta'], df['D'], df['rho'] = compute_kappa(df)

# Define high volatility events
df['volatility'] = df['returns'].rolling(20).std() * np.sqrt(252)
vol_threshold = df['volatility'].quantile(0.8)  # Top 20% volatility days
df['high_vol'] = (df['volatility'] > vol_threshold).astype(int)

print(f"\nVolatility threshold (80th percentile): {vol_threshold:.2%}")
print(f"High volatility days: {df['high_vol'].sum()} ({df['high_vol'].mean():.1%})")

# SPLIT: Train on 2010-2023, Test on 2024
train = df[df.index < '2024-01-01'].copy()
test = df[df.index >= '2024-01-01'].copy()

# KAPPA PREDICTION SIGNAL
# Rule: kappa > threshold predicts high volatility in next 1-5 days
# Adaptive threshold based on training data - using 95th percentile
# (Kappa values are typically very small: median ~0.003, 95th ~0.02)
train_kappa_95th = train['kappa'].quantile(0.95)
kappa_threshold = train_kappa_95th  # Use 95th percentile as threshold
print(f"\nAdaptive kappa threshold (95th percentile): {kappa_threshold:.4f}")
df['kappa_signal'] = (df['kappa'] > kappa_threshold).astype(int)

# Predict next-day volatility
df['prediction'] = df['kappa_signal'].shift(1)  # Predict today based on yesterday's kappa

print(f"\nKappa threshold: {kappa_threshold:.3f}")
print(f"Days with kappa > {kappa_threshold}: {df['kappa_signal'].sum()}")

print(f"\n{'='*60}")
print("HOLD-OUT VALIDATION (2024 Data)")
print(f"{'='*60}")
print(f"Training period: {train.index[0]} to {train.index[-1]} ({len(train)} days)")
print(f"Test period: {test.index[0]} to {test.index[-1]} ({len(test)} days)")

# Add prediction column to test set
test['kappa_signal'] = (test['kappa'] > kappa_threshold).astype(int)
test['prediction'] = test['kappa_signal'].shift(1)

# Calculate metrics on test set
test_clean = test.dropna(subset=['prediction', 'high_vol'])

if len(test_clean) > 0:
    y_true = test_clean['high_vol']
    y_pred = test_clean['prediction']
    
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    
    # Calculate true positives, false positives, etc.
    cm = confusion_matrix(y_true, y_pred)
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
    else:
        tn = fp = fn = tp = 0
    
    print(f"\nResults on 2024 hold-out data:")
    print(f"  Precision: {precision:.2%} ({tp} correct / {tp+fp} predicted)")
    print(f"  Recall: {recall:.2%} ({tp} found / {tp+fn} actual)")
    print(f"  True Positives: {tp}")
    print(f"  False Positives: {fp}")
    print(f"  True Negatives: {tn}")
    print(f"  False Negatives: {fn}")
    
    # Baseline (random guess)
    baseline_precision = y_true.mean()
    print(f"\n  Baseline (random): {baseline_precision:.2%}")
    print(f"  Improvement: {precision - baseline_precision:+.2%}")
    
    # Risk-adjusted return simulation
    print(f"\n{'='*60}")
    print("STRATEGY SIMULATION")
    print(f"{'='*60}")
    
    # Strategy: Go to cash when kappa > threshold (avoid high vol periods)
    test_clean['strategy_returns'] = np.where(
        test_clean['kappa_signal'].shift(1) == 1,
        0,  # Cash when high kappa predicted
        test_clean['returns']  # Market otherwise
    )
    
    test_clean['cumulative_market'] = (1 + test_clean['returns']).cumprod()
    test_clean['cumulative_strategy'] = (1 + test_clean['strategy_returns']).cumprod()
    
    market_return = test_clean['cumulative_market'].iloc[-1] - 1
    strategy_return = test_clean['cumulative_strategy'].iloc[-1] - 1
    
    market_vol = test_clean['returns'].std() * np.sqrt(252)
    strategy_vol = test_clean['strategy_returns'].std() * np.sqrt(252)
    
    print(f"Market return (2024): {market_return:.2%}")
    print(f"Strategy return (2024): {strategy_return:.2%}")
    print(f"Market volatility: {market_vol:.2%}")
    print(f"Strategy volatility: {strategy_vol:.2%}")
    if market_vol > 0:
        print(f"Risk reduction: {(1 - strategy_vol/market_vol):.1%}")

# PLOT
print(f"\n{'='*60}")
print("Generating plots...")
print(f"{'='*60}")

fig, axes = plt.subplots(4, 1, figsize=(12, 10))

# Plot 1: Price and kappa
ax1 = axes[0]
ax1_twin = ax1.twinx()
ax1.plot(df.index, df['Close'], color='blue', alpha=0.7, label='S&P 500')
ax1_twin.plot(df.index, df['kappa'], color='red', alpha=0.5, label='kappa')
ax1_twin.axhline(y=kappa_threshold, color='red', linestyle='--', alpha=0.5)
ax1.set_ylabel('S&P 500', color='blue')
ax1_twin.set_ylabel('kappa', color='red')
ax1.set_title('S&P 500 Price vs kappa')
ax1.legend(loc='upper left')
ax1_twin.legend(loc='upper right')

# Plot 2: kappa vs Realized Volatility
ax2 = axes[1]
scatter = ax2.scatter(df['kappa'], df['volatility'], alpha=0.3, c=df.index.astype(int), cmap='viridis')
ax2.axvline(x=kappa_threshold, color='red', linestyle='--', alpha=0.5)
ax2.set_xlabel('kappa')
ax2.set_ylabel('Realized Volatility')
ax2.set_title('kappa vs Realized Volatility')
plt.colorbar(scatter, ax=ax2, label='Date')

# Plot 3: Time series of predictions (2024 only)
ax3 = axes[2]
ax3.plot(test.index, test['high_vol'], label='Actual High Vol', alpha=0.7)
ax3.plot(test.index, test['prediction'], label='kappa Prediction', alpha=0.7)
ax3.set_ylabel('High Volatility Event')
ax3.set_title('Predictions vs Actual (2024)')
ax3.legend()

# Plot 4: Cumulative returns
if len(test_clean) > 0:
    ax4 = axes[3]
    ax4.plot(test_clean.index, test_clean['cumulative_market'], label='Market', alpha=0.7)
    ax4.plot(test_clean.index, test_clean['cumulative_strategy'], label='kappa Strategy', alpha=0.7)
    ax4.set_ylabel('Cumulative Return')
    ax4.set_title('Strategy Performance (2024)')
    ax4.legend()

plt.tight_layout()
plt.savefig('kappa_validation_results.png', dpi=150)
print("Saved: kappa_validation_results.png")

# SUMMARY
print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
print(f"Kappa-Framework predicts high volatility with:")
if len(test_clean) > 0:
    print(f"  Precision: {precision:.1%} (vs {baseline_precision:.1%} baseline)")
    print(f"  Recall: {recall:.1%}")
    if market_vol > 0:
        print(f"  Risk reduction: {(1 - strategy_vol/market_vol):.1%}")
    success = precision > baseline_precision
    print(f"\nValidation: {'SUCCESS' if success else 'FAIL'}")
else:
    print("  No test data available")
print(f"{'='*60}")
