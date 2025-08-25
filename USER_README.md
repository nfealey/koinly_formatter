# Koinly Formatter User Guide

## Overview

Koinly Formatter is a desktop application that converts cryptocurrency wallet export files into Koinly-compatible CSV format for tax reporting. It supports multiple wallet formats and provides an easy-to-use graphical interface.

## Supported Wallets

### 1. Sparrow Wallet
- **Required**: Single CSV export file from Sparrow wallet
- **Format**: Standard Sparrow transaction export
- **Contains**: Date, Value (in satoshis), Label, Transaction ID

### 2. Zeus Wallet
- **Required**: Three separate CSV files:
  - `invoices.csv` - Lightning invoices (incoming payments)
  - `payments.csv` - Lightning payments (outgoing payments)
  - `onchain.csv` - On-chain Bitcoin transactions

## Installation

### Prerequisites
- Python 3.6 or higher
- Required Python packages (install with `pip install -r requirements.txt`):
  - pandas
  - pytz
  - tkinter (usually included with Python)

### Running the Application
```bash
python main.py
```

## How to Use

### Converting Sparrow Wallet Files

1. Launch the application
2. Click "Browse" next to "Source File" and select your Sparrow wallet CSV export
3. Verify the output directory (defaults to Downloads folder)
4. Click "Convert"
5. The converted file will be saved with a timestamp in the output directory

### Converting Zeus Wallet Files

1. Launch the application
2. Select "Zeus Wallet" from the "Wallet Format" dropdown
3. The source file input will be disabled (Zeus requires multiple files)
4. Verify the output directory (defaults to Downloads folder)
5. Click "Convert"
6. You'll be prompted to select three files in order:
   - First: Select `invoices.csv`
   - Second: Select `payments.csv`
   - Third: Select `onchain.csv`
7. The converter will combine all three files into a single Koinly-compatible CSV

## Output Format

The generated CSV files include the following columns (as applicable):
- **Koinly Date**: Transaction date in Koinly's expected format (YYYY-MM-DD HH:MM UTC)
- **Amount/Received Amount/Sent Amount**: Transaction amount in BTC
- **Currency/Received Currency/Sent Currency**: Cryptocurrency type (BTC)
- **Label**: Transaction label or memo
- **TxHash**: Transaction or payment hash
- **Description**: Combined notes from various fields
- **Fee Amount**: Transaction fees (if applicable)

## Features

### Visual Validation
- ✓ Green checkmark indicates valid file/directory selection
- ✗ Red X indicates invalid selection
- Real-time validation as you type or browse

### Progress Indication
- Progress bar shows activity during conversion
- Status bar displays current operation and results

### Error Handling
- User-friendly error messages for common issues:
  - Missing files
  - Invalid file formats
  - Permission errors
  - Processing errors

## Troubleshooting

### Common Issues

1. **"File not found" error**
   - Ensure the CSV file exists at the selected location
   - Check file permissions

2. **"Invalid CSV format" error**
   - Verify the file is a valid CSV export from your wallet
   - Ensure the file isn't corrupted or incomplete

3. **"Missing required columns" error**
   - The CSV file doesn't contain expected columns
   - Make sure you're using the correct wallet format selection

4. **Zeus wallet conversion fails**
   - Ensure you select all three required files
   - Files must be named appropriately or contain the expected data

### File Format Requirements

#### Sparrow Wallet CSV
Must contain these columns:
- `Date (UTC)` - Transaction date
- `Value` - Amount in satoshis
- `Label` - Transaction label
- `Txid` - Transaction ID

#### Zeus Wallet CSVs
- **invoices.csv**: Must contain `Amount Paid (sat)`, `Payment Hash`, `Timestamp`
- **payments.csv**: Must contain `Amount Paid (sat)`, `Payment Hash`, `Creation Date`
- **onchain.csv**: Must contain `Amount (sat)`, `Transaction Hash`, `Timestamp`

## Tips

1. **Organize Your Files**: Keep wallet export files in a dedicated folder
2. **Check Output**: Always verify the converted file before importing to Koinly
3. **Backup Originals**: Keep your original wallet export files as backup
4. **Use Descriptive Labels**: Transaction labels in your wallet will be preserved

## Privacy & Security

- All processing is done locally on your computer
- No data is sent to external servers
- Original files are never modified
- Output files contain only transaction data (no private keys or sensitive wallet information)

## Getting Help

If you encounter issues:
1. Check the error message for specific details
2. Verify your CSV files match the expected format
3. Ensure you have write permissions to the output directory
4. Check the console output for additional debug information

## Contributing

To add support for additional wallets:
1. Create a new converter class inheriting from `BaseWalletConverter`
2. Implement the `convert()` method
3. Add the wallet to the GUI's `wallet_types` dictionary
4. Test with sample data

For more technical details, see the code documentation and `refactoring.md`.