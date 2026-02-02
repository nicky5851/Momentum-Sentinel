import pandas as pd
import quantstats as qs
import yaml
import pathlib
import sys

# --- Path Anchoring ---
CURRENT_FILE = pathlib.Path(__file__).resolve()
BASE_DIR = CURRENT_FILE.parents[3] 

class AnalyticsProvider:
    def __init__(self, config_name: str = "configs/config.yaml"):
        config_path = BASE_DIR / config_name
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        self.report_path = BASE_DIR / "reports"
        self.report_path.mkdir(exist_ok=True)

    def generate_tearsheet(self, results_df: pd.DataFrame, ticker: str):
        """Generates a professional-grade HTML report."""
        # QuantStats needs percentage returns (not log returns) for its math
        # We calculate the daily change from the equity curve
        returns = results_df['cum_strategy_returns'].pct_change().dropna()
        benchmark = results_df['cum_market_returns'].pct_change().dropna()
        
        file_name = self.report_path / f"{ticker}_tearsheet.html"
        print(f"[*] Generating professional report at {file_name}...")
        
        qs.reports.html(
            returns, 
            benchmark=benchmark, 
            output=str(file_name), 
            title=f"Momentum Sentinel: {ticker} Strategy Report"
        )

if __name__ == "__main__":
    # Import the Backtester from your internal engine module
    from momentum_sentinel.engine.backtester import Backtester
    
    # 1. Initialize and Run Backtest
    bt = Backtester()
    ticker = bt.config['assets']['ticker']
    
    print(f"[*] Loading data and running engine for {ticker}...")
    try:
        data = bt.load_data(ticker)
        results = bt.run_backtest(data)
        
        # 2. Generate Report
        analytics = AnalyticsProvider()
        analytics.generate_tearsheet(results, ticker)
        print(f"[+] Success! Open the report at: {analytics.report_path}/{ticker}_tearsheet.html")
    except Exception as e:
        print(f"[!] Pipeline failed: {e}")