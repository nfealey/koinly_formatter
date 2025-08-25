# Koinly Formatter Refactoring Guide

This document outlines the refactoring opportunities identified in the codebase and provides a roadmap for improvements.

## Critical Issues (Priority 1)

### 1. Zeus Converter Duplicate Code
**File**: `supported_wallets/zues_koinly.py`
- **Issue**: The entire `ZuessToKoinly` class is duplicated within the same file (lines 148-285 duplicate lines 4-141)
- **Impact**: Causes confusion, increases file size, potential for conflicting changes
- **Solution**: Remove the duplicate class definition

### 2. Naming Convention Error
**Files**: `zues_koinly.py`, `main.py`
- **Issue**: "Zeus" is misspelled as "Zues" throughout the codebase
- **Impact**: Confusing for users and developers, unprofessional
- **Solution**: 
  - Rename `zues_koinly.py` to `zeus_koinly.py`
  - Rename class `ZuessToKoinly` to `ZeusToKoinly`
  - Update references in `main.py`

### 3. Zeus Converter GUI Incompatibility
**File**: `supported_wallets/zues_koinly.py`
- **Issue**: Uses `input()` function which doesn't work with GUI
- **Impact**: Application crashes when Zeus converter is selected without all required files
- **Solution**: Accept file paths as parameters instead of prompting for input

## Code Quality Issues (Priority 2)

### 4. Missing Error Handling
**All files**
- **Issues**:
  - No try-except blocks around file operations
  - No validation of input files
  - No user feedback on errors
  - `quit()` used instead of proper exception handling
- **Solution**: Implement comprehensive error handling with user-friendly messages

### 5. Code Duplication Between Converters
**Files**: `sparrow_to_koinly.py`, `zues_koinly.py`
- **Duplicated functionality**:
  - Satoshi to BTC conversion
  - BTC formatting (8 decimal places)
  - Timestamp generation
  - CSV output logic
- **Solution**: Create a base converter class with shared functionality

### 6. Import Organization Issues
**All files**
- **Issues**:
  - Duplicate imports (`pandas` imported twice in some files)
  - Imports scattered throughout code
  - `import os` repeated multiple times within functions
- **Solution**: Move all imports to the top of files, remove duplicates

## Design Improvements (Priority 3)

### 7. Create Base Converter Class
**New file**: `supported_wallets/base_converter.py`
```python
from abc import ABC, abstractmethod
from typing import Optional, Dict, List
import pandas as pd
from datetime import datetime
import pytz
import os

class BaseWalletConverter(ABC):
    """Base class for all wallet converters."""
    
    SATS_PER_BTC = 100_000_000
    DEFAULT_CURRENCY = "BTC"
    
    def __init__(self, source_file: str, output_dir: str):
        self.source_file = source_file
        self.output_dir = output_dir
        self.validate_inputs()
    
    def validate_inputs(self):
        """Validate input file exists and output directory is writable."""
        if not os.path.exists(self.source_file):
            raise FileNotFoundError(f"Source file not found: {self.source_file}")
        if not os.path.exists(self.output_dir):
            raise FileNotFoundError(f"Output directory not found: {self.output_dir}")
        if not os.access(self.output_dir, os.W_OK):
            raise PermissionError(f"Cannot write to output directory: {self.output_dir}")
    
    @abstractmethod
    def convert(self) -> str:
        """Convert wallet data to Koinly format. Returns output file path."""
        pass
    
    def sats_to_btc(self, sats: int) -> float:
        """Convert satoshis to BTC."""
        return sats / self.SATS_PER_BTC
    
    def format_btc(self, btc: float) -> str:
        """Format BTC value to 8 decimal places."""
        return f"{btc:.8f}"
    
    def get_output_filename(self, prefix: str) -> str:
        """Generate timestamped output filename."""
        timestamp = datetime.now(pytz.utc).strftime("%Y-%m-%d_%H-%M-%S")
        return os.path.join(self.output_dir, f"{prefix}_{timestamp}.csv")
    
    def create_koinly_dataframe(self) -> pd.DataFrame:
        """Create empty Koinly-formatted DataFrame with standard columns."""
        return pd.DataFrame(columns=[
            'Date', 'Sent Amount', 'Sent Currency', 'Received Amount', 
            'Received Currency', 'Fee Amount', 'Fee Currency', 
            'Net Worth Amount', 'Net Worth Currency', 'Label', 
            'Description', 'TxHash'
        ])
```

### 8. Add Type Hints
**All Python files**
- **Current**: No type hints used
- **Solution**: Add comprehensive type hints to all functions and methods
- **Example**:
```python
def convert(self) -> None:  # Current
def convert(self) -> str:   # Improved - returns output file path
```

### 9. Improve GUI Error Handling and Feedback
**File**: `main.py`
- **Add**:
  - Try-except blocks in convert method
  - Progress indicator during conversion
  - Error dialogs for failures
  - Input validation before conversion
  - Status bar for feedback

### 10. Configuration Support
**New feature**
- **Add support for**:
  - Different cryptocurrencies (not just BTC)
  - Custom date formats
  - Decimal precision settings
  - Export format options

## File Structure Improvements

### 11. Missing Package Initialization
**Directory**: `supported_wallets/`
- **Issue**: No `__init__.py` file
- **Solution**: Create `__init__.py` to make it a proper Python package

### 12. Create Requirements File
**New file**: `requirements.txt`
```
pandas>=1.3.0
pytz>=2021.1
```

### 13. Remove Unnecessary Code
**Files**: Various
- Remove commented virtual environment setup instructions
- Remove donation messages from library code
- Remove duplicate import statements
- Remove unused variables

## Refactoring Priority Order

### Phase 1: Critical Fixes (Immediate)
1. Fix Zeus class duplication
2. Fix "zues" → "zeus" naming
3. Fix Zeus input() GUI incompatibility
4. Create `__init__.py` in supported_wallets

### Phase 2: Core Improvements (Short-term)
1. Create base converter class
2. Refactor existing converters to use base class
3. Add comprehensive error handling
4. Create requirements.txt

### Phase 3: Enhancement (Medium-term)
1. Add type hints throughout
2. Improve GUI with progress feedback
3. Add configuration support
4. Implement logging instead of print statements

## Testing Recommendations

After refactoring:
1. Test both converters with sample data
2. Test error cases (missing files, invalid data)
3. Verify GUI handles all error scenarios gracefully
4. Ensure output format remains Koinly-compatible

## Code Style Guidelines

For consistency across refactoring:
1. Use PEP 8 style guide
2. Add docstrings to all classes and methods
3. Use meaningful variable names
4. Keep functions focused on single responsibilities
5. Prefer composition over inheritance where appropriate

## Example Refactored Converter

```python
from typing import Optional
import pandas as pd
from .base_converter import BaseWalletConverter

class SparrowToKoinly(BaseWalletConverter):
    """Converter for Sparrow Wallet CSV exports to Koinly format."""
    
    def convert(self) -> str:
        """Convert Sparrow wallet export to Koinly format.
        
        Returns:
            str: Path to the output CSV file
            
        Raises:
            ValueError: If required columns are missing
            pd.errors.EmptyDataError: If input file is empty
        """
        try:
            # Read source file
            df = pd.read_csv(self.source_file)
            
            # Validate required columns
            required_columns = ['Date (UTC)', 'Balance (BTC)', 'Label', 'Transaction']
            missing_columns = set(required_columns) - set(df.columns)
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Create Koinly formatted DataFrame
            df_koinly = self.create_koinly_dataframe()
            
            # Convert data
            df_koinly['Date'] = pd.to_datetime(df['Date (UTC)']).dt.strftime('%Y-%m-%d %H:%M UTC')
            df_koinly['Received Amount'] = df['Balance (BTC)'].apply(lambda x: self.format_btc(abs(x)))
            df_koinly['Received Currency'] = self.DEFAULT_CURRENCY
            df_koinly['Label'] = df['Label']
            df_koinly['TxHash'] = df['Transaction']
            
            # Save output
            output_file = self.get_output_filename('sparrow_wallet')
            df_koinly.to_csv(output_file, index=False)
            
            return output_file
            
        except Exception as e:
            raise Exception(f"Error converting Sparrow wallet data: {str(e)}")
```

## Benefits of Refactoring

1. **Maintainability**: Easier to add new wallet types
2. **Reliability**: Proper error handling prevents crashes
3. **User Experience**: Better feedback and error messages
4. **Code Quality**: Type hints and documentation improve developer experience
5. **Extensibility**: Base class makes adding features easier
6. **Performance**: Removing duplicate code and imports
7. **Professionalism**: Correct naming and structure