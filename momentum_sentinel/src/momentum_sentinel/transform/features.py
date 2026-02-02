import pandas as pd
import pandas_ta as ta
import yaml
import pathlib

# --- Path Anchoring ---
# Finds the absolute path to the project root (3 levels up from this file)
CURRENT_FILE = pathlib.Path(__file__).resolve()
BASE_DIR = CURRENT_FILE.parents[3]

class FeatureEngineer:
    def __init__(self, config_name: str = "configs/config.yaml"):
        # Anchor config to project root
        config_path = BASE_DIR / config_name
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config not found at {config_path}")

        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        # Anchor data paths
        self.raw_path = BASE_DIR / "data/raw"
        self.proc_path = BASE_DIR / "data/processed"
        self.proc_path.mkdir(parents=True, exist_ok=True)

    def get_raw_data(self, ticker: str) -> pd.DataFrame:
        path = self.raw_path / f"{ticker.lower()}.parquet"
        if not path.exists():
            raise FileNotFoundError(f"Raw data not found at {path}. Run ingest/fetcher.py first.")
        return pd.read_parquet(path)

    def apply_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        fast = self.config['strategy_params']['sma_fast']
        slow = self.config['strategy_params']['sma_slow']

        # Professional Vectorized Indicators
        df['sma_fast'] = ta.sma(df['close'], length=fast)
        df['sma_slow'] = ta.sma(df['close'], length=slow)

        # Signal Logic: 1 for Buy, 0 for Neutral/Sell
        df['signal'] = 0.0
        df.loc[df['sma_fast'] > df['sma_slow'], 'signal'] = 1.0
        
        # Shift(1) is CRITICAL to avoid Look-Ahead Bias
        # You see the signal at today's close, you trade at tomorrow's open
        df['signal'] = df['signal'].shift(1) 

        return df.dropna()

    def save_processed_data(self, df: pd.DataFrame, name: str):
        file_path = self.proc_path / f"{name.lower()}_features.parquet"
        df.to_parquet(file_path)
        print(f"[+] Features successfully saved at {file_path}")

if __name__ == "__main__":
    engineer = FeatureEngineer()
    ticker_sym = engineer.config['assets']['ticker']
    
    try:
        raw_df = engineer.get_raw_data(ticker_sym)
        feature_df = engineer.apply_signals(raw_df)
        engineer.save_processed_data(feature_df, ticker_sym)
    except Exception as e:
        print(f"[!] Error in Feature Engineering: {e}")