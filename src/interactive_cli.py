try:
    from .category_manager import CategoryManager
except ImportError:
    # For when running tests or standalone
    from category_manager import CategoryManager

class InteractiveCLI:
    def __init__(self, category_manager):
        self.cm = category_manager
    
    def update_categories(self, df, month=None):
        """交互式更新分类"""
        unmapped = self.cm.get_unmapped_descriptions(df)
        
        if not unmapped:
            month_text = f" for {month}" if month else ""
            print(f"All descriptions have been categorized{month_text}!")
            return df
        
        month_text = f" in {month}" if month else ""
        print(f"Found {len(unmapped)} unmapped descriptions{month_text}:")
        
        skip_all = False
        
        for desc in unmapped:
            if skip_all:
                break
            print(f"\nDescription: '{desc}'")
            
            # 显示类似的已有分类
            similar = self.suggest_similar_categories(desc)
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
                    print("Skipping all remaining unmapped descriptions...")
                    break
                
                if category:
                    self.cm.add_mapping(desc, category, is_programmatic=False)
                    print(f"Added: '{desc}' -> '{category}'")
                    
                    # 建议通用模式
                    patterns = self.cm.suggest_pattern_from_mapping(desc, category)
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
                    print("Please enter a valid category or 'skip'")
        
        # 重新应用分类
        return self.cm.apply_categories(df)
    
    def suggest_similar_categories(self, description):
        """建议相似的分类"""
        import difflib
        existing_categories = list(set(self.cm.mapping.values()))
        return difflib.get_close_matches(
            description.lower(), 
            [cat.lower() for cat in existing_categories], 
            n=3, cutoff=0.6
        )
