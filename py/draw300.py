import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# 设置中文字体支持SimHei
#plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
#plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

# 读取CSV文件
df = pd.read_csv('沪深300ETF.csv')

# 转换日期格式
df['交易日期'] = pd.to_datetime(df['交易日期'], format='%Y%m%d')

# 将成交额从万元转换为十亿元（除以100000）
df['成交量(十亿元)'] = df['总成交额(万元)'] / 100000

# 计算日均成交量
# average_volume = df['成交量(十亿元)'].mean()
average_volume = 11.8

# 创建紧凑的图表
plt.figure(figsize=(max(8, len(df)*0.4), 6))  # 根据数据量动态调整宽度

# 使用整数位置作为x轴
x_positions = np.arange(len(df))

# 绘制柱状图（深棕色），使用较窄的宽度
plt.bar(x_positions, df['成交量(十亿元)'], width=0.4, color='#8B4513', alpha=0.8, 
        label='沪深300ETF交易总额（十亿元）')

# 绘制日均线（红色虚线）
plt.axhline(y=average_volume, color='red', linestyle='--', linewidth=2, 
            label=f'沪深300ETF日均交易总额（十亿元）: {average_volume:.1f}')

# 设置标题和标签
plt.title('沪深300 ETF成交量', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('2025年', fontsize=11, labelpad=8)
plt.ylabel('成交量（十亿元）', fontsize=11, labelpad=8)

# 设置Y轴范围和刻度
max_volume = df['成交量(十亿元)'].max()
plt.ylim(0, max(40, max_volume * 1.2))
y_ticks = np.arange(0, max(40, max_volume * 1.2) + 5, 5)
plt.yticks(y_ticks, fontsize=10)

# 设置X轴刻度和标签 - 添加旋转和字体大小调整
date_labels = df['交易日期'].dt.strftime('%m/%d').tolist()
plt.xticks(x_positions, date_labels, fontsize=9, rotation=45, ha='right')
plt.gca().set_xlim(-0.5, len(df)-0.5)  # 紧凑的x轴范围

# 添加图例
plt.legend(loc='upper right', frameon=True, fontsize=10)

# 添加网格
plt.grid(axis='y', alpha=0.3)

# 在柱子上方添加数值标签
for i, v in enumerate(df['成交量(十亿元)']):
    plt.text(i, v + 0.3, f'{v:.1f}', 
             ha='center', va='bottom', fontsize=9, fontweight='bold')

# 调整布局，使图表更紧凑
plt.tight_layout(pad=2.0)  # 增加内边距以适应旋转的标签

# 使用系统时间命名并保存图片
current_time = datetime.now().strftime("%y%m%d")  # 格式为YYMMDD，例如251212
filename = f"{current_time}_沪深300ETF成交量.png"
plt.savefig(filename, dpi=300, bbox_inches='tight')
print(f"图表已保存为: {filename}")

# 显示图表
# plt.show()