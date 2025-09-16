import datetime
import time
import requests
import csv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def fetch_szse_data(sec_code="159919", date="2025-09-09", max_retries=3):
    """
    获取深圳证券交易所股票交易数据
    """
    # 基础URL和参数
    base_url = "https://www.szse.cn/api/report/ShowReport/data"
    
    params = {
        "SHOWTYPE": "JSON",
        "CATALOGID": "1815_stock_snapshot",
        "TABKEY": "tab2",  # tab2表示基金，tab1表示股票
        "txtDMorJC": sec_code,
        "txtBeginDate": date,
        "txtEndDate": date,
        "archiveDate": "2023-09-01",  # 固定值
        "random": int(time.time() * 1000)  # 随机数防止缓存
    }
    
    # 请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.szse.cn/market/trend/index.html",
        "X-Request-Type": "ajax",
        "X-Requested-With": "XMLHttpRequest",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors"
    }
    
    # 配置重试会话
    session = requests.Session()
    session.trust_env = False
    
    retry = Retry(total=max_retries, backoff_factor=0.5, 
                 status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    
    try:
        # 发送请求
        response = session.get(base_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 深圳交易所返回标准JSON，无需JSONP处理
        return response.json()
        
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def is_json_complete(data):
    """
    判断深圳证券交易所JSON数据是否完整
    """
    if data is None:
        return "否"
    elif len(data) == 0:
        return "否"
    elif not data[0].get("data"):
        return "否"
    elif len(data[0].get("data", [])) == 0:
        return "否"
    else:
        return "是"

def save_to_csv(data, filename="szse_stock_data.csv"):
    """
    将深圳证券交易所数据保存到CSV文件
    """
    # 判断数据完整性
    completeness = is_json_complete(data)
    
    # 准备CSV行数据
    if data and len(data) > 0 and data[0].get("data") and len(data[0]["data"]) > 0:
        result = data[0]["data"][0]
        row = [
            result.get('zqjc', ''),
            result.get('zqdm', ''),
            result.get('jyrq', ''),
            result.get('qss', ''),
            result.get('ks', ''),
            result.get('zg', ''),
            result.get('zd', ''),
            result.get('ss', ''),
            result.get('sdf', ''),
            result.get('cjgs', ''),
            result.get('cjje', ''),
            completeness
        ]
    else:
        # 如果数据不完整，创建空行但仍包含完整性判断
        row = ['', '', '', '', '', '', '', '', '', '', '', completeness]
    
    # 写入CSV文件
    try:
        # 尝试打开文件以检查是否存在
        with open(filename, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            # 如果文件存在，则追加数据
            with open(filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
    except FileNotFoundError:
        # 如果文件不存在，创建文件并写入表头
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # 写入表头
            header = [
                "证券名称", "证券代码", "交易日期", "前收价", "开盘价", 
                "最高价", "最低价", "收盘价", "涨跌幅(%)", 
                "成交量(万份)", "成交额(万元)", "数据完整性"
            ]
            writer.writerow(header)
            writer.writerow(row)
            
    print(f"数据已保存到 {filename}")

def sz_fetch_and_save_data(codes, start_date, end_date):
    """
    主函数：获取并保存数据
    """
    # 统计网络请求成功和失败次数
    success_count = 0
    fail_count = 0
    
    # 设定每天递增的间隔（一天）
    delta = datetime.timedelta(days=1)
    
    for code in codes:
        # 为每个代码创建CSV文件
        csv_filename = f"{code}_SZ.csv"
        
        # 循环遍历日期
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            print(f"正在获取代码 {code} 日期 {date_str} 的数据...")
            
            # 获取数据
            try:
                data = fetch_szse_data(sec_code=code, date=date_str)
                
                # 如果fetch_szse_data返回None，表示请求失败
                if data is None:
                    # 保存空数据到CSV
                    save_to_csv(None, csv_filename)
                    fail_count += 1
                    print(f"代码 {code} 日期 {date_str} 请求失败")
                else:
                    # 保存数据到CSV
                    save_to_csv(data, csv_filename)
                    success_count += 1
                    print(f"代码 {code} 日期 {date_str} 请求成功")
                    
            except Exception as e:
                # 如果fetch_szse_data抛出异常，表示请求失败
                print(f"代码 {code} 日期 {date_str} 请求异常: {e}")
                # 保存空数据到CSV
                save_to_csv(None, csv_filename)
                fail_count += 1
            
            # 将当前日期增加一天
            current_date += delta
            
            # 单线程调用间隔5秒
            time.sleep(5)

    # 最终统计结果
    print(f"深圳所有任务完成！成功次数: {success_count}, 失败次数: {fail_count}")
    
    # 保存统计结果到文件
    with open("sz_success_count.txt", "w", encoding="utf-8") as f:
        f.write(f"成功次数: {success_count}")
    with open("sz_fail_count.txt", "w", encoding="utf-8") as f:
        f.write(f"失败次数: {fail_count}")
    
    return success_count, fail_count

# 如果直接运行此文件，则执行以下代码
if __name__ == "__main__":
    # 代码数组
    codes = ['159919']
    
    # 使用系统当前日期作为起始和结束日期
    current_date = datetime.date.today()
    start_date = current_date
    end_date = current_date
    
    # 调用函数获取数据
    success_count, fail_count = sz_fetch_and_save_data(codes, start_date, end_date)
    
    # 最终统计结果
    print(f"所有任务完成！成功次数: {success_count}, 失败次数: {fail_count}")