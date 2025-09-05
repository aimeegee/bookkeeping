#!/usr/bin/env python3
import argparse
from pathlib import Path
from src.data_processor import DataProcessor
from src.category_manager import CategoryManager
from src.interactive_cli import InteractiveCLI

def main():
    parser = argparse.ArgumentParser(description='Bank Transaction Merger and Categorizer')
    parser.add_argument('--input-dir', default='data/input', help='Input directory')
    parser.add_argument('--output-file', default='data/output/merged_transactions.csv', help='Output file')
    parser.add_argument('--no-interactive', action='store_true', help='Skip interactive categorization')
    
    args = parser.parse_args()
    
    # 初始化组件
    processor = DataProcessor()
    category_manager = CategoryManager()
    cli = InteractiveCLI(category_manager)
    
    try:
        # 1. 合并所有银行文件
        print("Merging bank transaction files...")
        merged_df = processor.merge_files(args.input_dir)
        print(f"Merged {len(merged_df)} transactions from {merged_df['bank'].nunique()} banks")
        
        # 2. 应用已有分类
        print("Applying existing categories...")
        merged_df = category_manager.apply_categories(merged_df)
        
        # 3. 交互式分类更新
        if not args.no_interactive:
            print("Starting interactive categorization...")
            merged_df = cli.update_categories(merged_df)
        
        # 4. 保存结果
        output_path = Path(args.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        merged_df.to_csv(output_path, index=False)
        print(f"Results saved to: {output_path}")
        
        # 5. 显示统计信息
        print(f"\nSummary:")
        print(f"Total transactions: {len(merged_df)}")
        print(f"Date range: {merged_df['date'].min()} to {merged_df['date'].max()}")
        print(f"Total amount: ${merged_df['amount'].sum():.2f}")
        print(f"Categorized: {merged_df['comment'].notna().sum()}/{len(merged_df)}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
