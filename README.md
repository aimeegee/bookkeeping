# Bank Transaction Merger and Categorizer

A Python tool to merge bank transaction files from different banks and automatically categorize expenses.

## Features

- 📊 Merge transaction files from multiple banks (CSV/Excel/Google Sheets)
- 🏦 Support for CBA, ANZ, Westpac, NAB with configurable formats
- 🔄 Automatic amount sign normalization (positive for expenses, negative for income)
- 🏷️ Intelligent transaction categorization with learning capability
- 💬 Interactive CLI for manual categorization
- 🔍 Fuzzy matching for similar descriptions
- 💾 Persistent category mapping storage
- 🌐 Google Sheets integration via shareable URLs

## Project Structure

```
bookkeeping/
├── config/
│   ├── bank_config.json          # Bank configuration (date formats, amount signs)
│   └── category_mapping.json     # Description -> Category mapping storage
├── data/
│   ├── input/                     # Original bank transaction files
│   └── output/                    # Processed merged files
├── src/
│   ├── data_processor.py          # Core data processing logic
│   ├── bank_parser.py            # Bank-specific data parsers
│   ├── category_manager.py       # Category management and mapping
│   └── interactive_cli.py        # Interactive command line interface
├── main.py                        # Main program entry point
├── requirements.txt
└── README.md
```

## Setup

1. **Install dependencies:**

   ```bash
   cd bookkeeping
   pip install -r requirements.txt
   ```

2. **Prepare your transaction files:**

   - Place bank transaction files in `data/input/`
   - Supported formats: CSV, XLSX, and Google Sheets (via URL)
   - Use naming format: `<month><bank-name>.csv/xlsx` or `YYYY-MM-bankname.csv/xlsx`
   - Examples: `08amex.csv`, `08cba.xlsx`, `2024-08-westpac.csv`

3. **Configure banks in `config/bank_config.json`:**
   ```json
   {
     "cba": {
       "name": "Commonwealth Bank",
       "revert_amount": false,
       "date_format": "%d/%m/%Y"
     }
   }
   ```

## Usage

### Basic Usage

```bash
python main.py
```

### Command Line Options

```bash
python main.py --input-dir data/input --output-dir data/output
python main.py --no-interactive  # Skip interactive categorization
```

### Google Sheets Integration

For Google Sheets integration, you can modify the `main.py` to include Google Sheets URLs:

```python
# Example: Adding Google Sheets support
google_sheets = [
    {
        "url": "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit#gid=0",
        "filename": "08visa.csv"  # Used for bank identification
    }
]

# Pass to merge_files method
merged_df = processor.merge_files(args.input_dir, google_sheets_urls=google_sheets)
```

The Google Sheets URL will be automatically converted to CSV export format for processing.

### File Format Requirements

Your CSV/Excel files should contain these columns (case-insensitive):

- `date` - Transaction date
- `description` - Transaction description
- `amount` - Transaction amount

Example CSV:

```csv
Date,Description,Amount
01/08/2024,WOOLWORTHS 1234,45.67
02/08/2024,Coffee Shop,-4.50
03/08/2024,Salary,-3000.00
```

## Bank Configuration

Configure each bank in `config/bank_config.json`:

- `name`: Display name for the bank
- `revert_amount`: Set to `true` if the bank uses opposite signs (e.g., positive for income)
- `date_format`: Python strftime format for dates

## Category Management

The system automatically learns transaction categories:

1. **First run**: Manually categorize unknown descriptions
2. **Subsequent runs**: Automatic categorization based on learned patterns
3. **Fuzzy matching**: Similar descriptions get suggested categories

Categories are stored in `config/category_mapping.json` and persist between runs.

## Example Workflow

1. Export transaction files from your banks
2. Rename files following the `YYYY-MM-bankname.csv` format
3. Place files in `data/input/`
4. Run `python main.py`
5. Categorize any new transaction descriptions when prompted
6. Review the monthly output files in `data/output/` (e.g., `202408.csv`, `202409.csv`)

## Output Format

The system creates separate CSV files for each month (named `YYYYMM.csv`) containing:

- `date`: Transaction date (standardized)
- `description`: Original transaction description
- `amount`: Standardized amount (positive = expense, negative = income)
- `bank`: Bank name
- `month`: Source month from filename
- `comment`: Your categorized description (e.g., "Coffee", "Groceries")

## Tips

- Use consistent category names (e.g., "Groceries" not "groceries" or "Grocery")
- The system learns from your input - be consistent for better automation
- Review the `config/category_mapping.json` periodically to clean up categories
- Backup your config files - they contain your learned categorizations

## Troubleshooting

**File format errors**: Ensure your CSV/Excel files have the required columns
**Date parsing errors**: Check the date format in your bank config
**Missing categories**: Run without `--no-interactive` to categorize new descriptions
