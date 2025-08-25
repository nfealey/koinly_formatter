"""Base wallet converter utilities for cryptocurrency wallet format conversions.

This module provides abstract base classes and common functionality for converting
various cryptocurrency wallet export formats to Koinly-compatible CSV format.
"""

import os
import csv
import logging
from datetime import datetime
import pytz
from abc import ABC, abstractmethod
from typing import List, Set, Dict, Any

# Configure logger
logger = logging.getLogger(__name__)


class BaseWalletConverter(ABC):
    """Abstract base class for wallet converters with shared functionality.

    This class provides common methods and utilities for converting cryptocurrency
    wallet export files to Koinly-compatible CSV format. Subclasses must implement
    the convert() method to handle specific wallet formats.

    Attributes:
        source_file (str): Path to the source wallet export file
        output_dir (str): Directory where converted files will be saved
        export_keys (Set[str]): Set of column names to include in output
        final_csv (List[Dict[str, Any]]): List of transaction dictionaries
    """

    def __init__(self, source_file: str, output_dir: str) -> None:
        """Initialize the wallet converter.

        Args:
            source_file: Path to the source wallet export file
            output_dir: Directory where converted files will be saved
        """
        self.source_file: str = source_file
        self.output_dir: str = output_dir
        self.export_keys: Set[str] = set()
        self.final_csv: List[Dict[str, Any]] = []

    def sats_to_btc(self, sats: int) -> float:
        """Convert satoshis to BTC.

        Args:
            sats: Amount in satoshis (1 BTC = 100,000,000 satoshis)

        Returns:
            float: Amount in BTC
        """
        return sats / 100_000_000

    def format_btc(self, btc_amount: float) -> str:
        """Format BTC amount to 8 decimal places.

        Args:
            btc_amount: Amount in BTC

        Returns:
            str: Formatted BTC amount with 8 decimal places
        """
        return "{:.8f}".format(btc_amount)

    def generate_timestamp(self) -> str:
        """Generate current UTC timestamp for filename.

        Returns:
            str: Timestamp in format YYYY-MM-DD_HH-MM-SS
        """
        return datetime.now(pytz.utc).strftime("%Y-%m-%d_%H-%M-%S")

    def validate_source_file(self) -> None:
        """Validate that source file exists and is a CSV.

        Raises:
            FileNotFoundError: If source file doesn't exist
            ValueError: If source path is not a file or not a CSV
        """
        if not os.path.exists(self.source_file):
            raise FileNotFoundError(f"Source file not found: {self.source_file}")
        if not os.path.isfile(self.source_file):
            raise ValueError(f"Source path is not a file: {self.source_file}")
        if not self.source_file.lower().endswith(".csv"):
            raise ValueError(f"Source file must be a CSV file: {self.source_file}")

    def ensure_output_dir(self) -> None:
        """Ensure output directory exists, creating it if necessary.

        Raises:
            RuntimeError: If directory cannot be created
        """
        try:
            os.makedirs(self.output_dir, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"Cannot create output directory: {e}")

    def write_csv(self, filename_prefix: str) -> str:
        """Write the final CSV file with consistent formatting.

        Args:
            filename_prefix: Prefix for the output filename (e.g., 'zeus_wallet')

        Returns:
            str: Path to the generated output file

        Raises:
            ValueError: If no transactions to export
            PermissionError: If cannot write to output file
            RuntimeError: If other error occurs during write
        """
        if not self.final_csv:
            raise ValueError("No transactions found to export")

        self.ensure_output_dir()

        # Generate output filename
        timestamp = self.generate_timestamp()
        output_file = os.path.join(
            self.output_dir, f"{filename_prefix}_{timestamp}.csv"
        )

        try:
            with open(output_file, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=self.export_keys)
                writer.writeheader()
                for row in self.final_csv:
                    writer.writerow(row)

            logger.debug(
                f"Successfully wrote {len(self.final_csv)} transactions to {output_file}"
            )
            return output_file

        except PermissionError:
            raise PermissionError(
                f"Cannot write to output file: {output_file}. Check file permissions."
            )
        except Exception as e:
            raise RuntimeError(f"Error writing output file: {e}")

    @abstractmethod
    def convert(self) -> str:
        """Convert wallet transactions to Koinly format.

        This method must be implemented by subclasses to handle specific
        wallet export formats.

        Returns:
            str: Path to the generated output file

        Raises:
            Various exceptions depending on implementation
        """
        pass
