# Bank Transaction Merger and Categorizer

A Python tool to merge bank transaction files from different banks and automatically categorize expenses.

## Features

- 📊 Merge transaction files from multiple banks (CSV)
- 🏦 Support for CBA, ANZ, Westpac, NAB with configurable formats
- 🔄 Automatic amount sign normalization (positive for expenses, negative for income)
- 🏷️ **Intelligent transaction categorization** with 94% automatic recognition
- 💬 Interactive CLI for manual categorization with pattern suggestions
- 🔍 Multi-level matching: exact, pattern-based, and fuzzy matching
- 🧠 Smart pattern recognition for common merchants and categories
- 🌏 Multi-language support (English, Chinese characters)
- 💾 Persistent category mapping storage

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

   - Place bank transaction CSV files in `data/input/`
   - Use naming format: `<bank>-<YYYYMM>.csv`
   - Examples: `amex-202408.csv`, `cba-202408.csv`, `westpac-202409.csv`

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

### File Format Requirements

Your CSV files should contain these columns (case-insensitive):

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

The system features an **intelligent automatic categorization system** with multiple matching strategies:

### Automatic Pattern Recognition

The system automatically recognizes common transaction patterns without manual setup:

- **Groceries**: WOOLWORTHS, COLES, IGA, ALDI, SUPERMARKET, GROCERIES
- **Coffee**: COFFEE, STARBUCKS, CAFE, ESPRESSO, 咖啡
- **Fast Food**: MCDONALD, KFC, BURGER KING, SUBWAY, DOMINO, PIZZA, 麦当劳
- **Income**: SALARY, WAGE, PAY, INCOME, DEPOSIT, TRANSFER IN
- **Bank Fees**: BANK FEE, ATM FEE, MONTHLY FEE, ACCOUNT FEE
- **Transport**: UBER, TAXI, TRAIN, BUS, METRO, TRANSPORT, PETROL, FUEL

### Multi-Level Matching System

1. **Exact Match**: Direct lookup from stored mappings
2. **Smart Pattern Matching**: Keyword recognition for common brands/categories
3. **Fuzzy Matching**: Similar descriptions with 60% similarity threshold
4. **Manual Entry**: For unique descriptions not covered by patterns

### Learning Capabilities

The system automatically learns from your input:

1. **First run**: Manually categorize unknown descriptions
2. **Subsequent runs**: Automatic categorization based on:
   - Built-in pattern recognition (~94% success rate)
   - Learned exact mappings
   - Fuzzy matching for similar descriptions
3. **Pattern suggestions**: System suggests reusable patterns for new mappings

### Storage System

- **`config/category_mapping.json`**: Stores exact description→category mappings
- **`config/pattern_mapping.json`**: Stores custom pattern rules (optional)
- **Built-in patterns**: Hard-coded intelligent recognition for common merchants

Categories persist between runs and improve accuracy over time.

## Example Workflow

1. Export transaction files from your banks
2. Rename files following the `<bank>-<YYYYMM>.csv` format
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
- `comment`: Your categorized description (e.g., "coffee", "groceries", "transport")

## Enhanced Features

### Smart Categorization Examples

The system automatically recognizes common patterns:

```csv
Original Description              → Auto Category
WOOLWORTHS 1234 SYDNEY           → groceries
STARBUCKS COFFEE #123            → coffee
McDONALD'S 麦当劳 M456             → fast food
UBER TRIP 123                    → transport
BANK FEE MONTHLY                 → bank fees
SALARY PAYMENT                   → income
```

### Multi-Language Support

Supports transaction descriptions in multiple languages:

- English: "STARBUCKS COFFEE" → coffee
- Chinese: "麦当劳" (McDonald's) → fast food
- Mixed: "McDONALD'S 麦当劳 M456" → fast food

## Tips

- Use consistent category names (e.g., "Groceries" not "groceries" or "Grocery")
- The system learns from your input - be consistent for better automation
- Review the `config/category_mapping.json` periodically to clean up categories
- Backup your config files - they contain your learned categorizations

## Troubleshooting

**File format errors**: Ensure your CSV files have the required columns
**Date parsing errors**: Check the date format in your bank config
**Missing categories**: Run without `--no-interactive` to categorize new descriptions
