# Momentum Sentinel 🛡️

**Professional Quantitative Backtesting Engine**

A modular, production-grade backtesting framework built in Python for analyzing Momentum strategies. This engine decouples data ingestion, feature engineering, and execution logic to ensure reproducible financial research.

## 🚀 Features

- **Vectorized Backtesting**: Uses NumPy and Pandas for high-speed performance.
- **Data Integrity**: Automated ingestion from Yahoo Finance with Parquet serialization.
- **Path Anchoring**: Robust absolute path discovery for reliable execution in any environment.
- **Professional Analytics**: Generates full HTML tearsheets via `QuantStats` (Sharpe, Drawdown, Sortino).

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **Data**: Pandas, PyArrow (Parquet)
- **Quant Math**: NumPy, Pandas-TA
- **Reporting**: QuantStats, Matplotlib

## 📊 The Strategy: SMA Crossover

This engine currently implements a dual Moving Average Crossover strategy:

- **Signal**: Buy when Fast SMA > Slow SMA.
- **Execution**: Signal is shifted by $t+1$ to prevent **Look-Ahead Bias**.

## 🚦 Getting Started

1. **Setup Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
