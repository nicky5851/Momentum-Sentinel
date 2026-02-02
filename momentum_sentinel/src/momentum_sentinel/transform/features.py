import pandas as pd
import pandas_ta as ta
import yaml
import pathlib

class FeatureEngineer:
    def __init__(self, config_path: str = "configs/config.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        self.raw_path = pathlib.Path("data/raw")
        self.proc_path = pathlib.Path("data/processed")
        self.proc_path.mkdir(parents=True, exist_ok=True)

    def get_raw_data(self, ticker: str) -> pd.DataFrame:
        """Loads the parquet file generated in Phase 2."""
        path = self.raw_path / f"{ticker.lower()}.parquet"
        if not path.exists():
            raise FileNotFoundError(f"Raw data for {ticker} not found. Run Ingestion first.")
        return pd.read_parquet(path)

    def apply_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates Technical Indicators and Trading Signals.
        Logic: 1 for Buy (Fast > Slow), 0 for Neutral/Sell.
        """
        fast_period = self.config['strategy_params']['sma_fast']
        slow_period = self.config['strategy_params']['sma_slow']

        # Calculate SMAs using pandas_ta (vectorized)
        df['sma_fast'] = ta.sma(df['close'], length=fast_period)
        df['sma_slow'] = ta.sma(df['close'], length=slow_period)

        # Generate Signal: 1 when fast is above slow, else 0
        # We use .shift(1) because we can only trade on the NEXT open 
        # after a signal is generated at today's close (avoiding look-ahead bias).
        df['signal'] = 0.0
        df.loc[df['sma_fast'] > df['sma_slow'], 'signal'] = 1.0
        df['signal'] = df['signal'].shift(1) 

        # Drop NaN values created by the SMA window
        return df.dropna()

    def save_processed_data(self, df: pd.DataFrame, name: str):
        file_path = self.proc_path / f"{name}_features.parquet"
        df.to_parquet(file_path)
        print(f"[+] Features saved at {file_path}")

if __name__ == "__main__":
    engineer = FeatureEngineer()
    ticker = engineer.config['assets']['ticker']
    
    raw_df = engineer.get_raw_data(ticker)
    feature_df = engineer.apply_signals(raw_df)
    engineer.save_processed_data(feature_df, ticker.lower())