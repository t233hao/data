import csv

# 初始化计数器
count = 0

# 请将 'your_file.csv' 替换为您的实际文件路径
with open('510300.csv', 'r', encoding='utf-8') as csvfile:
    # 创建CSV读取器
    csv_reader = csv.DictReader(csvfile)
    
    # 遍历每一行数据
    for row in csv_reader:
        # 检查“数据完整性”列的值是否为“是”
        if row.get('数据完整性') == '是':
            count += 1

# 打印结果
print(f"数据完整性为‘是’的次数是：{count}")