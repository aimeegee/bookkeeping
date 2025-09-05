import json
from pathlib import Path
import difflib
import re

class CategoryManager:
    def __init__(self, mapping_file="config/category_mapping.json", patterns_file="config/pattern_mapping.json"):
        self.mapping_file = Path(mapping_file)
        self.patterns_file = Path(patterns_file)
        self.mapping = self.load_mapping()
        self.patterns = self.load_patterns()
    
    def load_mapping(self):
        """加载描述->分类映射"""
        if self.mapping_file.exists():
            with open(self.mapping_file) as f:
                return json.load(f)
        return {}
    
    def load_patterns(self):
        """加载模式->分类映射"""
        if self.patterns_file.exists():
            with open(self.patterns_file) as f:
                return json.load(f)
        return {}
    
    def save_mapping(self):
        """保存映射到文件"""
        self.mapping_file.parent.mkdir(exist_ok=True)
        with open(self.mapping_file, 'w') as f:
            json.dump(self.mapping, f, indent=2, ensure_ascii=False)
    
    def save_patterns(self):
        """保存模式映射到文件"""
        self.patterns_file.parent.mkdir(exist_ok=True)
        with open(self.patterns_file, 'w') as f:
            json.dump(self.patterns, f, indent=2, ensure_ascii=False)
    
    def get_category(self, description):
        """获取描述对应的分类"""
        # 1. 直接匹配
        if description in self.mapping:
            return self.mapping[description]
        
        # 2. 模式匹配 (关键词/品牌名识别)
        category = self._match_patterns(description)
        if category:
            return category
        
        # 3. 改进的模糊匹配
        close_matches = difflib.get_close_matches(
            description, self.mapping.keys(), n=1, cutoff=0.6  # 降低阈值，提高匹配率
        )
        if close_matches:
            return self.mapping[close_matches[0]]
        
        return None
    
    def _match_patterns(self, description):
        """基于模式匹配获取分类"""
        description_upper = description.upper()
        
        # 检查用户定义的模式
        for pattern, category in self.patterns.items():
            if self._pattern_matches(pattern, description_upper):
                return category
        
        # 内置智能模式匹配
        built_in_category = self._built_in_pattern_match(description_upper)
        if built_in_category:
            return built_in_category
        
        return None
    
    def _pattern_matches(self, pattern, description):
        """检查模式是否匹配描述"""
        # 支持不同类型的模式
        if pattern.startswith('CONTAINS:'):
            keyword = pattern[9:]  # 移除 "CONTAINS:" 前缀
            return keyword in description
        elif pattern.startswith('REGEX:'):
            regex_pattern = pattern[6:]  # 移除 "REGEX:" 前缀
            return bool(re.search(regex_pattern, description, re.IGNORECASE))
        else:
            # 默认为包含匹配
            return pattern.upper() in description
    
    def _built_in_pattern_match(self, description):
        """内置的智能模式匹配"""
        # 常见超市/杂货店
        grocery_keywords = ['WOOLWORTHS', 'COLES', 'IGA', 'ALDI', 'SUPERMARKET', 'GROCERIES']
        if any(keyword in description for keyword in grocery_keywords):
            return 'groceries'
        
        # 咖啡相关
        coffee_keywords = ['COFFEE', 'STARBUCKS', 'CAFE', 'ESPRESSO', '咖啡']
        if any(keyword in description for keyword in coffee_keywords):
            return 'coffee'
        
        # 快餐
        fastfood_keywords = ['MCDONALD', 'KFC', 'BURGER KING', 'SUBWAY', 'DOMINO', 'PIZZA', '麦当劳']
        if any(keyword in description for keyword in fastfood_keywords):
            return 'fast food'
        
        # 工资/收入
        income_keywords = ['SALARY', 'WAGE', 'PAY', 'INCOME', 'DEPOSIT', 'TRANSFER IN']
        if any(keyword in description for keyword in income_keywords):
            return 'income'
        
        # 银行费用
        bank_keywords = ['BANK FEE', 'ATM FEE', 'MONTHLY FEE', 'ACCOUNT FEE']
        if any(keyword in description for keyword in bank_keywords):
            return 'bank fees'
        
        # 交通
        transport_keywords = ['UBER', 'TAXI', 'TRAIN', 'BUS', 'METRO', 'TRANSPORT', 'PETROL', 'FUEL']
        if any(keyword in description for keyword in transport_keywords):
            return 'transport'
        
        return None
    
    def add_mapping(self, description, category):
        """添加新的映射"""
        self.mapping[description] = category
        self.save_mapping()
    
    def add_pattern(self, pattern, category):
        """添加新的模式映射"""
        self.patterns[pattern] = category
        self.save_patterns()
    
    def apply_categories(self, df):
        """为DataFrame添加分类列"""
        df['comment'] = df['description'].apply(self.get_category)
        return df
    
    def get_unmapped_descriptions(self, df):
        """获取未分类的描述"""
        return df[df['comment'].isna()]['description'].unique().tolist()
    
    def suggest_pattern_from_mapping(self, description, category):
        """根据新映射建议通用模式"""
        description_upper = description.upper()
        suggestions = []
        
        # 检查是否包含常见关键词
        common_keywords = [
            'WOOLWORTHS', 'COLES', 'IGA', 'ALDI', 'SUPERMARKET',
            'COFFEE', 'STARBUCKS', 'CAFE',
            'MCDONALD', 'KFC', 'BURGER', 'PIZZA',
            'UBER', 'TAXI', 'PETROL', 'FUEL',
            'SALARY', 'WAGE', 'PAY'
        ]
        
        for keyword in common_keywords:
            if keyword in description_upper:
                pattern = f"CONTAINS:{keyword}"
                suggestions.append(pattern)
        
        return suggestions
    
    def get_exact_match(self, description):
        """获取精确匹配的分类，用于学习模式"""
        return self.mapping.get(description)
