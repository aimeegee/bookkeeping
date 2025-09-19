import json
from pathlib import Path
import difflib
import re

class CategoryManager:
    def __init__(self, mapping_file="config/category_mapping.yml", patterns_file="config/pattern_mapping.json"):
        # If a specific mapping file is provided, use it directly
        provided_mapping_file = Path(mapping_file)
        
        # Only use auto-detection if using default file paths
        if mapping_file == "config/category_mapping.yml":
            # Default behavior: check for YAML first, fall back to JSON
            yaml_mapping_file = Path("config/category_mapping.yml")
            json_mapping_file = Path("config/category_mapping.json")
            
            if yaml_mapping_file.exists():
                self.mapping_file = yaml_mapping_file
                self.use_yaml = True
            elif json_mapping_file.exists():
                self.mapping_file = json_mapping_file
                self.use_yaml = False
            else:
                # Default to YAML for new installations
                self.mapping_file = yaml_mapping_file
                self.use_yaml = True
        else:
            # Use the specifically provided file
            self.mapping_file = provided_mapping_file
            self.use_yaml = str(provided_mapping_file).endswith('.yml') or str(provided_mapping_file).endswith('.yaml')
        
        self.patterns_file = Path(patterns_file)
        self.mapping = self.load_mapping()
        self.patterns = self.load_patterns()
    
    def load_mapping(self):
        """加载描述->分类映射"""
        if not self.mapping_file.exists():
            return {}
        
        if self.use_yaml:
            return self._load_yaml_mapping()
        else:
            with open(self.mapping_file) as f:
                return json.load(f)
    
    def _load_yaml_mapping(self):
        """从YAML文件加载映射"""
        mapping = {}
        current_category = None
        
        with open(self.mapping_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.rstrip()
                if not line:
                    continue
                
                if line.startswith('- ') and not line.startswith('  - '):
                    # This is a category line
                    current_category = line[2:].strip()
                elif line.startswith('  - ') and current_category:
                    # This is a description line, possibly with comment
                    description_part = line[4:].strip()
                    
                    # Check for comment (everything after #)
                    if ' # ' in description_part:
                        desc_with_quotes, comment = description_part.split(' # ', 1)
                        comment = comment.strip()
                    else:
                        desc_with_quotes = description_part
                        comment = ''
                    
                    # Remove quotes if present
                    if desc_with_quotes.startswith('"') and desc_with_quotes.endswith('"'):
                        description = desc_with_quotes[1:-1]
                    else:
                        description = desc_with_quotes
                    
                    # Store in new format if there's a comment, otherwise backward compatible
                    if comment:
                        mapping[description] = {
                            'category': current_category,
                            'comment': comment
                        }
                    else:
                        mapping[description] = current_category
        
        return mapping
    
    def load_patterns(self):
        """加载模式->分类映射"""
        if self.patterns_file.exists():
            with open(self.patterns_file) as f:
                return json.load(f)
        return {}
    
    def save_mapping(self):
        """保存映射到文件"""
        self.mapping_file.parent.mkdir(exist_ok=True)
        
        if self.use_yaml:
            self._save_yaml_mapping()
        else:
            with open(self.mapping_file, 'w') as f:
                json.dump(self.mapping, f, indent=2, ensure_ascii=False)
    
    def _save_yaml_mapping(self):
        """保存映射到YAML文件"""
        from collections import defaultdict
        
        # Group descriptions by category with comments
        categories = defaultdict(list)
        for description, mapping_value in self.mapping.items():
            if isinstance(mapping_value, dict):
                category = mapping_value['category']
                comment = mapping_value.get('comment', '')
                categories[category].append((description, comment))
            else:
                # Old format - convert to new format
                categories[mapping_value].append((description, ''))
        
        # Write to YAML file with comments
        with open(self.mapping_file, 'w', encoding='utf-8') as f:
            for category in sorted(categories.keys()):
                f.write(f'- {category}\n')
                for description, comment in sorted(categories[category], key=lambda x: x[0]):
                    # Escape quotes in descriptions
                    escaped_desc = description.replace('"', '\\"')
                    if comment:
                        f.write(f'  - "{escaped_desc}" # {comment}\n')
                    else:
                        f.write(f'  - "{escaped_desc}"\n')
    
    def save_patterns(self):
        """保存模式映射到文件"""
        self.patterns_file.parent.mkdir(exist_ok=True)
        with open(self.patterns_file, 'w') as f:
            json.dump(self.patterns, f, indent=2, ensure_ascii=False)
    
    def get_category(self, description):
        """获取描述对应的分类"""
        # 1. 直接匹配
        if description in self.mapping:
            mapping_value = self.mapping[description]
            # Handle both old format (string) and new format (dict)
            if isinstance(mapping_value, dict):
                return mapping_value['category']
            else:
                return mapping_value
        
        # 2. 模式匹配 (关键词/品牌名识别)
        category = self._match_patterns(description)
        if category:
            return category
        
        # 3. 改进的模糊匹配
        close_matches = difflib.get_close_matches(
            description, self.mapping.keys(), n=1, cutoff=0.6  # 降低阈值，提高匹配率
        )
        if close_matches:
            mapping_value = self.mapping[close_matches[0]]
            # Handle both old format (string) and new format (dict)
            if isinstance(mapping_value, dict):
                return mapping_value['category']
            else:
                return mapping_value
        
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
    
    def add_mapping(self, description, category, is_programmatic=False):
        """添加新的映射
        
        Args:
            description: 交易描述
            category: 分类
            is_programmatic: 是否为程序自动添加（非用户交互）
        """
        self.mapping[description] = {
            'category': category,
            'comment': 'UNCONFIRMED' if is_programmatic else ''
        }
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
        mapping_value = self.mapping.get(description)
        if isinstance(mapping_value, dict):
            return mapping_value['category']
        else:
            return mapping_value
