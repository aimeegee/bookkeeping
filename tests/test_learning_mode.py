import unittest
import sys
from pathlib import Path
import tempfile
import shutil
import pandas as pd
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from learning_mode import LearningMode
from category_manager import CategoryManager

class TestLearningMode(unittest.TestCase):
    """Test cases for LearningMode class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create temporary config files
        self.mapping_file = Path(self.temp_dir) / 'category_mapping.json'
        
        # Initialize with minimal test data
        test_mapping = {
            "EXISTING MERCHANT": "existing_category"
        }
        
        with open(self.mapping_file, 'w') as f:
            json.dump(test_mapping, f)
        
        self.cm = CategoryManager(mapping_file=str(self.mapping_file))
        self.learning_mode = LearningMode(self.cm)
        
        # Create test CSV file
        self.test_csv = Path(self.temp_dir) / 'test_learning.csv'
        self.create_test_csv()
    
    def tearDown(self):
        """Clean up after each test method"""
        shutil.rmtree(self.temp_dir)
    
    def create_test_csv(self):
        """Create a test CSV file for learning"""
        test_data = {
            'date': ['2025-08-01', '2025-08-02', '2025-08-03'],
            'description': ['NEW MERCHANT 1', 'NEW MERCHANT 2', 'UNCATEGORIZED MERCHANT'],
            'amount': [50.00, 25.50, 15.00],
            'category': ['groceries', 'coffee', ''],  # Last one is uncategorized
            'bank': ['Test Bank', 'Test Bank', 'Test Bank'],
            'comment': ['', '', 'needs categorization']
        }
        
        df = pd.DataFrame(test_data)
        df.to_csv(self.test_csv, index=False)
    
    def test_learn_existing_categories(self):
        """Test learning from categorized transactions"""
        # Create a simple test DataFrame
        test_data = pd.DataFrame({
            'description': ['NEW MERCHANT 1', 'NEW MERCHANT 2'],
            'category': ['groceries', 'coffee']
        })
        
        initial_count = len(self.cm.mapping)
        learned_count = self.learning_mode._learn_existing_categories(test_data)
        
        # Should have learned 2 new mappings
        self.assertEqual(learned_count, 2)
        self.assertEqual(len(self.cm.mapping), initial_count + 2)
        
        # Check the mappings were added
        self.assertEqual(self.cm.get_exact_match('NEW MERCHANT 1'), 'groceries')
        self.assertEqual(self.cm.get_exact_match('NEW MERCHANT 2'), 'coffee')
    
    def test_csv_format_validation(self):
        """Test CSV format validation"""
        # Create invalid CSV (missing required columns)
        invalid_csv = Path(self.temp_dir) / 'invalid.csv'
        invalid_data = pd.DataFrame({
            'date': ['2025-08-01'],
            'description': ['TEST'],
            # Missing amount, category, bank columns
        })
        invalid_data.to_csv(invalid_csv, index=False)
        
        # Should return False for invalid format
        result = self.learning_mode.learn_from_csv(str(invalid_csv))
        self.assertFalse(result)
    
    def test_valid_csv_processing(self):
        """Test processing a valid CSV file"""
        # The test CSV created in setUp should be valid
        result = self.learning_mode.learn_from_csv(str(self.test_csv))
        
        # Should succeed (even though it might not categorize uncategorized items in test)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
