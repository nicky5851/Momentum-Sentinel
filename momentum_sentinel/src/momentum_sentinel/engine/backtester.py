import pandas as pd
import numpy as np
import yaml
import pathlib
import matplotlib.pyplot as plt

# --- Path Anchoring ---
# This finds the absolute path to the project root (3 levels up from this file)
CURRENT_FILE = pathlib.Path(__file__).resolve()
BASE_DIR = CURRENT_FILE.parents[3]

class Backtester:
    def __init__(self, config_name: str = "configs/config.yaml"):
        # Anchor the config path to the project root
        config_path = BASE_DIR / config_name
        
        if not config_path.exists():
            raise FileNotFoundError(f"Could not find config at {config_path}. Check your folder structure!")

        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        # Anchor data paths to the project root
        self.proc_path = BASE_DIR / "data/processed"

    def load_data(self, ticker: str) -> pd.DataFrame:
        path = self.proc_path / f"{ticker.lower()}_features.parquet"
        if not path.exists():
            raise FileNotFoundError(f"Processed data not found at {path}. Did you run features.py?")
        return pd.read_parquet(path)

    def run_backtest(self, df: pd.DataFrame):
        """
        Calculates returns and equity curve using vectorized math.
        """
        # Calculate daily log returns for the market
        df['market_returns'] = np.log(df['close'] / df['close'].shift(1))

        # Strategy returns = (Signal from yesterday) * (Market return today)
        # The shift(1) is handled in features.py, so we use 'signal' directly here
        df['strategy_returns'] = df['signal'] * df['market_returns']

        # Cumulative returns (Equity Curve)
        df['cum_market_returns'] = df['market_returns'].cumsum().apply(np.exp)
        df['cum_strategy_returns'] = df['strategy_returns'].cumsum().apply(np.exp)

        return df

    def plot_results(self, df: pd.DataFrame, ticker: str):
        plt.figure(figsize=(12, 6))
        plt.plot(df['cum_market_returns'], label='Market (Buy & Hold)', color='gray', alpha=0.6)
        plt.plot(df['cum_strategy_returns'], label='SMA Strategy', color='blue', linewidth=2)
        plt.title(f"Momentum Sentinel: {ticker} Performance")
        plt.xlabel("Date")
        plt.ylabel("Growth of $1")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Save plot to reports folder
        report_path = BASE_DIR / "reports"
        report_path.mkdir(exist_ok=True)
        plt.savefig(report_path / f"{ticker}_equity_curve.png")
        print(f"[+] Equity curve saved to {report_path}")
        plt.show()

if __name__ == "__main__":
    # Initialize Backtester
    tester = Backtester()
    ticker_sym = tester.config['assets']['ticker']
    
    # Execute Pipeline
    try:
        data = tester.load_data(ticker_sym)
        results = tester.run_backtest(data)
        
        final_roi = (results['cum_strategy_returns'].iloc[-1] - 1) * 100
        print(f"--- Backtest Results: {ticker_sym} ---")
        print(f"Total Strategy Return: {final_roi:.2f}%")
        
        tester.plot_results(results, ticker_sym)
        
    except Exception as e:
        print(f"[!] Error during backtest: {e}")