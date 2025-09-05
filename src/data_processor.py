import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import re

class DataProcessor:
    def __init__(self, config_path="config/bank_config.json"):
        with open(config_path) as f:
            self.bank_config = json.load(f)
    
    def parse_filename(self, filename):
        """解析文件名获取月份和银行名"""
        pattern = r'(\d{4}-\d{2})-(.+)\.(csv|xlsx)$'
        match = re.match(pattern, filename)
        if match:
            month, bank_name = match.groups()[:2]
            return month, bank_name.lower()
        raise ValueError(f"Invalid filename format: {filename}")
    
    def load_and_process_file(self, file_path):
        """加载并处理单个银行文件"""
        filename = Path(file_path).name
        month, bank_code = self.parse_filename(filename)
        
        # 读取文件
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # 标准化列名
        df.columns = df.columns.str.lower()
        required_cols = ['date', 'description', 'amount']
        
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"Missing required columns in {filename}")
        
        # 处理日期
        bank_info = self.bank_config.get(bank_code, {})
        date_format = bank_info.get('date_format', '%Y-%m-%d')
        df['date'] = pd.to_datetime(df['date'], format=date_format)
        
        # 处理金额符号
        if bank_info.get('revert_amount', False):
            df['amount'] = -df['amount']
        
        # 添加银行标识
        df['bank'] = bank_info.get('name', bank_code.upper())
        df['month'] = month
        
        return df[['date', 'description', 'amount', 'bank', 'month']]
    
    def merge_files(self, input_dir="data/input"):
        """合并所有银行文件"""
        input_path = Path(input_dir)
        all_data = []
        
        for file_path in input_path.glob("*.csv"):
            try:
                df = self.load_and_process_file(str(file_path))
                all_data.append(df)
                print(f"Processed: {file_path.name}")
            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")
        
        for file_path in input_path.glob("*.xlsx"):
            try:
                df = self.load_and_process_file(str(file_path))
                all_data.append(df)
                print(f"Processed: {file_path.name}")
            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")
        
        if not all_data:
            raise ValueError("No valid files found to process")
        
        # 合并并排序
        merged_df = pd.concat(all_data, ignore_index=True)
        merged_df = merged_df.sort_values('date').reset_index(drop=True)
        
        return merged_df
