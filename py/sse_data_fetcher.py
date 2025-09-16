import datetime
import time
import requests
import json
import csv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def fetch_sse_data(sec_code="510300", date=None, max_retries=3):
    """
    获取上海证券交易所股票交易数据
    """
    if date is None:
        date = datetime.date.today().strftime('%Y-%m-%d')
    
    # 基础URL和参数
    base_url = "https://query.sse.com.cn/commonQuery.do"
    callback_id = f"jsonpCallback{int(time.time() * 1000) % 100000000}"
    
    params = {
        "jsonCallBack": callback_id,
        "sqlId": "COMMON_SSE_CP_GPJCTPZ_GPLB_CJGK_MRGK_C",
        "SEC_CODE": sec_code,
        "TX_DATE": date.replace("-", ""),
        "_": int(time.time() * 1000)
    }
    
    # 请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.sse.com.cn/"
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
        
        # 处理JSONP响应
        text = response.text
        json_str = text[text.find('(')+1:text.rfind(')')]
        return json.loads(json_str)
        
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def is_json_complete(data):
    """
    判断JSON数据是否完整
    """
    if data is None:
        return "否"
    elif len(data.get("result", [])) == 0:
        return "否"
    elif not data.get("result"):
        return "否"
    else:
        return "是"

def save_to_csv(data, filename="stock_data.csv"):
    """
    将数据保存到CSV文件
    """
    # 判断数据完整性
    completeness = is_json_complete(data)
    
    # 准备CSV行数据
    if data and data.get("result"):
        result = data["result"][0]
        row = [
            result.get('SEC_NAME', ''),
            result.get('SEC_CODE', ''),
            result.get('TX_DATE', ''),
            result.get('CLOSE_PRICE', ''),
            result.get('CHANGE_RATE', ''),
            result.get('HIGH_PRICE', ''),
            result.get('LOW_PRICE', ''),
            result.get('TRADE_VOL', ''),
            result.get('TRADE_AMT', ''),
            completeness
        ]
    else:
        # 如果数据不完整，创建空行但仍包含完整性判断
        row = ['', '', '', '', '', '', '', '', '', completeness]
    
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
                "证券名称", "证券代码", "交易日期", "收盘价", "涨跌幅(%)", 
                "最高价", "最低价", "成交量(万份)", "成交额(万元)", "数据完整性"
            ]
            writer.writerow(header)
            writer.writerow(row)
    
    print(f"数据已保存到 {filename}")

def sh_fetch_and_save_data(codes, start_date=None, end_date=None):
    """
    获取并保存多个代码的数据
    """
    if start_date is None:
        start_date = datetime.date.today()
    if end_date is None:
        end_date = datetime.date.today()
    
    # 设定每天递增的间隔（一天）
    delta = datetime.timedelta(days=1)
    
    # 统计网络请求成功和失败次数
    success_count = 0
    fail_count = 0
    
    for code in codes:
        # 为每个代码创建CSV文件
        csv_filename = f"{code}_SH.csv"
        
        # 循环遍历日期
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            print(f"正在获取代码 {code} 日期 {date_str} 的数据...")
            
            # 获取数据
            try:
                data = fetch_sse_data(sec_code=code, date=date_str)
                
                # 如果fetch_sse_data返回None，表示请求失败
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
                # 如果fetch_sse_data抛出异常，表示请求失败
                print(f"代码 {code} 日期 {date_str} 请求异常: {e}")
                # 保存空数据到CSV
                save_to_csv(None, csv_filename)
                fail_count += 1
            
            # 将当前日期增加一天
            current_date += delta
            
            # 单线程调用间隔5秒
            time.sleep(5)
    
    # 最终统计结果
    print(f"上证所有任务完成！成功次数: {success_count}, 失败次数: {fail_count}")
    
    # 保存统计结果到文件
    with open("sh_success_count.txt", "w", encoding="utf-8") as f:
        f.write(f"成功次数: {success_count}")
    with open("sh_fail_count.txt", "w", encoding="utf-8") as f:
        f.write(f"失败次数: {fail_count}")
    
    return success_count, fail_count