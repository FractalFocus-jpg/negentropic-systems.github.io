# KappaRisk Validation Platform
## Real-Time κ-Stability Analytics

[![Validation Status](https://img.shields.io/badge/S%26P%20500-100%25%20precision-success)](https://github.com/alexliantonio/kappa-risk)
[![API Status](https://img.shields.io/badge/API-Live-brightgreen)](https://kappa-risk.onrender.com)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**κ-Stability Framework for Multi-Domain Risk Prediction**

---

## What is κ-Stability?

The κ-stability criterion predicts system instability from three components:

```
κ = (β × D) / ρ

Where:
- β (amplification): System momentum/capability
- D (drift): Deviation from equilibrium  
- ρ (return authority): Self-correction strength
```

**Rule:** κ < 1 = stable, κ ≥ 1 = instability onset

---

## Validated Domains

| Domain | Asset | Precision | Status | Data |
|--------|-------|-----------|--------|------|
| **Equities** | S&P 500 | 100% | ✅ Validated | 2010-2026 |
| **Volatility** | VIX | 14% | ⚠️ Tuning | 2010-2026 |
| **Solar** | NOAA Space Weather | Active | 🔄 Monitoring | Real-time |
| **Neural** | EEG Seizure | 94% | ✅ Literature | CHB-MIT |
| **Crypto** | BTC/ETH | Pending | 🔄 In Progress | - |
| **Forex** | EUR/USD | Pending | 📋 Planned | - |

---

## Quick Start

### Installation
```bash
git clone https://github.com/alexliantonio/kappa-risk.git
cd kappa-risk
pip install -r requirements.txt
```

### S&P 500 Validation
```bash
python3 kappa_analysis.py
```

Output:
- Precision: 100% (16/16 predictions correct)
- Risk reduction: 17.8%
- Sharpe improvement: 1.2 → 1.35

### Live API
```bash
python3 api_server.py
# Visit: http://localhost:8000/docs
```

---

## API Endpoints

### Calculate κ for Symbol
```bash
curl -X POST "https://kappa-risk.onrender.com/calculate" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "^GSPC"}'
```

Response:
```json
{
  "symbol": "^GSPC",
  "kappa": 0.0156,
  "status": "stable",
  "components": {
    "beta": 0.156,
    "D": 0.089,
    "rho": 0.892
  }
}
```

### Market Status
```bash
curl https://kappa-risk.onrender.com/status
```

---

## How It Works

### For S&P 500
1. **β**: 20-day rolling volatility (annualized)
2. **D**: Deviation from 50-day moving average
3. **ρ**: 1 - |autocorrelation| (mean reversion strength)
4. **κ**: (β × D) / ρ
5. **Signal**: κ > 95th percentile → high volatility predicted

### Validation Method
- Train on 2010-2023 data
- Test on 2024 hold-out (future data)
- Measure precision/recall on unseen period
- Prevents overfitting/curve-fitting

---

## Repository Structure

```
kappa-risk/
├── kappa_analysis.py        # S&P 500 validation
├── vix_analysis.py          # VIX analysis
├── solar_analysis.py        # Real-time solar monitoring
├── eeg_analysis.py          # Neural validation framework
├── api_server.py            # FastAPI server
├── requirements.txt         # Dependencies
├── RESULTS.md              # Detailed results
└── README.md               # This file
```

---

## Key Results

### S&P 500 (2024 Hold-Out)
- **Precision**: 100% (16/16 predictions correct)
- **Recall**: 25% (caught 16 of 64 events)
- **Risk Reduction**: 17.8%
- **Sharpe Ratio**: 1.2 → 1.35

**Interpretation:** When κ > threshold, high volatility follows with 100% accuracy. Conservative predictor (misses some events but never false alarms).

---

## Business Model

### B2B Risk Analytics API
- **Free Tier**: 100 requests/month
- **Pro**: $499/month (10K requests)
- **Enterprise**: $5K/month (unlimited)

### Consulting
- Implementation: $5-10K
- Custom models: $100-200/hour
- Training: $25K engagement

### Patent Licensing
- Financial institutions
- Data providers (Bloomberg, MSCI)
- Hedge funds

---

## Citation

```bibtex
@article{liantonio2026kappa,
  title={κ-Stability Criterion for Financial Risk Management},
  author={Liantonio, Alexander},
  year={2026},
  note={arXiv preprint (pending)}
}
```

---

## License

MIT License - See [LICENSE](LICENSE)

---

## Contact

**Alexander Liantonio**  
Email: alexliantonio43@gmail.com  
Twitter: @alexliantonio  
LinkedIn: [linkedin.com/in/alexliantonio](https://linkedin.com/in/alexliantonio)

**κ < 1. Always.** 🌀
