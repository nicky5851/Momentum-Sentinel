import yfinance as yf
import pandas as pd
import yaml
import pathlib

class DataIngestor:
    def __init__(self, config_path: str = "configs/config.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        self.raw_path = pathlib.Path("data/raw")
        self.raw_path.mkdir(parents=True, exist_ok=True)

    def fetch_data(self):
        """Fetches historical data based on YAML config."""
        params = self.config['assets']
        bt_params = self.config['backtest_params']
        
        ticker = params['ticker']
        print(f"[*] Extracting {ticker} from Yahoo Finance...")
        
        df = yf.download(
            ticker, 
            start=bt_params['start_date'], 
            end=bt_params['end_date'],
            interval="1d"
        )
        
        if df.empty:
            raise ValueError(f"No data found for {ticker}. Check connection or ticker symbol.")

        # Standardizing schema: lowercase and underscore-separated
        df.columns = [col[0].lower().replace(" ", "_") if isinstance(col, tuple) else col.lower().replace(" ", "_") for col in df.columns]
        
        return df

    def save_data(self, df: pd.DataFrame, name: str):
        """Saves to Parquet for high-speed I/O."""
        file_path = self.raw_path / f"{name}.parquet"
        df.to_parquet(file_path, engine='pyarrow')
        print(f"[+] Data successfully cached at {file_path}")

if __name__ == "__main__":
    ingestor = DataIngestor()
    data = ingestor.fetch_data()
    ingestor.save_data(data, ingestor.config['assets']['ticker'].lower())