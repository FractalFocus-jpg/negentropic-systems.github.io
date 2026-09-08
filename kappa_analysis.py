"""LEGACY S&P 500 κ experiment — historical reproduction only.

The March 12, 2026 experiment originally reported this computation as a
successful validation. A 2026-09-08 independent cold audit found target
circularity, an inappropriate baseline, and full-sample target-threshold
leakage. The historical computation is retained, but its validation
interpretation is retired.

Current terminal:
REPRODUCIBLE_CODE__CIRCULAR_TARGET__DOMINATED_BY_TRIVIAL_BASELINES__NO_INDEPENDENT_PREDICTIVE_CONTENT_DEMONSTRATED

Use kappa_validation_v2.py for the preregistered clean replacement test.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import precision_score, recall_score, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("LEGACY KAPPA EXPERIMENT: S&P 500")
print("HISTORICAL COMPUTATION ONLY — VALIDATION CLAIM RETIRED 2026-09-08")
print("See VALIDATION_AUDIT.md and VALIDATION_PROTOCOL_V2.md")
print("=" * 60)

import os
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, 'sp500.csv')
df = pd.read_csv(data_path, index_col=0, parse_dates=True, skiprows=[1, 2])
df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
df['returns'] = df['Close'].pct_change()


def compute_kappa(data, window=20):
    beta = data['returns'].rolling(window).std() * np.sqrt(252)
    trend = data['Close'].rolling(50).mean()
    D = abs(data['Close'] - trend) / trend

    def safe_autocorr(x):
        if len(x) < 2:
            return 0
        try:
            return x.autocorr(lag=1)
        except Exception:
            return 0

    autocorr = data['returns'].rolling(window).apply(safe_autocorr)
    rho = 1 - abs(autocorr)
    kappa = (beta * D) / (rho + 0.001)
    return kappa, beta, D, rho


df['kappa'], df['beta'], df['D'], df['rho'] = compute_kappa(df)

# HISTORICAL TARGET CONSTRUCTION — KNOWN CIRCULARITY.
# beta above and volatility below are the same 20-day rolling-volatility
# series. This block is preserved only so the March computation can still be
# reproduced and inspected.
df['volatility'] = df['returns'].rolling(20).std() * np.sqrt(252)
vol_threshold = df['volatility'].quantile(0.8)  # KNOWN full-sample leakage
df['high_vol'] = (df['volatility'] > vol_threshold).astype(int)

train = df[df.index < '2024-01-01'].copy()
test = df[df.index >= '2024-01-01'].copy()

kappa_threshold = train['kappa'].quantile(0.95)
df['kappa_signal'] = (df['kappa'] > kappa_threshold).astype(int)
df['prediction'] = df['kappa_signal'].shift(1)

test['kappa_signal'] = (test['kappa'] > kappa_threshold).astype(int)
test['prediction'] = test['kappa_signal'].shift(1)
test_clean = test.dropna(subset=['prediction', 'high_vol']).copy()

if len(test_clean) == 0:
    raise RuntimeError('No historical test rows available')

y_true = test_clean['high_vol']
y_pred = test_clean['prediction']
precision = precision_score(y_true, y_pred, zero_division=0)
recall = recall_score(y_true, y_pred, zero_division=0)
cm = confusion_matrix(y_true, y_pred)
if cm.shape == (2, 2):
    tn, fp, fn, tp = cm.ravel()
else:
    tn = fp = fn = tp = 0

baseline_precision = y_true.mean()

print(f"Loaded {len(df)} rows")
print(f"Historical target threshold (full-sample q80; invalid for confirmation): {vol_threshold:.2%}")
print(f"Historical kappa threshold (train q95): {kappa_threshold:.6f}")
print(f"Historical precision: {precision:.2%} ({tp}/{tp + fp if tp + fp else 0})")
print(f"Historical recall: {recall:.2%} ({tp}/{tp + fn if tp + fn else 0})")
print(f"Historical prevalence comparison: {baseline_precision:.2%} — NOT an adequate persistence baseline")

# Historical strategy calculation retained as a diagnostic only.
test_clean['strategy_returns'] = np.where(
    test_clean['kappa_signal'].shift(1) == 1,
    0,
    test_clean['returns'],
)
test_clean['cumulative_market'] = (1 + test_clean['returns']).cumprod()
test_clean['cumulative_strategy'] = (1 + test_clean['strategy_returns']).cumprod()
market_vol = test_clean['returns'].std() * np.sqrt(252)
strategy_vol = test_clean['strategy_returns'].std() * np.sqrt(252)

fig, axes = plt.subplots(4, 1, figsize=(12, 10))
ax1 = axes[0]
ax1_twin = ax1.twinx()
ax1.plot(df.index, df['Close'], alpha=0.7, label='S&P 500')
ax1_twin.plot(df.index, df['kappa'], alpha=0.5, label='kappa')
ax1_twin.axhline(y=kappa_threshold, linestyle='--', alpha=0.5)
ax1.set_ylabel('S&P 500')
ax1_twin.set_ylabel('kappa')
ax1.set_title('Historical S&P 500 price vs kappa')

ax2 = axes[1]
ax2.scatter(df['kappa'], df['volatility'], alpha=0.3)
ax2.axvline(x=kappa_threshold, linestyle='--', alpha=0.5)
ax2.set_xlabel('kappa')
ax2.set_ylabel('Same-window rolling volatility target source')
ax2.set_title('Historical circularity diagnostic')

ax3 = axes[2]
ax3.plot(test.index, test['high_vol'], label='Historical target', alpha=0.7)
ax3.plot(test.index, test['prediction'], label='Historical kappa signal', alpha=0.7)
ax3.set_title('Historical predictions vs target')
ax3.legend()

ax4 = axes[3]
ax4.plot(test_clean.index, test_clean['cumulative_market'], label='Market', alpha=0.7)
ax4.plot(test_clean.index, test_clean['cumulative_strategy'], label='Historical strategy', alpha=0.7)
ax4.set_title('Historical strategy diagnostic — not validation evidence')
ax4.legend()

plt.tight_layout()
plt.savefig('kappa_validation_results.png', dpi=150)

print("=" * 60)
print("CURRENT TERMINAL")
print("REPRODUCIBLE_CODE__CIRCULAR_TARGET__DOMINATED_BY_TRIVIAL_BASELINES__NO_INDEPENDENT_PREDICTIVE_CONTENT_DEMONSTRATED")
print("Run kappa_validation_v2.py for the clean preregistered successor.")
print("=" * 60)
