import pandas as pd
from .wallet_utils import BaseWalletConverter


class SparrowToKoinly(BaseWalletConverter):
    def __init__(self, source_file, output_dir):
        super().__init__(source_file, output_dir)

    def convert(self):
        try:
            # Use base class validation
            self.validate_source_file()
                
            # Load the Sparrow CSV
            try:
                df = pd.read_csv(self.source_file)
            except pd.errors.EmptyDataError:
                raise ValueError("Source CSV file is empty")
            except pd.errors.ParserError as e:
                raise ValueError(f"Invalid CSV format: {e}")
            except Exception as e:
                raise RuntimeError(f"Error reading source file: {e}")
                
            # Validate required columns exist
            required_columns = ["Date (UTC)", "Value", "Label", "Txid"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns in Sparrow CSV: {', '.join(missing_columns)}")
                
            # Check if dataframe has any data
            if df.empty:
                raise ValueError("No data found in source CSV file")

            # Prepare the Koinly-formatted DataFrame
            df_koinly = pd.DataFrame()
            
            # Filter out rows with invalid dates
            df_filtered = df[pd.to_datetime(df["Date (UTC)"], errors="coerce").notna()]
            if df_filtered.empty:
                raise ValueError("No valid dates found in source data")
                
            # Convert dates
            try:
                df_koinly["Koinly Date"] = pd.to_datetime(df_filtered["Date (UTC)"]).dt.strftime(
                    "%Y-%m-%d %H:%M UTC"
                )
            except Exception as e:
                raise ValueError(f"Error converting dates: {e}")

            # Convert amounts from satoshis to BTC
            try:
                # Use base class method for conversion
                amounts_btc = df_filtered["Value"].apply(lambda x: self.sats_to_btc(x))
                df_koinly["Amount"] = amounts_btc.apply(lambda x: self.format_btc(x))
            except Exception as e:
                raise ValueError(f"Error converting amounts: {e}")
                
            df_koinly["Currency"] = "BTC"  # Assuming all values are BTC
            df_koinly["Label"] = df_filtered["Label"].replace("", pd.NA)
            df_koinly["TxHash"] = df_filtered["Txid"]

            # Convert DataFrame to list of dicts for base class
            self.final_csv = df_koinly.to_dict('records')
            self.export_keys = list(df_koinly.columns)
            
            # Use base class method to write CSV
            return self.write_csv("sparrow_wallet")
            
        except Exception as e:
            # Re-raise exception with context
            raise RuntimeError(f"Sparrow wallet conversion failed: {str(e)}")

