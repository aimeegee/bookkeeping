#!/usr/bin/env python3
import argparse
from pathlib import Path
from src.data_processor import DataProcessor
from src.category_manager import CategoryManager
from src.interactive_cli import InteractiveCLI

def main():
    parser = argparse.ArgumentParser(description='Bank Transaction Merger and Categorizer')
    parser.add_argument('--input-dir', default='data/input', help='Input directory')
    parser.add_argument('--output-dir', default='data/output', help='Output directory')
    parser.add_argument('--no-interactive', action='store_true', help='Skip interactive categorization')
    
    args = parser.parse_args()
    
    # 初始化组件
    processor = DataProcessor()
    category_manager = CategoryManager()
    cli = InteractiveCLI(category_manager)
    
    try:
        # 1. 合并所有银行文件，按月分组
        print("Merging bank transaction files...")
        monthly_data = processor.merge_files(args.input_dir)
        
        total_transactions = sum(len(df) for df in monthly_data.values())
        total_banks = len(set(bank for df in monthly_data.values() for bank in df['bank'].unique()))
        print(f"Processed {total_transactions} transactions from {total_banks} banks across {len(monthly_data)} months")
        
        # 2. 处理每个月的数据
        all_processed_data = {}
        for month, df in monthly_data.items():
            print(f"\nProcessing month {month}...")
            
            # 应用已有分类
            df = category_manager.apply_categories(df)
            
            # 交互式分类更新
            if not args.no_interactive:
                df = cli.update_categories(df, month)
            
            all_processed_data[month] = df
        
        # 3. 保存每月的结果文件
        print(f"\nSaving monthly files...")
        saved_files = processor.save_monthly_files(all_processed_data, args.output_dir)
        
        # 4. 显示总体统计信息
        print(f"\nSummary:")
        print(f"Total transactions: {total_transactions}")
        print(f"Months processed: {len(monthly_data)}")
        print(f"Files saved: {len(saved_files)}")
        
        for month, df in all_processed_data.items():
            categorized = df['comment'].notna().sum()
            total = len(df)
            amount_sum = df['amount'].sum()
            print(f"  {month}: {total} transactions, ${amount_sum:.2f}, {categorized}/{total} categorized")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
