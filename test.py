import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path

# 获取当前脚本所在目录
script_dir = Path(__file__).parent

# 构建相对路径
file_name = 'long_format_yearly_price.csv'
csv_file_path = script_dir / 'data' / file_name

print(csv_file_path)