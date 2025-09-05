#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced description mapping system
"""

import sys
import pandas as pd
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

from category_manager import CategoryManager

def test_enhanced_mapping():
    """Test the enhanced CategoryManager functionality"""
    print("=== Enhanced Description Mapping System Test ===\n")
    
    # Initialize CategoryManager
    cm = CategoryManager()
    
    # Test transactions with various patterns
    test_descriptions = [
        "WOOLWORTHS 1234 SYDNEY",
        "STARBUCKS COFFEE #123", 
        "McDONALD'S 麦当劳 M456",
        "SALARY PAYMENT",
        "COLES SUPERMARKET 789",
        "UBER TRIP 123",
        "KFC CHICKEN #456",
        "IGA SUPERMARKET BRIS",
        "BANK FEE MONTHLY",
        "ALDI STORE 789",
        "DOMINO'S PIZZA #123",
        "PETROL STATION FUEL",
        "CAFE LATTE DOWNTOWN",
        "ANOTHER WOOLWORTHS STORE",
        "NEW COFFEE PLACE",
        "UNKNOWN MERCHANT",
    ]
    
    print("Testing automatic categorization:\n")
    for desc in test_descriptions:
        category = cm.get_category(desc)
        status = "✅ AUTO" if category else "❌ MANUAL"
        print(f"{status:10} | {desc:30} | {category or 'Not categorized':15}")
    
    # Test pattern matching capabilities
    print(f"\n=== Pattern Matching Results ===")
    auto_categorized = sum(1 for desc in test_descriptions if cm.get_category(desc))
    manual_needed = len(test_descriptions) - auto_categorized
    
    print(f"Automatically categorized: {auto_categorized}/{len(test_descriptions)} ({auto_categorized/len(test_descriptions)*100:.1f}%)")
    print(f"Manual categorization needed: {manual_needed}")
    
    print(f"\n=== Built-in Pattern Categories ===")
    categories = {
        "groceries": ["WOOLWORTHS", "COLES", "IGA", "ALDI", "SUPERMARKET"],
        "coffee": ["COFFEE", "STARBUCKS", "CAFE", "ESPRESSO", "咖啡"],
        "fast food": ["MCDONALD", "KFC", "BURGER KING", "SUBWAY", "DOMINO", "PIZZA", "麦当劳"],
        "income": ["SALARY", "WAGE", "PAY", "INCOME", "DEPOSIT"],
        "bank fees": ["BANK FEE", "ATM FEE", "MONTHLY FEE", "ACCOUNT FEE"],
        "transport": ["UBER", "TAXI", "TRAIN", "BUS", "METRO", "TRANSPORT", "PETROL", "FUEL"]
    }
    
    for category, keywords in categories.items():
        print(f"{category:12}: {', '.join(keywords)}")

if __name__ == "__main__":
    test_enhanced_mapping()