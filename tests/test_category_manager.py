import unittest
import sys
from pathlib import Path
import tempfile
import shutil
import pandas as pd
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from category_manager import CategoryManager

class TestCategoryManager(unittest.TestCase):
    """Test cases for CategoryManager class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create temporary config files
        self.mapping_file = Path(self.temp_dir) / 'category_mapping.yml'
        self.patterns_file = Path(self.temp_dir) / 'pattern_mapping.json'
        
        # Initialize with test data - create YAML format
        test_mapping_yaml = """- coffee
  - "STARBUCKS"
- fast food
  - "MCDONALD'S"
- groceries
  - "WOOLWORTHS"
"""
        
        test_patterns = {
            "COFFEE": "coffee",
            "SUPERMARKET": "groceries"
        }
        
        with open(self.mapping_file, 'w') as f:
            f.write(test_mapping_yaml)
        
        with open(self.patterns_file, 'w') as f:
            json.dump(test_patterns, f)
        
        self.cm = CategoryManager(
            mapping_file=str(self.mapping_file),
            patterns_file=str(self.patterns_file)
        )
    
    def tearDown(self):
        """Clean up after each test method"""
        shutil.rmtree(self.temp_dir)
    
    def test_exact_match(self):
        """Test exact description matching"""
        self.assertEqual(self.cm.get_category("WOOLWORTHS"), "groceries")
        self.assertEqual(self.cm.get_category("MCDONALD'S"), "fast food")
        self.assertIsNone(self.cm.get_category("UNKNOWN MERCHANT"))
    
    def test_pattern_matching(self):
        """Test pattern-based matching"""
        # Should match COFFEE pattern
        self.assertEqual(self.cm.get_category("STARBUCKS COFFEE SHOP"), "coffee")
        
        # Should match SUPERMARKET pattern
        self.assertEqual(self.cm.get_category("COLES SUPERMARKET"), "groceries")
    
    def test_add_mapping(self):
        """Test adding new mappings"""
        self.cm.add_mapping("NEW MERCHANT", "shopping")
        self.assertEqual(self.cm.get_category("NEW MERCHANT"), "shopping")
        
        # Check that it's saved in YAML format
        self.cm.save_mapping()
        with open(self.mapping_file, 'r') as f:
            yaml_content = f.read()
        self.assertIn("NEW MERCHANT", yaml_content)
        self.assertIn("shopping", yaml_content)
    
    def test_get_exact_match(self):
        """Test exact match retrieval for learning mode"""
        self.assertEqual(self.cm.get_exact_match("WOOLWORTHS"), "groceries")
        self.assertIsNone(self.cm.get_exact_match("WOOLWORTHS SYDNEY"))  # Should be None for non-exact
    
    def test_apply_categories(self):
        """Test applying categories to a DataFrame"""
        test_data = pd.DataFrame({
            'description': ['WOOLWORTHS', 'MCDONALD\'S', 'UNKNOWN PLACE'],
            'amount': [50.0, 25.0, 10.0]
        })
        
        result_df = self.cm.apply_categories(test_data)
        
        # Check that comment column was added
        self.assertIn('comment', result_df.columns)
        
        # Check categorizations
        self.assertEqual(result_df.loc[0, 'comment'], 'groceries')
        self.assertEqual(result_df.loc[1, 'comment'], 'fast food')
        self.assertIsNone(result_df.loc[2, 'comment'])  # Unknown should be None
    
    def test_get_unmapped_descriptions(self):
        """Test getting unmapped descriptions"""
        test_data = pd.DataFrame({
            'description': ['WOOLWORTHS', 'UNKNOWN PLACE 1', 'UNKNOWN PLACE 2']
        })
        
        # Apply categories first to create comment column
        test_data = self.cm.apply_categories(test_data)
        
        unmapped = self.cm.get_unmapped_descriptions(test_data)
        
        # Should return the two unknown places
        self.assertEqual(len(unmapped), 2)
        self.assertIn('UNKNOWN PLACE 1', unmapped)
        self.assertIn('UNKNOWN PLACE 2', unmapped)
        self.assertNotIn('WOOLWORTHS', unmapped)

if __name__ == '__main__':
    unittest.main()
