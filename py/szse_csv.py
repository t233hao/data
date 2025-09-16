import csv
import os

# 文件列表
files = ['512100_SH.csv','560010_SH.csv','159845_SZ.csv','159629_SZ.csv']

# 初始化字典存储每日总成交额
daily_total_amount = {}

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        
        # 获取交易日期和成交额的列索引
        try:
            date_index = header.index('交易日期')
            amount_index = header.index('成交额(万元)')
        except ValueError:
            print(f"在文件 {file} 中未找到所需的列标题")
            continue
        
        for row in reader:
            # 检查行是否有足够的列
            if len(row) <= max(date_index, amount_index):
                continue
                
            # 统一日期格式：去除连字符
            date_str = row[date_index].replace('-', '')
            
            # 处理成交额字符串：去除逗号和引号
            amount_str = row[amount_index].replace(',', '').replace('"', '').strip()
            
            # 跳过空字符串
            if not amount_str:
                continue
                
            try:
                amount_val = float(amount_str)
            except ValueError:
                print(f"无法将 '{amount_str}' 转换为浮点数，跳过此行")
                continue
            
            # 累加成交额
            if date_str not in daily_total_amount:
                daily_total_amount[date_str] = 0
            daily_total_amount[date_str] += amount_val

# 按日期排序输出
sorted_dates = sorted(daily_total_amount.keys())
print("按交易日期排序的总成交额(万元):")
for date in sorted_dates:
    print(f"日期: {date}, 总成交额: {daily_total_amount[date]:.2f}")
# 将结果写入CSV文件
filename = "中证1000ETF.csv"
try:
    # 尝试打开文件以检查是否存在
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        # 如果文件存在，则追加数据
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # 写入表头
            header = ["交易日期", "总成交额(万元)"]
            writer.writerow(header)
            for date in sorted_dates:
                row = [date, f"{daily_total_amount[date]:.2f}"]
                writer.writerow(row)
except FileNotFoundError:
    # 如果文件不存在，创建文件并写入表头
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # 写入表头
        header = ["交易日期", "总成交额(万元)"]
        writer.writerow(header)
        for date in sorted_dates:
            row = [date, f"{daily_total_amount[date]:.2f}"]
            writer.writerow(row)

print(f"数据已保存到 {filename}")