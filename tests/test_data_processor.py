import unittest
import sys
from pathlib import Path
import tempfile
import shutil
import pandas as pd
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_processor import DataProcessor

class TestDataProcessor(unittest.TestCase):
    """Test cases for DataProcessor class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create a temporary bank config for testing
        self.temp_config_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_config_dir) / 'bank_config.json'
        
        # Create test bank config
        test_config = {
            "cba": {
                "name": "Commonwealth Bank",
                "revert_amount": True,
                "date_format": "%d/%m/%Y"
            },
            "amex": {
                "name": "American Express",
                "revert_amount": False,
                "date_format": "%d/%m/%Y"
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
        
        self.processor = DataProcessor(str(self.config_file))
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test CSV files
        self.create_test_files()
    
    def tearDown(self):
        """Clean up after each test method"""
        shutil.rmtree(self.temp_dir)
        shutil.rmtree(self.temp_config_dir)
    
    def create_test_files(self):
        """Create test CSV files with known data"""
        # Create test CBA file
        cba_data = {
            'Date': ['01/08/2025', '02/08/2025'],
            'Description': ['WOOLWORTHS SYDNEY', 'COFFEE SHOP'],
            'Amount': [-50.00, -5.50]  # CBA uses negative for expenses
        }
        cba_df = pd.DataFrame(cba_data)
        cba_path = Path(self.temp_dir) / 'cba-202508.csv'
        cba_df.to_csv(cba_path, index=False)
        
        # Create test AMEX file
        amex_data = {
            'Date': ['03/08/2025', '04/08/2025'],
            'Description': ['AMAZON PURCHASE', 'RESTAURANT'],
            'Amount': [100.00, 75.50]  # AMEX uses positive for expenses
        }
        amex_df = pd.DataFrame(amex_data)
        amex_path = Path(self.temp_dir) / 'amex-202508.csv'
        amex_df.to_csv(amex_path, index=False)
    
    def test_filename_parsing_new_format(self):
        """Test parsing of new filename format: <bank>-<YYYYMM>.csv"""
        month, bank = self.processor.parse_filename("amex-202508.csv")
        self.assertEqual(month, "2025-08")
        self.assertEqual(bank, "amex")
        
        month, bank = self.processor.parse_filename("cba-202412.csv")
        self.assertEqual(month, "2024-12")
        self.assertEqual(bank, "cba")
    
    def test_filename_parsing_invalid_format(self):
        """Test parsing of invalid filename formats"""
        with self.assertRaises(ValueError):
            self.processor.parse_filename("invalid-filename.csv")
        
        with self.assertRaises(ValueError):
            self.processor.parse_filename("amex-20250.csv")  # Invalid date
    
    def test_load_and_process_file(self):
        """Test loading and processing individual files"""
        cba_file = Path(self.temp_dir) / 'cba-202508.csv'
        df = self.processor.load_and_process_file(str(cba_file))
        
        # Check required columns
        required_cols = ['date', 'description', 'amount', 'bank', 'month']
        for col in required_cols:
            self.assertIn(col, df.columns)
        
        # Check data types
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df['date']))
        self.assertTrue(pd.api.types.is_numeric_dtype(df['amount']))
        
        # Check amount reversal for CBA (revert_amount: true in config)
        # Original amounts are negative, should be made positive
        self.assertTrue(all(df['amount'] > 0))
    
    def test_merge_files(self):
        """Test merging multiple bank files"""
        monthly_data = self.processor.merge_files(self.temp_dir)
        
        # Should have data for August 2025
        self.assertIn('202508', monthly_data)
        
        df = monthly_data['202508']
        
        # Should have 4 transactions total (2 from each bank)
        self.assertEqual(len(df), 4)
        
        # Should have both banks
        banks = df['bank'].unique()
        self.assertIn('Commonwealth Bank', banks)
        self.assertIn('American Express', banks)
        
        # Should be sorted by date
        self.assertTrue(df['date'].is_monotonic_increasing)
    
    def test_save_monthly_files(self):
        """Test saving monthly files with correct format"""
        # Create test data
        test_data = {
            '202508': pd.DataFrame({
                'date': pd.to_datetime(['2025-08-01', '2025-08-02']),
                'description': ['TEST MERCHANT 1', 'TEST MERCHANT 2'],
                'amount': [50.00, 25.50],
                'bank': ['Test Bank', 'Test Bank'],
                'month': ['2025-08', '2025-08'],
                'comment': ['groceries', 'coffee']
            })
        }
        
        # Save files
        output_dir = Path(self.temp_dir) / 'output'
        saved_files = self.processor.save_monthly_files(test_data, str(output_dir))
        
        # Check file was created
        self.assertEqual(len(saved_files), 1)
        self.assertTrue(Path(saved_files[0]).exists())
        
        # Check file content
        df = pd.read_csv(saved_files[0])
        
        # Check column order: date, description, amount, category, bank, comment
        expected_columns = ['date', 'description', 'amount', 'category', 'bank', 'comment']
        self.assertEqual(list(df.columns), expected_columns)
        
        # Check that 'comment' was renamed to 'category'
        self.assertEqual(df['category'].iloc[0], 'groceries')
        self.assertEqual(df['category'].iloc[1], 'coffee')

if __name__ == '__main__':
    unittest.main()
