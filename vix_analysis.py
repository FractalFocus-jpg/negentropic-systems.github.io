import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import precision_score, recall_score, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("KAPPA-FRAMEWORK VALIDATION: VIX")
print("Date: 2026-03-12")
print("=" * 60)

# Load VIX data
df = pd.read_csv('vix.csv', index_col=0, parse_dates=True, skiprows=[1,2])
df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
df['returns'] = df['Close'].pct_change()

print(f"\nLoaded {len(df)} rows of VIX data")
print(f"Date range: {df.index[0]} to {df.index[-1]}")
print(f"VIX range: {df['Close'].min():.2f} to {df['Close'].max():.2f}")

# KAPPA CALCULATION (adapted for VIX mean-reversion)
def compute_kappa_vix(data, window=10):  # Shorter window for faster VIX
    """
    VIX-specific kappa:
    - Beta: volatility of volatility
    - D: deviation from long-term mean (VIX mean-reverts)
    - Rho: strength of mean-reversion
    """
    # Beta: VIX daily change volatility
    vix_changes = data['Close'].diff()
    beta = vix_changes.rolling(window).std()
    
    # Long-term mean (VIX typically ~20)
    long_mean = data['Close'].rolling(252).mean()  # 1-year mean
    D = abs(data['Close'] - long_mean) / long_mean
    
    # Rho: mean reversion strength (autocorrelation of changes)
    def safe_autocorr(x):
        if len(x) < 2:
            return 0
        try:
            return x.autocorr(lag=1)
        except:
            return 0
    
    autocorr = vix_changes.rolling(window).apply(safe_autocorr)
    rho = 1 - abs(autocorr)  # High autocorr = weak mean reversion
    
    kappa = (beta * D) / (rho + 0.001)
    return kappa, beta, D, rho

print("\nCalculating VIX-specific kappa...")
df['kappa'], df['beta'], df['D'], df['rho'] = compute_kappa_vix(df)

# Define VIX spike events (top 15% daily increases)
df['vix_change'] = df['Close'].pct_change()
spike_threshold = df['vix_change'].quantile(0.85)  # Top 15% daily jumps
df['vix_spike'] = (df['vix_change'] > spike_threshold).astype(int)

print(f"\nVIX spike threshold (85th percentile): {spike_threshold:+.2%}")
print(f"VIX spike days: {df['vix_spike'].sum()} ({df['vix_spike'].mean():.1%})")

# Check kappa statistics
print(f"\nKappa statistics:")
print(f"  Mean: {df['kappa'].mean():.4f}")
print(f"  90th percentile: {df['kappa'].quantile(0.9):.4f}")
print(f"  95th percentile: {df['kappa'].quantile(0.95):.4f}")

# SPLIT: Train on 2010-2023, Test on 2024
train = df[df.index < '2024-01-01'].copy()
test = df[df.index >= '2024-01-01'].copy()

# Adaptive threshold
train_kappa_90th = train['kappa'].quantile(0.90)
kappa_threshold = train_kappa_90th
print(f"\nKappa threshold (90th percentile): {kappa_threshold:.4f}")

# Predict VIX spikes
test['kappa_signal'] = (test['kappa'] > kappa_threshold).astype(int)
test['prediction'] = test['kappa_signal'].shift(1)  # Predict today from yesterday's kappa
test['prediction_5day'] = test['kappa_signal'].rolling(5).max().shift(1)  # 5-day window

print(f"\n{'='*60}")
print("VIX VALIDATION (2024-2025)")
print(f"{'='*60}")

# Next-day prediction
test_clean = test.dropna(subset=['prediction', 'vix_spike'])
if len(test_clean) > 0:
    y_true = test_clean['vix_spike']
    y_pred = test_clean['prediction']
    
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    
    cm = confusion_matrix(y_true, y_pred)
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
    else:
        tn = fp = fn = tp = 0
    
    baseline = y_true.mean()
    
    print(f"\nNext-day prediction:")
    print(f"  Precision: {precision:.1%} ({tp}/{tp+fp})")
    print(f"  Recall: {recall:.1%} ({tp}/{tp+fn})")
    print(f"  Baseline: {baseline:.1%}")
    print(f"  Improvement: {precision-baseline:+.1%}")

# 5-day window prediction
test_clean_5d = test.dropna(subset=['prediction_5day', 'vix_spike'])
if len(test_clean_5d) > 0:
    y_true_5d = test_clean_5d['vix_spike']
    y_pred_5d = test_clean_5d['prediction_5day']
    
    precision_5d = precision_score(y_true_5d, y_pred_5d, zero_division=0)
    recall_5d = recall_score(y_true_5d, y_pred_5d, zero_division=0)
    
    print(f"\n5-day window prediction:")
    print(f"  Precision: {precision_5d:.1%}")
    print(f"  Recall: {recall_5d:.1%}")

# Plot
fig, axes = plt.subplots(3, 1, figsize=(12, 8))

# VIX price and kappa
ax1 = axes[0]
ax1_twin = ax1.twinx()
ax1.plot(df.index, df['Close'], color='purple', alpha=0.7, label='VIX')
ax1_twin.plot(df.index, df['kappa'], color='red', alpha=0.5, label='kappa')
ax1_twin.axhline(y=kappa_threshold, color='red', linestyle='--', alpha=0.3)
ax1.set_ylabel('VIX', color='purple')
ax1_twin.set_ylabel('kappa', color='red')
ax1.set_title('VIX vs kappa')
ax1.legend(loc='upper left')
ax1_twin.legend(loc='upper right')

# Spike predictions
ax2 = axes[1]
ax2.plot(test.index, test['vix_spike'], label='Actual Spike', alpha=0.7)
ax2.plot(test.index, test['prediction'], label='kappa Predicted', alpha=0.7)
ax2.set_ylabel('VIX Spike')
ax2.set_title('VIX Spike Prediction (2024)')
ax2.legend()

# Scatter: kappa vs next-day VIX change
df['next_day_change'] = df['vix_change'].shift(-1)
ax3 = axes[2]
scatter = ax3.scatter(df['kappa'], df['next_day_change'], alpha=0.3, c=df.index.astype(int), cmap='plasma')
ax3.axvline(x=kappa_threshold, color='red', linestyle='--', alpha=0.5)
ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)
ax3.set_xlabel('kappa')
ax3.set_ylabel('Next-day VIX Change')
ax3.set_title('kappa vs Next-day VIX Change')
plt.colorbar(scatter, ax=ax3, label='Date')

plt.tight_layout()
plt.savefig('vix_validation_results.png', dpi=150)
print("\nSaved: vix_validation_results.png")

print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
print(f"VIX kappa-framework: {precision:.0%} precision, {recall:.0%} recall")
if precision > baseline:
    print("Status: SUCCESS")
else:
    print("Status: NEEDS IMPROVEMENT")
print(f"{'='*60}")
