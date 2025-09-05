#!/usr/bin/env python3
import argparse
from pathlib import Path
from src.data_processor import DataProcessor
from src.category_manager import CategoryManager
from src.interactive_cli import InteractiveCLI
from src.learning_mode import LearningMode

def main():
    parser = argparse.ArgumentParser(description='Bank Transaction Merger and Categorizer')
    parser.add_argument('--input-dir', default='data/input', help='Input directory')
    parser.add_argument('--output-dir', default='data/output', help='Output directory')
    parser.add_argument('--no-interactive', action='store_true', help='Skip interactive categorization')
    parser.add_argument('--month', help='Process specific month only (format: YYYYMM, e.g., 202408)')
    parser.add_argument('--list-months', action='store_true', help='List available months from input files')
    parser.add_argument('--learn-from', help='Learn categories from an existing CSV file (same format as output)')
    
    args = parser.parse_args()
    
    # 初始化组件
    processor = DataProcessor()
    category_manager = CategoryManager()
    cli = InteractiveCLI(category_manager)
    learning_mode = LearningMode(category_manager)
    
    # 如果是学习模式
    if args.learn_from:
        if not Path(args.learn_from).exists():
            print(f"Error: Learning file '{args.learn_from}' not found")
            return 1
        
        print(f"Learning mode: Processing '{args.learn_from}'")
        success = learning_mode.learn_from_csv(args.learn_from)
        return 0 if success else 1
    
    args = parser.parse_args()
    
    # 初始化组件
    processor = DataProcessor()
    category_manager = CategoryManager()
    cli = InteractiveCLI(category_manager)
    
    try:
        # 1. 合并所有银行文件，按月分组
        print("Merging bank transaction files...")
        monthly_data = processor.merge_files(args.input_dir)
        
        # 如果用户想列出可用月份
        if args.list_months:
            print("\nAvailable months:")
            for month in sorted(monthly_data.keys()):
                count = len(monthly_data[month])
                banks = monthly_data[month]['bank'].unique()
                print(f"  {month}: {count} transactions from {', '.join(banks)}")
            return 0
        
        # 如果用户指定了特定月份
        if args.month:
            if args.month not in monthly_data:
                print(f"Month {args.month} not found in input files.")
                print("Available months:", ", ".join(sorted(monthly_data.keys())))
                return 1
            # 只处理指定的月份
            monthly_data = {args.month: monthly_data[args.month]}
            print(f"Processing only month: {args.month}")
        
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
