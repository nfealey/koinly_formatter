# Koinly Formatter

A GUI application that converts transaction files from cryptocurrency wallets into CSV format compatible with Koinly tax software.

## Overview

This project allows users to easily convert transaction files from Sparrow Wallet or Zeus to a CSV format that can be imported into Koinly for tax reporting purposes. The application provides a simple graphical interface for selecting and converting wallet transaction files.

## Supported Wallets

- **Sparrow Wallet** - Bitcoin wallet (converts from Sparrow CSV export)
- **Zeus** - Lightning Network wallet (requires invoices.csv, payments.csv, and onchain.csv files)

Additional wallet support is planned for future releases.

## Features

- User-friendly GUI for easy file selection and conversion
- Converts wallet-specific transaction formats to Koinly-compatible CSV
- Batch processing capabilities for multiple transaction files
- Automatic BTC/satoshi conversion
- Lightning Network transaction support (Zeus)
- Transaction labeling and categorization

## Requirements

- Python 3.x
- pandas
- pytz
- tkinter (usually comes with Python)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/koinly_formatter.git
   cd koinly_formatter
   ```

2. Create a virtual environment (recommended):
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   Or install dependencies manually:
   ```bash
   pip install pandas pytz
   ```

## Usage

1. Run the GUI application:
   ```bash
   python main.py
   ```

2. In the GUI:
   - Select your wallet type from the dropdown menu
   - Click "Browse" to select your wallet export file(s)
   - Choose an output directory for the converted Koinly CSV file
   - Click "Convert" to process the files

### Wallet-Specific Instructions

**Sparrow Wallet:**
- Export your transaction history from Sparrow as CSV
- Select the exported CSV file in the converter

**Zeus Wallet:**
- Export the following three CSV files from Zeus:
  - invoices.csv
  - payments.csv
  - onchain.csv
- Select all three files when prompted

## Output Format

The converter generates a Koinly-compatible CSV file with the following columns:
- Date (UTC timezone)
- Sent Amount
- Sent Currency
- Received Amount
- Received Currency
- Fee Amount
- Fee Currency
- Net Worth Amount
- Net Worth Currency
- Label
- Description
- TxHash

## Contributing

Contributions to add support for additional wallets are welcome! To add a new wallet:

1. Create a new converter file in the `supported_wallets` directory
2. Implement a class with a `convert()` method that accepts input file path(s) and output directory
3. The converter should output a Koinly-compatible CSV file
4. Submit a pull request with your changes

## License

This project is licensed under the MIT License - see the LICENSE file for details.