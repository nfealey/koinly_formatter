# No change needed here, just use the class definition

import pandas as pd
import pandas as pd
import os
from datetime import datetime
import pytz

class SparrowToKoinly:
    def __init__(self, source_file, output_dir):
        self.source_file = source_file
        self.output_dir = output_dir

    def convert(self):
        # Load the Sparrow CSV
        df = pd.read_csv(self.source_file)

        # Prepare the Koinly-formatted DataFrame
        df_koinly = pd.DataFrame()
        df_koinly["Koinly Date"] = pd.to_datetime(df["Date (UTC)"]).dt.strftime(
            "%Y-%m-%d %H:%M UTC"
        )

        df_koinly["Amount"] = (df["Value"] / 100_000_000).map("{:.8f}".format)
        df_koinly["Currency"] = "BTC"  # Assuming all values are BTC
        df_koinly["Label"] = df["Label"].replace("", pd.NA)
        df_koinly["TxHash"] = df["Txid"]

        # Save the output to CSV in Koinly format
        current_datetime = datetime.now(pytz.utc).strftime("%Y-%m-%d_%H-%M-%S")
        output_file = os.path.join(self.output_dir, f"sparrow_wallet_{current_datetime}.csv")
        df_koinly.to_csv(output_file, index=False)

        print(f"Koinly-formatted CSV saved to: {output_file}")


# python3 -m venv path/to/venv
# source path/to/venv/bin/activate
# python3 -m pip install xyz
