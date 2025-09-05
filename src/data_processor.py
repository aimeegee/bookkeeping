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
        # Support format: <bank>-<YYYYMM>.csv (e.g., "amex-202408.csv")
        
        pattern = r'(.+)-(\d{6})\.csv$'
        match = re.match(pattern, filename)
        if match:
            bank_name, yyyymm = match.groups()[:2]
            # Convert YYYYMM to YYYY-MM format for internal processing
            year = yyyymm[:4]
            month = yyyymm[4:6]
            month_formatted = f"{year}-{month}"
            return month_formatted, bank_name.lower()
            
        raise ValueError(f"Invalid filename format: {filename}. Expected <bank>-<YYYYMM>.csv (e.g., amex-202408.csv)")
    
    def load_and_process_file(self, file_path):
        """加载并处理单个银行文件"""
        filename = Path(file_path).name
        month, bank_code = self.parse_filename(filename)
        
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
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
        
        # Process CSV files only
        for file_path in input_path.glob("*.csv"):
            try:
                df = self.load_and_process_file(str(file_path))
                all_data.append(df)
                print(f"Processed: {file_path.name}")
            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")
        
        if not all_data:
            raise ValueError("No valid CSV files found to process")
        
        # 合并并排序
        merged_df = pd.concat(all_data, ignore_index=True)
        merged_df = merged_df.sort_values('date').reset_index(drop=True)
        
        # 按月份分组
        monthly_data = {}
        for month, group in merged_df.groupby('month'):
            # 转换月份格式从 YYYY-MM 到 YYYYMM
            month_key = month.replace('-', '')
            monthly_data[month_key] = group.reset_index(drop=True)
        
        return monthly_data
    
    def save_monthly_files(self, monthly_data, output_dir="data/output"):
        """保存按月分组的数据到单独文件"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        for month, df in monthly_data.items():
            # 重新排序列：date, description, amount, comment, bank (移除month)
            df_output = df.copy()
            
            # 确保comment列存在
            if 'comment' not in df_output.columns:
                df_output['comment'] = ''
            
            # 重新排序列，移除month，bank放到最后
            column_order = ['date', 'description', 'amount', 'comment', 'bank']
            df_output = df_output[column_order]
            
            filename = f"{month}.csv"
            file_path = output_path / filename
            df_output.to_csv(file_path, index=False)
            saved_files.append(str(file_path))
            print(f"Saved {len(df_output)} transactions to: {filename}")
        
        return saved_files
