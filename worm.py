# 爬虫文件，爬取相对应的信息
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os

def get_house_price(city_code, city_name, year):
    """
    获取指定城市和年份的二手房价格数据
    
    Args:
        city_code: 城市代号，如 'sh' (上海)
        city_name: 城市名称，如 'Shanghai'
        year: 年份，如 2015
    
    Returns:
        list: 包含 (city_name, year, month, price) 的元组列表
    """
    url = f"https://fangjia.gotohui.com/years/{city_code}/{year}/"
    
    try:
        # 发送请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"⚠️  {city_name} {year}年 - 请求失败，状态码: {response.status_code}")
            return []
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='ntable')
        
        if not table:
            # 尝试查找任意包含数据的表格
            table = soup.find('table')
        
        if not table:
            print(f"⚠️  {city_name} {year}年 - 未找到表格")
            return []
        
        # 提取数据
        data = []
        rows = table.find_all('tr')
        
        for row in rows[1:]:  # 跳过表头
            cells = row.find_all('td')
            if len(cells) >= 2:
                # 提取月份
                month_text = cells[0].get_text(strip=True)
                month_match = re.search(r'(\d+)月?', month_text)
                
                # 提取二手房价格（第二列）
                price_text = cells[1].get_text(strip=True)
                price_match = re.search(r'(\d+)', price_text)
                
                if month_match and price_match:
                    month = int(month_match.group(1))
                    price = int(price_match.group(1))
                    data.append((city_name, year, month, price))
        
        # 按月份排序
        data.sort(key=lambda x: x[2])
        
        print(f"✅ {city_name} {year}年 - 成功获取 {len(data)} 条数据")
        return data
        
    except Exception as e:
        print(f"❌ {city_name} {year}年 - 错误: {str(e)}")
        return []


def crawl_city_data(city_code, city_name, start_year=2015, end_year=2024):
    """
    爬取指定城市从start_year到end_year的所有房价数据
    
    Args:
        city_code: 城市代号
        city_name: 城市名称
        start_year: 起始年份
        end_year: 结束年份
    
    Returns:
        DataFrame: 包含所有数据的DataFrame
    """
    all_data = []
    
    print(f"\n开始爬取 {city_name} ({city_code}) 的房价数据...")
    print(f"年份范围: {start_year} - {end_year}")
    print("-" * 50)
    
    for year in range(start_year, end_year + 1):
        data = get_house_price(city_code, city_name, year)
        all_data.extend(data)
        
        # 添加延时，避免请求过快
        time.sleep(1)
    
    # 创建DataFrame
    df = pd.DataFrame(all_data, columns=['city_name', 'year', 'month', 'price'])
    
    print("-" * 50)
    print(f"✅ 完成！共获取 {len(df)} 条数据")
    
    return df


def crawl_multiple_cities(cities_dict, start_year=2015, end_year=2024, output_dir='./data'):
    """
    爬取多个城市的房价数据
    
    Args:
        cities_dict: 字典，格式为 {'城市代号': '城市名称'}
        start_year: 起始年份
        end_year: 结束年份
        output_dir: 输出目录
    
    Returns:
        DataFrame: 包含所有城市数据的DataFrame
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    all_cities_data = []
    
    for city_code, city_name in cities_dict.items():
        df = crawl_city_data(city_code, city_name, start_year, end_year)
        all_cities_data.append(df)
        
        # 保存单个城市的数据
        filename = f"{city_name.lower()}_house_price.csv"
        filepath = os.path.join(output_dir, filename)
        df.to_csv(filepath, index=False, header=False, encoding='utf-8-sig')
        print(f"💾 {city_name} 数据已保存到: {filepath}\n")
        
        time.sleep(1)
    
    # 合并所有城市数据
    final_df = pd.concat(all_cities_data, ignore_index=True)
    return final_df


if __name__ == "__main__":

    # 方式1: 爬取单个城市
    print("=" * 60)
    print("方式1: 爬取单个城市")
    print("=" * 60)
    
    city_code = '108'
    city_name = "Nanning"
    
    df_city = crawl_city_data(
        city_code=city_code,
        city_name=city_name,
        start_year=2015,
        end_year=2024
    )
    
    # 自动创建data目录（如果不存在）
    os.makedirs('./data', exist_ok=True)
    
    # 根据城市名称自动生成文件名（转小写）
    filename = f"{city_name.lower()}_house_price.csv"
    filepath = f"C:/Users/ChristianOrsted/Desktop/csv_data/{filename}"
    
    df_city.to_csv(filepath, index=False, header=False, encoding='utf-8-sig')
    print(f"\n💾 数据已保存到: {filepath}")
    
    # 显示前几行
    print("\n数据预览：")
    print(df_city.head(12))
    
    
    # 方式2: 批量爬取多个城市（自动保存每个城市的CSV）
    # 取消下面注释可以爬取多个城市
    """
    print("\n" + "=" * 60)
    print("方式2: 批量爬取多个城市")
    print("=" * 60)
    
    cities = {
        '2': 'Shanghai',       # 上海
        '1': 'Beijing',        # 北京
        '3': 'Guangzhou',      # 广州
        '49': 'Shenzhen',      # 深圳
        '6': 'Hangzhou',       # 杭州
        '7': 'Nanjing',        # 南京
        # 添加更多城市...
    }
    
    df_all = crawl_multiple_cities(cities, start_year=2015, end_year=2024, output_dir='./data')
    
    # 保存合并后的所有城市数据
    df_all.to_csv('./data/all_cities_house_price.csv', index=False, header=False, encoding='utf-8-sig')
    print(f"\n💾 所有城市合并数据已保存到: ./data/all_cities_house_price.csv")
    
    # 显示统计信息
    print("\n📊 数据统计：")
    print(df_all.groupby('city_name').size())
    """
