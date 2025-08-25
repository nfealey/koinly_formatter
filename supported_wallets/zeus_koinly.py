"""Zeus wallet to Koinly format converter.

This module handles the conversion of Zeus wallet export files (invoices.csv,
payments.csv, and onchain.csv) to Koinly-compatible CSV format.
"""

import os
import csv
import logging
from typing import Optional
from .wallet_utils import BaseWalletConverter

logger = logging.getLogger(__name__)


class ZeusToKoinly(BaseWalletConverter):
    """Converter for Zeus wallet exports to Koinly format.
    
    Zeus wallet exports transactions in three separate CSV files:
    - invoices.csv: Lightning invoices (incoming payments)
    - payments.csv: Lightning payments (outgoing payments)  
    - onchain.csv: On-chain Bitcoin transactions
    
    This converter combines all three files into a single Koinly-compatible CSV.
    """
    def __init__(self, source_file: str, output_dir: str, 
                 invoices_path: Optional[str] = None, 
                 payments_path: Optional[str] = None, 
                 onchain_path: Optional[str] = None) -> None:
        """Initialize Zeus wallet converter.
        
        Args:
            source_file: Not used for Zeus (kept for compatibility)
            output_dir: Directory where converted file will be saved
            invoices_path: Path to invoices.csv file
            payments_path: Path to payments.csv file  
            onchain_path: Path to onchain.csv file
        """
        super().__init__(source_file, output_dir)
        self.invoices_path: Optional[str] = invoices_path
        self.payments_path: Optional[str] = payments_path
        self.onchain_path: Optional[str] = onchain_path


    def convert(self) -> str:
        """Convert Zeus wallet exports to Koinly format.
        
        Processes three CSV files (invoices, payments, onchain) and combines
        them into a single Koinly-compatible CSV file.
        
        Returns:
            str: Path to the generated output file
            
        Raises:
            FileNotFoundError: If required CSV files are not found
            ValueError: If CSV files have invalid format or data
            RuntimeError: If processing fails
        """
        # Use provided paths or check for default files in current directory
        try:
            if self.invoices_path is None:
                if os.path.exists('invoices.csv'):
                    invoices_path = os.path.join(os.getcwd(), 'invoices.csv')
                else:
                    raise FileNotFoundError("invoices.csv not found and no path provided")
            else:
                invoices_path = self.invoices_path
                
            if self.payments_path is None:
                if os.path.exists('payments.csv'):
                    payments_path = os.path.join(os.getcwd(), 'payments.csv')
                else:
                    raise FileNotFoundError("payments.csv not found and no path provided")
            else:
                payments_path = self.payments_path
                
            if self.onchain_path is None:
                if os.path.exists('onchain.csv'):
                    onchain_path = os.path.join(os.getcwd(), 'onchain.csv')
                else:
                    raise FileNotFoundError("onchain.csv not found and no path provided")
            else:
                onchain_path = self.onchain_path
                
            known_paths={
                'INVOICES':invoices_path,
                'PAYMENTS':payments_path,
                'ONCHAIN':onchain_path
            }
            
            # verify all given files exist
            for file_type, file_path in known_paths.items():
                if file_path == "":
                    continue
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"{file_type} file not found at path: {file_path}")
                if not os.path.isfile(file_path):
                    raise ValueError(f"{file_type} path is not a file: {file_path}")
                if not file_path.lower().endswith('.csv'):
                    raise ValueError(f"{file_type} file must be a CSV file: {file_path}")
        
            # Mapping of Zeus field names to Koinly field names
            convert_keys={
                'Amount Paid (sat)':'Received Amount',
                'Payment Hash':'TxHash',
                'Transaction Hash':'TxHash',
                'Creation Date':'Date',
                'Timestamp':'Date',
            }
            # Fields to ignore from Zeus exports (not needed for Koinly)
            ignore_keys={'Expiry','Payment Request'}
            # Initialize export keys - more will be added dynamically
            self.export_keys={'Description','Received Currency','Sent Currency'}
            # Fields that should be combined into the Description field
            notes_keys={'Memo','Note','Destination'}

            # Process each CSV file
            for csv_type, known_path in known_paths.items():
                try:
                    with open(known_path, mode='r', encoding='utf-8') as file:
                        csvFile = csv.DictReader(file)
                        # read in CSV file line by line
                        for row_num, line in enumerate(csvFile, start=2):  # start=2 because row 1 is headers
                            notes_field='' # start with a blank notes field
                            new_line={} # we put output data into here
                            for key,value in line.items():
                                write_value=value
                                write_key=key
                                if key in ignore_keys:
                                    continue
                                elif key in notes_keys:
                                    # special handling for "notes" fields
                                    if value.strip()!='':
                                        notes_add='{}:{} + '.format(key,value)
                                        notes_field=notes_field+notes_add
                                    continue
                                elif key in {'Amount Paid (sat)'} and csv_type=='INVOICES':
                                    # Convert satoshis to BTC for received invoices
                                    try:
                                        converted=self.sats_to_btc(int(value))
                                        write_value=self.format_btc(converted)
                                        write_key='Received Amount'
                                        new_line['Received Currency']='BTC'
                                    except ValueError:
                                        raise ValueError(f"Invalid amount value in {csv_type} row {row_num}: '{value}'")
                                elif key in {'Amount Paid (sat)'} and csv_type=='PAYMENTS':
                                    # Convert satoshis to BTC for sent payments
                                    try:
                                        converted=self.sats_to_btc(int(value))
                                        write_value=self.format_btc(converted)
                                        write_key='Sent Amount'
                                        new_line['Sent Currency']='BTC'
                                    except ValueError:
                                        raise ValueError(f"Invalid amount value in {csv_type} row {row_num}: '{value}'")
                                elif key=='Amount (sat)':
                                    # On-chain transactions: positive = received, negative = sent
                                    try:
                                        numbered=int(value)
                                        if numbered>0:
                                            write_key='Received Amount'
                                            new_line['Received Currency']='BTC'
                                        elif numbered<0:
                                            write_key='Sent Amount'
                                            new_line['Sent Currency']='BTC'
                                        elif numbered==0:
                                            continue
                                        converted=abs(self.sats_to_btc(numbered))
                                        write_value=self.format_btc(converted)
                                    except ValueError:
                                        raise ValueError(f"Invalid amount value in {csv_type} row {row_num}: '{value}'")
                                elif key=='Total Fees (sat)':
                                    # Convert fee amount from satoshis to BTC
                                    try:
                                        numbered=int(value)
                                        if numbered>0:  # Only record fees for outgoing transactions
                                            converted=abs(self.sats_to_btc(numbered))
                                            write_value=self.format_btc(converted)
                                            write_key='Fee Amount'
                                    except ValueError:
                                        raise ValueError(f"Invalid fee value in {csv_type} row {row_num}: '{value}'")
                                elif key not in convert_keys:
                                    # Log warning but continue processing
                                    logger.debug(f"Unknown field '{key}' in {csv_type} - skipping")
                                    continue
                                else:
                                    write_key=convert_keys[key]
                                if write_key not in self.export_keys:
                                    self.export_keys.add(write_key)
                                new_line[write_key]=write_value 
                            new_line['Description']=notes_field
                            self.final_csv.append(new_line)
                        
                except FileNotFoundError as e:
                    raise FileNotFoundError(f"Cannot read {csv_type} file: {e}")
                except csv.Error as e:
                    raise ValueError(f"Invalid CSV format in {csv_type} file at line {row_num}: {e}")
                except Exception as e:
                    raise RuntimeError(f"Error processing {csv_type} file: {e}")
            # Use the base class method to write the CSV
            return self.write_csv("zeus_wallet")
                
        except Exception as e:
            # Re-raise exception with context
            raise RuntimeError(f"Zeus wallet conversion failed: {str(e)}")
