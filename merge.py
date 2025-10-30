
import os
import glob

def merge_csv_files(input_dir, output_file):
    """
    直接追加合并所有CSV文件
    
    Args:
        input_dir: 输入目录路径
        output_file: 输出文件路径
    """
    print(f"正在合并 {input_dir} 下的所有CSV文件...")
    print("-" * 60)
    
    # 获取所有CSV文件
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))
    
    if not csv_files:
        print("❌ 未找到CSV文件！")
        return
    
    print(f"找到 {len(csv_files)} 个CSV文件：")
    for file in csv_files:
        print(f"  📄 {os.path.basename(file)}")
    
    print("\n开始合并...")
    print("-" * 60)
    
    # 合并文件
    total_lines = 0
    with open(output_file, 'w', encoding='utf-8-sig') as outfile:
        for i, file in enumerate(csv_files, 1):
            with open(file, 'r', encoding='utf-8-sig') as infile:
                content = infile.read()
                outfile.write(content)
                
                # 统计行数
                lines = content.count('\n')
                total_lines += lines
                
                print(f"✅ [{i}/{len(csv_files)}] {os.path.basename(file):30s} - {lines:4d} 行")
    
    print("-" * 60)
    print(f"✅ 合并完成！")
    print(f"   📊 总行数: {total_lines}")
    print(f"   💾 输出文件: {output_file}")
    print(f"   📁 文件大小: {os.path.getsize(output_file) / 1024:.2f} KB")


if __name__ == "__main__":
    input_directory = r"C:\\Users\\ChristianOrsted\\Desktop\\csv_data"
    output_filepath = "./data/monthly_price.csv"
    
    print("=" * 60)
    print("CSV文件批量合并工具")
    print("=" * 60)
    print()
    
    merge_csv_files(input_directory, output_filepath)
    
    print("\n🎉 完成！可以打开 monthly_price.csv 查看结果")