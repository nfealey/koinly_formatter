"""Zeus wallet single-file format to Koinly converter.

This module handles the conversion of the new Zeus wallet export format
(single CSV file) to Koinly-compatible CSV format.
"""

import os
import csv
import logging
from typing import Optional
from .wallet_utils import BaseWalletConverter

logger = logging.getLogger(__name__)


class ZeusSingleFileToKoinly(BaseWalletConverter):
    """Converter for new Zeus wallet single-file exports to Koinly format.

    Zeus wallet now exports all Lightning payments in a single CSV file
    instead of the previous three-file format (invoices, payments, onchain).
    This converter handles the new format.
    """

    def __init__(self, source_file: str, output_dir: str) -> None:
        """Initialize Zeus single-file wallet converter.

        Args:
            source_file: Path to Zeus wallet export CSV file
            output_dir: Directory where converted file will be saved
        """
        super().__init__(source_file, output_dir)

    def convert(self) -> str:
        """Convert Zeus wallet single-file export to Koinly format.

        The new Zeus format combines all Lightning payments in one file.
        We determine if a payment was sent or received based on the presence
        of a Destination field (sent) or Payment Request field (received).

        Returns:
            str: Path to the generated output file

        Raises:
            FileNotFoundError: If source file not found
            ValueError: If CSV has invalid format or missing columns
            RuntimeError: If processing fails
        """
        try:
            # Validate input file exists and is a CSV
            self.validate_source_file()

            # Initialize export keys
            self.export_keys = {
                'Date', 'Received Amount', 'Sent Amount', 
                'Received Currency', 'Sent Currency', 
                'TxHash', 'Description'
            }

            # Process the CSV file
            try:
                with open(self.source_file, mode='r', encoding='utf-8') as file:
                    csv_reader = csv.DictReader(file)
                    
                    # Validate required columns
                    if not csv_reader.fieldnames:
                        raise ValueError("CSV file has no headers")
                    
                    required_fields = {'Amount Paid (sat)', 'Payment Hash', 'Creation Date'}
                    missing_fields = required_fields - set(csv_reader.fieldnames)
                    if missing_fields:
                        raise ValueError(
                            f"Missing required fields: {', '.join(missing_fields)}"
                        )
                    
                    # Process each row
                    for row_num, row in enumerate(csv_reader, start=2):
                        new_line = {}
                        
                        # Get amount and payment hash
                        try:
                            amount_sats = int(row['Amount Paid (sat)'])
                            amount_btc = self.sats_to_btc(amount_sats)
                            formatted_amount = self.format_btc(amount_btc)
                        except (ValueError, KeyError) as e:
                            raise ValueError(
                                f"Invalid amount in row {row_num}: "
                                f"{row.get('Amount Paid (sat)', 'missing')}"
                            )
                        
                        # Determine if sent or received based on Destination field
                        # If there's a destination, it's a sent payment
                        # Otherwise, it's a received payment (invoice)
                        destination = row.get('Destination', '').strip()
                        
                        if destination:
                            # Sent payment
                            new_line['Sent Amount'] = formatted_amount
                            new_line['Sent Currency'] = 'BTC'
                        else:
                            # Received payment
                            new_line['Received Amount'] = formatted_amount
                            new_line['Received Currency'] = 'BTC'
                        
                        # Add common fields
                        new_line['Date'] = row['Creation Date']
                        new_line['TxHash'] = row['Payment Hash']
                        
                        # Build description from memo and note
                        description_parts = []
                        if row.get('Memo', '').strip():
                            description_parts.append(f"Memo: {row['Memo']}")
                        if row.get('Note', '').strip():
                            description_parts.append(f"Note: {row['Note']}")
                        if destination:
                            description_parts.append(f"To: {destination[:20]}...")
                        
                        new_line['Description'] = ' | '.join(description_parts)
                        
                        self.final_csv.append(new_line)
                
            except FileNotFoundError:
                raise FileNotFoundError(f"Cannot read source file: {self.source_file}")
            except csv.Error as e:
                raise ValueError(f"Invalid CSV format: {e}")
            except Exception as e:
                raise RuntimeError(f"Error processing file: {e}")
            
            # Use base class method to write CSV
            return self.write_csv("zeus_wallet_single")
            
        except Exception as e:
            # Re-raise exception with context
            raise RuntimeError(f"Zeus wallet conversion failed: {str(e)}")