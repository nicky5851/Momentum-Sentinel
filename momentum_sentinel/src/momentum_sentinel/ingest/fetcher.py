import yfinance as yf
import pandas as pd
import yaml
import pathlib

# --- Path Anchoring ---
# 1. backtester.py -> 2. engine -> 3. momentum_sentinel -> 4. src -> 5. momentum_sentinel -> 6. Root
CURRENT_FILE = pathlib.Path(__file__).resolve()
BASE_DIR = CURRENT_FILE.parents[3] 

class DataIngestor:
    def __init__(self, config_name: str = "configs/config.yaml"):
        # Anchor the config path to the true Project Root
        config_path = BASE_DIR / config_name
        
        print(f"[*] Looking for config at: {config_path}")
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config not found! BASE_DIR is: {BASE_DIR}")

        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        # Anchor data path
        self.raw_path = BASE_DIR / "data/raw"
        self.raw_path.mkdir(parents=True, exist_ok=True)

    def fetch_data(self):
        params = self.config['assets']
        bt_params = self.config['backtest_params']
        
        df = yf.download(
            params['ticker'], 
            start=bt_params['start_date'], 
            end=bt_params['end_date']
        )
        
        # Clean column names
        df.columns = [col[0].lower().replace(" ", "_") if isinstance(col, tuple) else col.lower().replace(" ", "_") for col in df.columns]
        return df

    def save_data(self, df: pd.DataFrame, name: str):
        file_path = self.raw_path / f"{name.lower()}.parquet"
        df.to_parquet(file_path)
        print(f"[+] Data saved to {file_path}")

if __name__ == "__main__":
    ingestor = DataIngestor()
    ticker = ingestor.config['assets']['ticker']
    data = ingestor.fetch_data()
    ingestor.save_data(data, ticker)