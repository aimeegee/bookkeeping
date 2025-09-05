import pandas as pd
import json
from pathlib import Path

try:
    from .category_manager import CategoryManager
    from .interactive_cli import InteractiveCLI
except ImportError:
    # For when running tests or standalone
    from category_manager import CategoryManager
    from interactive_cli import InteractiveCLI

class LearningMode:
    def __init__(self, category_manager):
        self.cm = category_manager
        self.cli = InteractiveCLI(category_manager)
    
    def learn_from_csv(self, csv_file_path):
        """从CSV文件学习分类"""
        try:
            df = pd.read_csv(csv_file_path)
            print(f"Loading learning data from: {csv_file_path}")
            
            # 验证CSV格式
            required_columns = ['date', 'description', 'amount', 'category', 'bank']
            if not all(col in df.columns for col in required_columns):
                print(f"Error: CSV file must contain columns: {required_columns}")
                return False
            
            # 统计信息
            total_rows = len(df)
            rows_with_category = df['category'].notna().sum()
            rows_without_category = total_rows - rows_with_category
            
            print(f"Found {total_rows} transactions:")
            print(f"  - {rows_with_category} with categories")
            print(f"  - {rows_without_category} without categories")
            
            # 1. 学习已有分类
            learned_mappings = self._learn_existing_categories(df)
            
            # 2. 处理未分类的交易
            if rows_without_category > 0:
                print(f"\nProcessing {rows_without_category} uncategorized transactions...")
                self._process_uncategorized(df)
            
            print(f"\nLearning completed!")
            print(f"Added {learned_mappings} new category mappings")
            
            return True
            
        except Exception as e:
            print(f"Error processing learning file: {e}")
            return False
    
    def _learn_existing_categories(self, df):
        """学习已有的分类映射"""
        learned_count = 0
        categorized_df = df[df['category'].notna()]
        
        if len(categorized_df) == 0:
            return learned_count
        
        print(f"\nLearning from {len(categorized_df)} categorized transactions...")
        
        for _, row in categorized_df.iterrows():
            description = row['description']
            category = row['category']
            
            # 检查是否已经有这个映射
            existing_category = self.cm.get_exact_match(description)
            
            if existing_category is None:
                # 添加新的映射
                self.cm.add_mapping(description, category)
                learned_count += 1
                print(f"  Learned: '{description}' -> '{category}'")
            elif existing_category != category:
                # 映射冲突，询问用户
                print(f"\nConflict found:")
                print(f"  Description: '{description}'")
                print(f"  Existing mapping: '{existing_category}'")
                print(f"  New mapping: '{category}'")
                
                choice = input("Keep (e)xisting, use (n)ew, or (s)kip? [e/n/s]: ").strip().lower()
                if choice == 'n':
                    self.cm.add_mapping(description, category)
                    learned_count += 1
                    print(f"  Updated: '{description}' -> '{category}'")
                elif choice == 'e':
                    print(f"  Kept existing mapping")
                else:
                    print(f"  Skipped")
        
        return learned_count
    
    def _process_uncategorized(self, df):
        """处理未分类的交易"""
        uncategorized_df = df[df['category'].isna() | (df['category'] == '')]
        
        if len(uncategorized_df) == 0:
            return
        
        print(f"\nProcessing uncategorized transactions...")
        skip_all = False
        
        for _, row in uncategorized_df.iterrows():
            if skip_all:
                break
                
            description = row['description']
            comment = row.get('comment', '')
            
            # 尝试自动分类
            auto_category = self.cm.get_category(description)
            
            if auto_category:
                print(f"\nAuto-categorized: '{description}' -> '{auto_category}'")
                continue
            
            # 需要手动分类
            print(f"\nUncategorized transaction:")
            print(f"  Description: '{description}'")
            if comment and comment.strip():
                print(f"  Comment: '{comment}'")
            print(f"  Amount: {row['amount']}")
            print(f"  Bank: {row['bank']}")
            
            # 显示相似的已有分类
            similar = self.cli.suggest_similar_categories(description)
            if similar:
                print("Similar existing categories:")
                for i, cat in enumerate(similar, 1):
                    print(f"  {i}. {cat}")
            
            while True:
                category = input("Enter category (or 'skip' to skip, 'skip-all' to skip all remaining): ").strip()
                
                if category.lower() == 'skip':
                    break
                elif category.lower() == 'skip-all':
                    skip_all = True
                    print("Skipping all remaining uncategorized transactions...")
                    break
                elif category:
                    self.cm.add_mapping(description, category)
                    print(f"Added: '{description}' -> '{category}'")
                    
                    # 建议通用模式
                    patterns = self.cm.suggest_pattern_from_mapping(description, category)
                    if patterns:
                        print(f"\nSuggested patterns for automatic matching:")
                        for pattern in patterns:
                            print(f"  - {pattern}")
                        
                        add_pattern = input("Add any pattern? (y/N or specify pattern): ").strip()
                        if add_pattern.lower() == 'y' and patterns:
                            # 添加第一个建议的模式
                            self.cm.add_pattern(patterns[0], category)
                            print(f"Added pattern: '{patterns[0]}' -> '{category}'")
                        elif add_pattern and add_pattern.lower() != 'n':
                            # 用户指定的模式
                            self.cm.add_pattern(add_pattern, category)
                            print(f"Added pattern: '{add_pattern}' -> '{category}'")
                    
                    break
                else:
                    print("Please enter a valid category or 'skip'/'skip-all'")
