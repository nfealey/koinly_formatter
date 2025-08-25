import pandas as pd
import os
from datetime import datetime
import pytz


class SparrowToKoinly:
    def __init__(self, source_file, output_dir):
        self.source_file = source_file
        self.output_dir = output_dir

    def convert(self):
        try:
            # Validate input file exists and is readable
            if not os.path.exists(self.source_file):
                raise FileNotFoundError(f"Source file not found: {self.source_file}")
            if not os.path.isfile(self.source_file):
                raise ValueError(f"Source path is not a file: {self.source_file}")
            if not self.source_file.lower().endswith('.csv'):
                raise ValueError(f"Source file must be a CSV file: {self.source_file}")
                
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
                df_koinly["Amount"] = (df_filtered["Value"] / 100_000_000).map("{:.8f}".format)
            except Exception as e:
                raise ValueError(f"Error converting amounts: {e}")
                
            df_koinly["Currency"] = "BTC"  # Assuming all values are BTC
            df_koinly["Label"] = df_filtered["Label"].replace("", pd.NA)
            df_koinly["TxHash"] = df_filtered["Txid"]

            # Ensure output directory exists
            try:
                os.makedirs(self.output_dir, exist_ok=True)
            except Exception as e:
                raise RuntimeError(f"Cannot create output directory: {e}")
                
            # Save the output to CSV in Koinly format
            current_datetime = datetime.now(pytz.utc).strftime("%Y-%m-%d_%H-%M-%S")
            output_file = os.path.join(
                self.output_dir, f"sparrow_wallet_{current_datetime}.csv"
            )
            
            try:
                df_koinly.to_csv(output_file, index=False)
            except PermissionError:
                raise PermissionError(f"Cannot write to output file: {output_file}. Check file permissions.")
            except Exception as e:
                raise RuntimeError(f"Error writing output file: {e}")

            print(f"Conversion successful! Output saved to: {output_file}")
            print(f"Total transactions processed: {len(df_koinly)}")
            return output_file
            
        except Exception as e:
            # Re-raise exception with context
            raise RuntimeError(f"Sparrow wallet conversion failed: {str(e)}")

