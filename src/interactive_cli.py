from .category_manager import CategoryManager

class InteractiveCLI:
    def __init__(self, category_manager):
        self.cm = category_manager
    
    def update_categories(self, df):
        """交互式更新分类"""
        unmapped = self.cm.get_unmapped_descriptions(df)
        
        if not unmapped:
            print("All descriptions have been categorized!")
            return df
        
        print(f"Found {len(unmapped)} unmapped descriptions:")
        
        for desc in unmapped:
            print(f"\nDescription: '{desc}'")
            
            # 显示类似的已有分类
            similar = self.suggest_similar_categories(desc)
            if similar:
                print("Similar existing categories:")
                for i, cat in enumerate(similar, 1):
                    print(f"  {i}. {cat}")
            
            while True:
                category = input("Enter category (or 'skip' to skip): ").strip()
                
                if category.lower() == 'skip':
                    break
                
                if category:
                    self.cm.add_mapping(desc, category)
                    print(f"Added: '{desc}' -> '{category}'")
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
