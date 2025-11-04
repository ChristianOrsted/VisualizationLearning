from flask import Flask, render_template, jsonify, request, redirect, url_for
import pymysql
import json
from contextlib import contextmanager

app = Flask(__name__)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'housing_price',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

@contextmanager
def get_db_connection():
    """使用上下文管理器获取数据库连接，确保连接正确关闭"""
    conn = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        yield conn
    except Exception as e:
        print(f"数据库连接错误: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def get_all_cities():
    """获取所有城市列表 - 从年度表获取"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = "SELECT DISTINCT city_name FROM yearly_price_for_all ORDER BY city_name"
                cursor.execute(query)
                results = cursor.fetchall()
                return [row['city_name'] for row in results]
    except Exception as e:
        print(f"获取城市列表错误: {e}")
        return []

def get_all_cities_monthly():
    """获取所有城市列表 - 从月度表获取"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = "SELECT DISTINCT city_name FROM monthly_price_for_all ORDER BY city_name"
                cursor.execute(query)
                results = cursor.fetchall()
                return [row['city_name'] for row in results]
    except Exception as e:
        print(f"获取城市列表错误: {e}")
        return []

def get_multi_city_data(cities):
    """获取多个城市的年度数据"""
    if not cities:
        return []
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                placeholders = ','.join(['%s'] * len(cities))
                query = f"""
                    SELECT city_name, year, price, change_rate 
                    FROM yearly_price_for_all 
                    WHERE city_name IN ({placeholders})
                    ORDER BY city_name, year
                """
                cursor.execute(query, cities)
                results = cursor.fetchall()
                return results
    except Exception as e:
        print(f"获取城市数据错误: {e}")
        return []

def get_multi_city_monthly_data(cities):
    """获取多个城市的月度数据"""
    if not cities:
        return []
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                placeholders = ','.join(['%s'] * len(cities))
                query = f"""
                    SELECT city_name, year, month, price 
                    FROM monthly_price_for_all 
                    WHERE city_name IN ({placeholders})
                    ORDER BY city_name, year, month
                """
                cursor.execute(query, cities)
                results = cursor.fetchall()
                return results
    except Exception as e:
        print(f"获取城市月度数据错误: {e}")
        return []

def get_multi_city_monthly_change_rate_data(cities):
    """获取多个城市的月度涨跌幅数据 - 基于月度价格计算环比"""
    if not cities:
        return []
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                placeholders = ','.join(['%s'] * len(cities))
                query = f"""
                    SELECT city_name, year, month, price 
                    FROM monthly_price_for_all 
                    WHERE city_name IN ({placeholders})
                    ORDER BY city_name, year, month
                """
                cursor.execute(query, cities)
                results = cursor.fetchall()
                
                # 计算环比涨跌幅
                city_data = {}
                for row in results:
                    city = row['city_name']
                    if city not in city_data:
                        city_data[city] = []
                    city_data[city].append(row)
                
                # 为每个城市计算环比涨跌幅
                change_rate_results = []
                for city, data in city_data.items():
                    for i in range(len(data)):
                        if i == 0:
                            # 第一个月没有环比数据
                            continue
                        
                        current_price = float(data[i]['price']) if data[i]['price'] else 0
                        previous_price = float(data[i-1]['price']) if data[i-1]['price'] else 0
                        
                        if previous_price > 0:
                            change_rate = ((current_price - previous_price) / previous_price) * 100
                        else:
                            change_rate = 0
                        
                        change_rate_results.append({
                            'city_name': city,
                            'year': data[i]['year'],
                            'month': data[i]['month'],
                            'change_rate': round(change_rate, 2)
                        })
                
                return change_rate_results
    except Exception as e:
        print(f"获取城市月度涨跌幅数据错误: {e}")
        return []
    
def get_ranking_race_data():
    """获取所有城市的月度房价数据用于动态排名"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT city_name, year, month, price 
                    FROM monthly_price_for_all 
                    ORDER BY year, month, city_name
                """
                cursor.execute(query)
                results = cursor.fetchall()
                return results
    except Exception as e:
        print(f"获取排名竞速数据错误: {e}")
        return []

# ============ 路由 ============

@app.route('/')
def index():
    """主页 - 重定向到价格对比页面"""
    return redirect(url_for('price_page'))

@app.route('/chart/price_compare')
def price_page():
    """价格对比页面"""
    cities = get_all_cities_monthly()
    return render_template('price.html', cities=cities, current_page='price_compare')

@app.route('/chart/monthly_change_rate_compare')
def monthly_change_rate_page():
    """月度涨跌幅对比页面"""
    cities = get_all_cities_monthly()
    return render_template('monthly_change_rate.html', cities=cities, current_page='change_rate_compare')

@app.route('/chart/yearly_change_rate_compare')
def yearly_change_rate_page():
    """涨跌幅对比页面"""
    cities = get_all_cities()
    return render_template('yearly_change_rate.html', cities=cities, current_page='change_rate_compare')

@app.route('/chart/ranking_race')
def ranking_race_page():
    """城市房价排名竞速页面"""
    cities = get_all_cities_monthly()
    return render_template('ranking_race.html', cities=cities, current_page='ranking_race')

@app.route('/map/price_map')
def price_map_page():
    """房价地图页面"""
    return render_template('price_map.html', current_page='price_map')

@app.route('/map/change_rate_map')
def change_rate_map_page():
    """涨跌幅地图页面"""
    return render_template('change_rate_map.html', current_page='change_rate_map')

# 兼容性重定向
@app.route('/price_compare')
def price_compare_redirect():
    return redirect(url_for('price_page'))

@app.route('/change_rate_compare')
def change_rate_compare_redirect():
    return redirect(url_for('change_rate_page'))

@app.route('/map_view')
def map_view_redirect():
    return redirect(url_for('price_map_page'))

# ============ API接口 ============

@app.route('/api/price_data', methods=['POST'])
def get_price_data():
    """获取房价月度数据API"""
    try:
        selected_cities = request.json.get('cities', [])
        
        if not selected_cities:
            return jsonify({
                'dates': [],
                'series': [],
                'tableData': [],
                'cities': []
            })
        
        selected_cities = selected_cities[:5]
        data = get_multi_city_monthly_data(selected_cities)
        
        if not data:
            return jsonify({
                'dates': [],
                'series': [],
                'tableData': [],
                'cities': selected_cities,
                'error': '未找到数据'
            })
        
        # 组织数据
        city_data = {}
        dates = set()
        
        for row in data:
            city = row['city_name']
            year = row['year']
            month = row['month']
            price = float(row['price']) if row['price'] is not None else 0
            
            # 创建日期字符串 "YYYY-MM"
            date_str = f"{year}-{month:02d}"
            dates.add(date_str)
            
            if city not in city_data:
                city_data[city] = {}
            city_data[city][date_str] = round(price, 2)
        
        # 排序日期
        dates = sorted(list(dates))
        
        # 构建图表数据
        series_data = []
        for city in selected_cities:
            prices = [city_data.get(city, {}).get(date, 0) for date in dates]
            series_data.append({
                'name': city,
                'type': 'line',
                'data': prices,
                'smooth': True,
                'symbol': 'circle',
                'symbolSize': 6
            })
        
        # 构建表格数据
        table_data = []
        for date in dates:
            row = {'date': date}
            for city in selected_cities:
                row[city] = city_data.get(city, {}).get(date, 0)
            table_data.append(row)
        
        return jsonify({
            'dates': dates,
            'series': series_data,
            'tableData': table_data,
            'cities': selected_cities,
            'success': True
        })
    
    except Exception as e:
        print(f"API错误 (price_data): {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'success': False,
            'dates': [],
            'series': [],
            'tableData': [],
            'cities': []
        }), 500

@app.route('/api/monthly_change_rate_data', methods=['POST'])
def get_monthly_change_rate_data():
    """获取涨跌幅月度数据API - 修改为月度环比"""
    try:
        selected_cities = request.json.get('cities', [])
        
        if not selected_cities:
            return jsonify({
                'dates': [],
                'series': [],
                'tableData': [],
                'cities': []
            })
        
        selected_cities = selected_cities[:5]
        data = get_multi_city_monthly_change_rate_data(selected_cities)
        
        if not data:
            return jsonify({
                'dates': [],
                'series': [],
                'tableData': [],
                'cities': selected_cities,
                'error': '未找到数据'
            })
        
        # 组织数据
        city_data = {}
        dates = set()
        
        for row in data:
            city = row['city_name']
            year = row['year']
            month = row['month']
            change_rate = float(row['change_rate']) if row['change_rate'] is not None else 0
            
            # 创建日期字符串 "YYYY-MM"
            date_str = f"{year}-{month:02d}"
            dates.add(date_str)
            
            if city not in city_data:
                city_data[city] = {}
            city_data[city][date_str] = round(change_rate, 2)
        
        # 排序日期
        dates = sorted(list(dates))
        
        # 构建图表数据
        series_data = []
        for city in selected_cities:
            rates = [city_data.get(city, {}).get(date, 0) for date in dates]
            series_data.append({
                'name': city,
                'type': 'line',
                'data': rates,
                'smooth': True,
                'symbol': 'circle',
                'symbolSize': 6,
                'areaStyle': {
                    'opacity': 0.3
                }
            })
        
        # 构建表格数据
        table_data = []
        for date in dates:
            row = {'date': date}
            for city in selected_cities:
                row[city] = city_data.get(city, {}).get(date, 0)
            table_data.append(row)
        
        return jsonify({
            'dates': dates,
            'series': series_data,
            'tableData': table_data,
            'cities': selected_cities,
            'success': True
        })
    
    except Exception as e:
        print(f"API错误 (change_rate_data): {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'success': False,
            'dates': [],
            'series': [],
            'tableData': [],
            'cities': []
        }), 500
    
@app.route('/api/yearly_change_rate_data', methods=['POST'])
def get_yearly_change_rate_data():
    """获取涨跌幅数据API"""
    try:
        selected_cities = request.json.get('cities', [])
        
        if not selected_cities:
            return jsonify({
                'years': [],
                'series': [],
                'tableData': [],
                'cities': []
            })
        
        selected_cities = selected_cities[:5]
        data = get_multi_city_data(selected_cities)
        
        if not data:
            return jsonify({
                'years': [],
                'series': [],
                'tableData': [],
                'cities': selected_cities,
                'error': '未找到数据'
            })
        
        # 组织数据
        city_data = {}
        years = set()
        
        for row in data:
            city = row['city_name']
            year = row['year']
            change_rate = float(row['change_rate']) if row['change_rate'] is not None else 0
            
            years.add(year)
            
            if city not in city_data:
                city_data[city] = {}
            city_data[city][year] = round(change_rate, 2)
        
        years = sorted(list(years))
        
        # 构建图表数据
        series_data = []
        for city in selected_cities:
            rates = [city_data.get(city, {}).get(year, 0) for year in years]
            series_data.append({
                'name': city,
                'type': 'line',
                'data': rates,
                'smooth': True,
                'symbol': 'circle',
                'symbolSize': 6,
                'areaStyle': {
                    'opacity': 0.3
                }
            })
        
        # 构建表格数据
        table_data = []
        for year in years:
            row = {'year': year}
            for city in selected_cities:
                row[city] = city_data.get(city, {}).get(year, 0)
            table_data.append(row)
        
        return jsonify({
            'years': years,
            'series': series_data,
            'tableData': table_data,
            'cities': selected_cities,
            'success': True
        })
    
    except Exception as e:
        print(f"API错误 (change_rate_data): {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'success': False,
            'years': [],
            'series': [],
            'tableData': [],
            'cities': []
        }), 500

@app.route('/api/ranking_race_data')
def get_ranking_race_api():
    """获取排名竞速数据API"""
    try:
        raw_data = get_ranking_race_data()
        
        if not raw_data:
            return jsonify({
                'success': False,
                'message': '未找到数据'
            })
        
        # 按时间段分组数据
        time_data = {}
        time_points = set()
        
        for row in raw_data:
            time_key = f"{row['year']}-{str(row['month']).zfill(2)}"
            time_points.add(time_key)
            
            if time_key not in time_data:
                time_data[time_key] = []
            
            price = float(row['price']) if row['price'] and row['price'] != '' else 0
            
            # 确保价格有效
            if price > 0:
                time_data[time_key].append({
                    'city': row['city_name'],
                    'city_en': row['city_name'],  # 如果没有英文名，使用中文名
                    'price': price
                })
        
        # 对每个时间段的数据按价格排序
        for time_key in time_data:
            time_data[time_key].sort(key=lambda x: x['price'], reverse=True)
        
        # 获取所有时间点（排序）
        time_points = sorted(list(time_points))
        
        # 检查数据是否为空
        if not time_points:
            return jsonify({
                'success': False,
                'message': '没有有效的数据'
            })
        
        return jsonify({
            'success': True,
            'timePoints': time_points,
            'data': time_data
        })
        
    except Exception as e:
        print(f"获取排名竞速数据API错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/map_data', methods=['GET'])
def get_map_data():
    """获取地图数据API - 获取所有城市的最新房价"""
    try:
        year = request.args.get('year', type=int)
        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                if not year:
                    cursor.execute("SELECT MAX(year) as max_year FROM yearly_price_for_all")
                    result = cursor.fetchone()
                    year = result['max_year']
                
                query = """
                    SELECT city_name, price, change_rate 
                    FROM yearly_price_for_all 
                    WHERE year = %s AND price IS NOT NULL
                    ORDER BY price DESC
                """
                cursor.execute(query, (year,))
                results = cursor.fetchall()
                
                cursor.execute("SELECT DISTINCT year FROM yearly_price_for_all ORDER BY year")
                years = [row['year'] for row in cursor.fetchall()]
                
                map_data = []
                for row in results:
                    map_data.append({
                        'name': row['city_name'],
                        'value': round(float(row['price']), 2) if row['price'] else 0,
                        'changeRate': round(float(row['change_rate']), 2) if row['change_rate'] else 0
                    })
                
                return jsonify({
                    'success': True,
                    'year': year,
                    'years': years,
                    'data': map_data
                })
    
    except Exception as e:
        print(f"API错误 (map_data): {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/change_rate_map_data', methods=['GET'])
def get_change_rate_map_data():
    """获取涨跌幅地图数据API"""
    try:
        year = request.args.get('year', type=int)
        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                if not year:
                    cursor.execute("SELECT MAX(year) as max_year FROM yearly_price_for_all")
                    result = cursor.fetchone()
                    year = result['max_year']
                
                query = """
                    SELECT city_name, price, change_rate 
                    FROM yearly_price_for_all 
                    WHERE year = %s AND change_rate IS NOT NULL
                    ORDER BY change_rate DESC
                """
                cursor.execute(query, (year,))
                results = cursor.fetchall()
                
                cursor.execute("SELECT DISTINCT year FROM yearly_price_for_all ORDER BY year")
                years = [row['year'] for row in cursor.fetchall()]
                
                map_data = []
                for row in results:
                    map_data.append({
                        'name': row['city_name'],
                        'value': round(float(row['change_rate']), 2) if row['change_rate'] else 0,
                        'price': round(float(row['price']), 2) if row['price'] else 0
                    })
                
                return jsonify({
                    'success': True,
                    'year': year,
                    'years': years,
                    'data': map_data
                })
    
    except Exception as e:
        print(f"API错误 (change_rate_map_data): {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

if __name__ == '__main__':
    # 测试数据库连接
    try:
        with get_db_connection() as conn:
            print("✅ 数据库连接成功！")
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(DISTINCT city_name) as count FROM yearly_price_for_all")
                result = cursor.fetchone()
                print(f"✅ 年度数据表找到 {result['count']} 个城市")
                
                cursor.execute("SELECT COUNT(DISTINCT city_name) as count FROM monthly_price_for_all")
                result = cursor.fetchone()
                print(f"✅ 月度数据表找到 {result['count']} 个城市")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print("请检查数据库配置是否正确")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
