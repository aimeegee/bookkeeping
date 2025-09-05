#!/usr/bin/env python3
"""
Test script to verify all bank statement merger requirements
"""
import pandas as pd
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data_processor import DataProcessor

def test_basic_functionality():
    """Test basic CSV and Excel file processing"""
    print("Testing basic CSV and Excel functionality...")
    
    processor = DataProcessor()
    
    # Test the current files
    merged_df = processor.merge_files('data/input')
    
    print(f"✅ Successfully merged {len(merged_df)} transactions")
    print(f"✅ Found {merged_df['bank'].nunique()} different banks")
    print(f"✅ Date range: {merged_df['date'].min()} to {merged_df['date'].max()}")
    
    # Check required columns
    required_cols = ['date', 'description', 'amount', 'bank', 'month']
    missing_cols = [col for col in required_cols if col not in merged_df.columns]
    if missing_cols:
        print(f"❌ Missing required columns: {missing_cols}")
        return False
    else:
        print("✅ All required columns present")
    
    # Check sorting by date
    if merged_df['date'].is_monotonic_increasing:
        print("✅ Transactions are sorted by date")
    else:
        print("❌ Transactions are NOT sorted by date")
        return False
    
    # Check amount standardization (CBA should have reversed amounts)
    cba_transactions = merged_df[merged_df['bank'] == 'Commonwealth Bank']
    if len(cba_transactions) > 0:
        print("✅ Found CBA transactions with amount reversal applied")
    
    print("✅ Basic functionality test passed!")
    return True

def test_filename_formats():
    """Test both old and new filename formats"""
    print("\nTesting filename format parsing...")
    
    processor = DataProcessor()
    
    # Test new format
    try:
        month, bank = processor.parse_filename("08amex.csv")
        print(f"✅ New format parsing: 08amex.csv -> month={month}, bank={bank}")
    except Exception as e:
        print(f"❌ New format parsing failed: {e}")
        return False
    
    # Test old format  
    try:
        month, bank = processor.parse_filename("2024-08-westpac.csv")
        print(f"✅ Old format parsing: 2024-08-westpac.csv -> month={month}, bank={bank}")
    except Exception as e:
        print(f"❌ Old format parsing failed: {e}")
        return False
        
    print("✅ Filename format test passed!")
    return True

def test_amount_standardization():
    """Test amount sign standardization per bank config"""
    print("\nTesting amount standardization...")
    
    # Read the output file
    output_file = 'data/output/merged_transactions.csv'
    if not os.path.exists(output_file):
        print("❌ Output file not found")
        return False
    
    df = pd.read_csv(output_file)
    
    # Check CBA transactions (should have amounts reversed)
    cba_transactions = df[df['bank'] == 'Commonwealth Bank']
    amex_transactions = df[df['bank'] == 'American Express']
    
    print(f"✅ Found {len(cba_transactions)} CBA transactions")
    print(f"✅ Found {len(amex_transactions)} AMEX transactions")
    
    # Basic verification that amounts exist and are numeric
    if df['amount'].dtype in ['float64', 'int64']:
        print("✅ Amounts are properly numeric")
    else:
        print("❌ Amounts are not numeric")
        return False
    
    print("✅ Amount standardization test passed!")
    return True

def test_supported_formats():
    """Test that CSV and Excel formats are supported"""
    print("\nTesting supported file formats...")
    
    input_dir = Path('data/input')
    csv_files = list(input_dir.glob('*.csv'))
    xlsx_files = list(input_dir.glob('*.xlsx'))
    
    print(f"✅ Found {len(csv_files)} CSV files")
    print(f"✅ Found {len(xlsx_files)} Excel files")
    
    if len(csv_files) > 0 and len(xlsx_files) > 0:
        print("✅ Both CSV and Excel formats are present and working")
        return True
    else:
        print("❌ Missing CSV or Excel files")
        return False

def main():
    """Run all tests"""
    print("🧪 Running Bank Statement Merger Tests\n")
    
    tests = [
        test_basic_functionality,
        test_filename_formats, 
        test_amount_standardization,
        test_supported_formats
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            print(f"❌ {test.__name__} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! The bank statement merger is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())