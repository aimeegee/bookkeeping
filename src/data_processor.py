import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import re
import requests
from urllib.parse import urlparse

class DataProcessor:
    def __init__(self, config_path="config/bank_config.json"):
        with open(config_path) as f:
            self.bank_config = json.load(f)
    
    def parse_filename(self, filename):
        """解析文件名获取月份和银行名"""
        # Support format: <bank>-<YYYYMM>.csv (e.g., "amex-202408.csv")
        
        pattern = r'(.+)-(\d{6})\.(csv|xlsx)$'
        match = re.match(pattern, filename)
        if match:
            bank_name, yyyymm = match.groups()[:2]
            # Convert YYYYMM to YYYY-MM format for internal processing
            year = yyyymm[:4]
            month = yyyymm[4:6]
            month_formatted = f"{year}-{month}"
            return month_formatted, bank_name.lower()
            
        raise ValueError(f"Invalid filename format: {filename}. Expected <bank>-<YYYYMM>.csv (e.g., amex-202408.csv)")
    
    def load_and_process_file(self, file_path, filename_override=None):
        """加载并处理单个银行文件"""
        if filename_override:
            filename = filename_override
        else:
            filename = Path(file_path).name
            
        month, bank_code = self.parse_filename(filename)
        
        # 读取文件 - 支持 CSV, Excel, 和 Google Sheets URL
        if file_path.startswith('http'):
            # Google Sheets URL support
            df = self._load_google_sheets(file_path)
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
        
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

    def _load_google_sheets(self, url):
        """从Google Sheets URL加载数据"""
        # Convert Google Sheets URL to CSV export URL
        if 'docs.google.com/spreadsheets' in url:
            if '/edit' in url:
                sheet_id = url.split('/d/')[1].split('/')[0]
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
            else:
                csv_url = url
        else:
            csv_url = url
        
        try:
            response = requests.get(csv_url)
            response.raise_for_status()
            
            # Use StringIO to read CSV data from the response
            from io import StringIO
            df = pd.read_csv(StringIO(response.text))
            return df
        except Exception as e:
            raise ValueError(f"Failed to load Google Sheets from {url}: {e}")
    
    def merge_files(self, input_dir="data/input", google_sheets_urls=None):
        """合并所有银行文件"""
        input_path = Path(input_dir)
        all_data = []
        
        # Process local files
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
        
        # Process Google Sheets URLs if provided
        if google_sheets_urls:
            for url_info in google_sheets_urls:
                try:
                    # url_info should be like {"url": "...", "filename": "08amex.csv"}
                    url = url_info.get('url')
                    filename = url_info.get('filename')
                    if not filename:
                        # Try to extract filename from URL or use a default
                        filename = "google_sheet.csv"
                    
                    # Load and process the Google Sheets data
                    df = self.load_and_process_file(url, filename_override=filename)
                    all_data.append(df)
                    print(f"Processed Google Sheet: {filename}")
                except Exception as e:
                    print(f"Error processing Google Sheet {url_info}: {e}")
        
        if not all_data:
            raise ValueError("No valid files found to process")
        
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
            filename = f"{month}.csv"
            file_path = output_path / filename
            df.to_csv(file_path, index=False)
            saved_files.append(str(file_path))
            print(f"Saved {len(df)} transactions to: {filename}")
        
        return saved_files
