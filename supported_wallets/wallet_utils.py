import os
import csv
from datetime import datetime
import pytz
from abc import ABC, abstractmethod
from typing import List, Set, Dict, Any


class BaseWalletConverter(ABC):
    """Base class for wallet converters with shared functionality."""
    
    def __init__(self, source_file: str, output_dir: str) -> None:
        self.source_file: str = source_file
        self.output_dir: str = output_dir
        self.export_keys: Set[str] = set()
        self.final_csv: List[Dict[str, Any]] = []
    
    def sats_to_btc(self, sats: int) -> float:
        """Convert satoshis to BTC."""
        return sats / 100_000_000
    
    def format_btc(self, btc_amount: float) -> str:
        """Format BTC amount to 8 decimal places."""
        return '{:.8f}'.format(btc_amount)
    
    def generate_timestamp(self) -> str:
        """Generate current timestamp for filename."""
        return datetime.now(pytz.utc).strftime("%Y-%m-%d_%H-%M-%S")
    
    def validate_source_file(self) -> None:
        """Validate that source file exists and is a CSV."""
        if not os.path.exists(self.source_file):
            raise FileNotFoundError(f"Source file not found: {self.source_file}")
        if not os.path.isfile(self.source_file):
            raise ValueError(f"Source path is not a file: {self.source_file}")
        if not self.source_file.lower().endswith('.csv'):
            raise ValueError(f"Source file must be a CSV file: {self.source_file}")
    
    def ensure_output_dir(self) -> None:
        """Ensure output directory exists."""
        try:
            os.makedirs(self.output_dir, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"Cannot create output directory: {e}")
    
    def write_csv(self, filename_prefix: str) -> str:
        """Write the final CSV file with consistent formatting."""
        if not self.final_csv:
            raise ValueError("No transactions found to export")
        
        self.ensure_output_dir()
        
        # Generate output filename
        timestamp = self.generate_timestamp()
        output_file = os.path.join(self.output_dir, f"{filename_prefix}_{timestamp}.csv")
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=self.export_keys)
                writer.writeheader()
                for row in self.final_csv:
                    writer.writerow(row)
            
            print(f"Conversion successful! Output saved to: {output_file}")
            print(f"Total transactions processed: {len(self.final_csv)}")
            return output_file
            
        except PermissionError:
            raise PermissionError(f"Cannot write to output file: {output_file}. Check file permissions.")
        except Exception as e:
            raise RuntimeError(f"Error writing output file: {e}")
    
    @abstractmethod
    def convert(self) -> str:
        """Convert wallet data to Koinly format. Must be implemented by subclasses.
        
        Returns:
            str: Path to the generated output file
        """
        pass