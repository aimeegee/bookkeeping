import json
from pathlib import Path
import difflib

class CategoryManager:
    def __init__(self, mapping_file="config/category_mapping.json"):
        self.mapping_file = Path(mapping_file)
        self.mapping = self.load_mapping()
    
    def load_mapping(self):
        """加载描述->分类映射"""
        if self.mapping_file.exists():
            with open(self.mapping_file) as f:
                return json.load(f)
        return {}
    
    def save_mapping(self):
        """保存映射到文件"""
        self.mapping_file.parent.mkdir(exist_ok=True)
        with open(self.mapping_file, 'w') as f:
            json.dump(self.mapping, f, indent=2, ensure_ascii=False)
    
    def get_category(self, description):
        """获取描述对应的分类"""
        # 直接匹配
        if description in self.mapping:
            return self.mapping[description]
        
        # 模糊匹配
        close_matches = difflib.get_close_matches(
            description, self.mapping.keys(), n=1, cutoff=0.8
        )
        if close_matches:
            return self.mapping[close_matches[0]]
        
        return None
    
    def add_mapping(self, description, category):
        """添加新的映射"""
        self.mapping[description] = category
        self.save_mapping()
    
    def apply_categories(self, df):
        """为DataFrame添加分类列"""
        df['comment'] = df['description'].apply(self.get_category)
        return df
    
    def get_unmapped_descriptions(self, df):
        """获取未分类的描述"""
        return df[df['comment'].isna()]['description'].unique().tolist()
