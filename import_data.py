import pandas as pd
from sqlalchemy import create_engine

# 1. 读取CSV文件
csv_file_path = r'D:\\Code\\Python\\VSCode\\VisualizationLearning\\data\\monthly_price.csv'
df = pd.read_csv(csv_file_path)

# 2. 创建数据库连接
# 格式：mysql+pymysql://用户名:密码@主机:端口/数据库名
engine = create_engine('mysql+pymysql://root:123456@localhost:3306/housing_price')

# 3. 导入数据到数据库
# if_exists参数：'replace'(替换), 'append'(追加), 'fail'(存在则报错)
table_name = 'monthly_price_for_all'
df.to_sql(table_name, engine, if_exists='replace', index=False)

print(f"Data has been seccessfullu imported to table {table_name} !")