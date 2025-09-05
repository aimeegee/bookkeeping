import pandas as pd
from pathlib import Path

class BankParser:
    """银行特定的数据解析器"""
    
    @staticmethod
    def parse_cba(file_path):
        """解析CBA银行流水"""
        df = pd.read_csv(file_path)
        # CBA特定的列名映射
        column_mapping = {
            'Date': 'date',
            'Description': 'description', 
            'Amount': 'amount'
        }
        df = df.rename(columns=column_mapping)
        return df
    
    @staticmethod
    def parse_anz(file_path):
        """解析ANZ银行流水"""
        df = pd.read_csv(file_path)
        # ANZ特定的列名映射
        column_mapping = {
            'Transaction Date': 'date',
            'Narrative': 'description',
            'Debit': 'debit',
            'Credit': 'credit'
        }
        df = df.rename(columns=column_mapping)
        
        # 合并借贷列为amount
        df['amount'] = df['credit'].fillna(0) - df['debit'].fillna(0)
        df = df.drop(['debit', 'credit'], axis=1)
        
        return df
    
    @staticmethod
    def parse_westpac(file_path):
        """解析Westpac银行流水"""
        df = pd.read_csv(file_path)
        # Westpac特定的列名映射
        column_mapping = {
            'Date': 'date',
            'Memo': 'description',
            'Amount': 'amount'
        }
        df = df.rename(columns=column_mapping)
        return df
