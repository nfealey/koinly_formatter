# Koinly Formatter Refactoring Guide

This document outlines the remaining refactoring opportunities in the codebase.

## Remaining Tasks

### 1. Configuration Support
**New feature**
- **Add support for**:
  - Different cryptocurrencies (not just BTC)
  - Custom date formats
  - Decimal precision settings
  - Export format options

### 2. Create Requirements File
**New file**: `requirements.txt`
```
pandas>=1.3.0
pytz>=2021.1
```

### 3. Enhanced Base Converter Class
**Enhancement to**: `supported_wallets/wallet_utils.py`
- Add constants like `SATS_PER_BTC = 100_000_000` and `DEFAULT_CURRENCY = "BTC"`
- Add `create_koinly_dataframe()` method with standard Koinly columns
- Consider additional shared functionality between converters

### 4. Implement Logging
**All files**
- Replace print statements with proper logging
- Add configurable log levels
- Log file operations and conversions for debugging

### 5. Add Comprehensive Documentation
**All files**
- Add docstrings to all classes and methods
- Create user documentation
- Add inline comments for complex logic

### 6. Unit Tests
**New directory**: `tests/`
- Create unit tests for converters
- Test edge cases and error conditions
- Test GUI components
- Ensure output format compatibility

### 7. Additional Wallet Support
**Potential additions**:
- Electrum wallet
- Bitcoin Core wallet
- Other Lightning wallets
- Hardware wallet exports

### 8. Export Format Options
**Enhancement**:
- Support multiple output formats (not just Koinly)
- Add templates for different tax software
- Allow custom CSV column mapping

### 9. Batch Processing
**New feature**:
- Process multiple files at once
- Support directory scanning for wallet files
- Progress tracking for batch operations

### 10. Settings Persistence
**New feature**:
- Save user preferences (default directories, formats)
- Remember last used settings
- Configuration file support

## Code Style Guidelines

For consistency across future development:
1. Use PEP 8 style guide
2. Add docstrings to all classes and methods
3. Use meaningful variable names
4. Keep functions focused on single responsibilities
5. Prefer composition over inheritance where appropriate

## Testing Recommendations

When implementing new features:
1. Test with sample data from each wallet type
2. Test error cases (missing files, invalid data)
3. Verify GUI handles all scenarios gracefully
4. Ensure output format remains compatible with target software

## Benefits of Continuing Refactoring

1. **Maintainability**: Easier to add new wallet types
2. **Reliability**: Better testing prevents regressions
3. **User Experience**: More features and better performance
4. **Code Quality**: Documentation improves developer experience
5. **Extensibility**: Modular design makes adding features easier
6. **Community**: Well-documented code encourages contributions