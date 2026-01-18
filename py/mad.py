import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.ticker as ticker
import os
import sys

# 获取当前目录下的TTF字体文件
current_dir = os.path.dirname(os.path.abspath(__file__))
ttf_files = [f for f in os.listdir(current_dir) if f.endswith('.ttf')]

if ttf_files:
    # 添加字体到Matplotlib字体管理器
    font_path = os.path.join(current_dir, ttf_files[0])
    fm.fontManager.addfont(font_path)
    
    # 获取字体名称
    font_prop = fm.FontProperties(fname=font_path)
    font_name = font_prop.get_name()
    
    # 设置全局字体
    plt.rcParams['font.family'] = font_name
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 设置中文字体支持SimHei
# plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
# plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

# 1. 读取历史窗口数据
try:
    hist_df = pd.read_csv('20天窗口数据.csv')
    print(f"历史窗口数据形状: {hist_df.shape}")
    print("历史窗口数据前5行:")
    print(hist_df.head())
except FileNotFoundError:
    print("错误: 未找到'20天窗口数据.csv'文件")
    sys.exit(1)

# 2. 读取新数据
try:
    new_df = pd.read_csv('沪深300ETF.csv')
    print(f"\n新数据形状: {new_df.shape}")
    print("新数据前5行:")
    print(new_df.head())
except FileNotFoundError:
    print("错误: 未找到'沪深300ETF.csv'文件")
    sys.exit(1)

# 3. 合并数据（历史数据在前，新数据在后）
df = pd.concat([hist_df, new_df], ignore_index=True)
print(f"\n合并后总数据形状: {df.shape}")

# 4. 检查总数据量是否大于20
if len(df) <= 20:
    print(f"错误: 合并后总数据量({len(df)})不足20天，无法进行计算")
    print("程序将关闭...")
    sys.exit(1)
else:
    print(f"数据量检查通过: 总数据{len(df)}天 > 20天窗口")

# 5. 实现滑动滞后窗口MAD方法
def lagged_rolling_mad(data, k=20, threshold=2.0):
    """
    滑动滞后窗口MAD异常检测
    
    参数:
    data: 时间序列数据
    k: 窗口大小
    threshold: 异常阈值
    
    返回:
    is_outlier: 异常值布尔数组
    z_scores: 各点的修正Z分数
    """
    n = len(data)
    z_scores = np.zeros(n)
    is_outlier = np.zeros(n, dtype=bool)
    
    for t in range(k, n):
        # 获取滞后窗口（不包含当前点）
        window = data[t-k:t]
        
        # 计算窗口中位数
        median_val = np.median(window)
        
        # 计算MAD
        mad_val = np.median(np.abs(window - median_val))
        
        # 处理MAD=0的情况
        if mad_val == 0:
            mad_val = 1e-8
        
        # 计算修正Z分数
        z_score = 0.6745 * (data[t] - median_val) / mad_val
        z_scores[t] = z_score
        
        # 判断异常
        if abs(z_score) > threshold:
            is_outlier[t] = True
    
    return is_outlier, z_scores

# 6. 应用到数据
data = df['总成交额(万元)'].values
is_outlier, z_scores = lagged_rolling_mad(data, k=20, threshold=2.0)

# 7. 添加结果到DataFrame
df['lag_mad_z_score'] = z_scores
df['is_outlier'] = is_outlier

# 8. 只显示新数据部分的异常值统计
new_data_start_idx = len(hist_df)
new_data_is_outlier = is_outlier[new_data_start_idx:]
outlier_count = np.sum(new_data_is_outlier)
new_data_count = len(new_df)

print(f"\n=== 新数据部分异常检测结果 ===")
print(f"新数据天数: {new_data_count}")
print(f"检测到的异常值数量: {outlier_count}")
print(f"异常值占比: {outlier_count/new_data_count*100:.2f}%")

# 9. 显示异常值详情（只显示新数据部分）
new_data_outliers = df.iloc[new_data_start_idx:][df.iloc[new_data_start_idx:]['is_outlier']]
print("\n异常值详情:")
if len(new_data_outliers) > 0:
    print(new_data_outliers[['交易日期', '总成交额(万元)', 'lag_mad_z_score']])
else:
    print("无异常值")

# 10. 只对新数据部分进行可视化
new_df_processed = df.iloc[new_data_start_idx:].copy()

# 转换日期格式
new_df_processed['日期'] = pd.to_datetime(new_df_processed['交易日期'], format='%Y%m%d')
# 创建日期标签（月-日格式）
new_df_processed['日期标签'] = new_df_processed['日期'].dt.strftime('%m-%d')

# 获取异常值数据
outlier_dates = new_df_processed[new_df_processed['is_outlier']]['日期']
outlier_z_scores = new_df_processed[new_df_processed['is_outlier']]['lag_mad_z_score']
outlier_labels = new_df_processed[new_df_processed['is_outlier']]['日期标签']

# 创建紧凑的图表
plt.figure(figsize=(max(8, len(new_df_processed)*0.1), 6))

# 1. 开启压缩
plt.yscale('symlog', linthresh=10)

# 2. 找回自动生成的“普通数字”刻度
ax = plt.gca()

# 让系统自动找刻度，但不要只找 10 的倍数
ax.yaxis.set_major_locator(ticker.AutoLocator()) 

# 强制把标签转回普通的数字（例如 10 而不是 10^1）
ax.yaxis.set_major_formatter(ticker.ScalarFormatter())

# 绘制修正Z分数
plt.plot(new_df_processed['日期'], new_df_processed['lag_mad_z_score'], 
         color='green', linewidth=1, label='修正Z分数')
plt.axhline(y=2.0, color='red', linestyle='--', alpha=0.7, label='阈值 (+2.0)')
plt.axhspan(1.75,2.0, color='orange', alpha=0.7, label='预警区间 (+1.75)')
plt.axhline(y=-2.0, color='red', linestyle='--', alpha=0.7, label='阈值 (-2.0)')
plt.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=0.5)

# 标记异常值点
if len(outlier_dates) > 0:
    plt.scatter(outlier_dates, outlier_z_scores, 
               color='red', s=50, label='异常值', zorder=5)

# 在异常值点旁边添加日期标签
if len(outlier_dates) > 0:
    for date, z_score, label in zip(outlier_dates, outlier_z_scores, outlier_labels):
        # 添加标注
        plt.annotate(label, 
                     xy=(date, z_score),
                     xytext=(0, 10),  # 偏移量
                     textcoords='offset points',
                     fontsize=8,
                     ha='center',
                     bbox=dict(boxstyle='round,pad=0.2', facecolor='yellow', alpha=0.7, edgecolor='red'),
                     arrowprops=dict(arrowstyle='->', color='red', lw=1))

plt.title('沪深300ETF滑动滞后窗口MAD异常检测 - 修正Z分数')
plt.xlabel('日期')
plt.ylabel('修正Z分数')
plt.legend()
plt.grid(True, alpha=0.3)

# 格式化x轴日期
plt.xticks(rotation=45)

# 调整布局
plt.tight_layout()

# 使用系统时间命名并保存图片
current_time = datetime.now().strftime("%y%m%d")
filename = f"{current_time}_沪深300ETF滑动滞后窗口MAD异常检测.png"
plt.savefig(filename, dpi=300, bbox_inches='tight')
print(f"\n图表已保存为: {filename}")

# 显示图表
# plt.show()

# 11. 计算和显示关键信息
print("\n" + "="*60)
print("数据汇总信息")
print("="*60)
print(f"历史窗口数据天数: {len(hist_df)}")
print(f"新数据天数: {len(new_df)}")
print(f"总数据天数: {len(df)}")
print(f"计算起始点: 第{20}天 (从历史数据开始)")
print(f"新数据开始索引: {new_data_start_idx}")
print(f"新数据第一个计算点: 新数据第1天")
print(f"检测窗口大小: 20天")
print(f"异常阈值: 2.0")

# 12. 添加数据验证
print("\n" + "="*60)
print("数据验证")
print("="*60)
print(f"1. 历史数据最后5天:")
print(hist_df.tail())
print(f"\n2. 新数据前5天:")
print(new_df.head())
print(f"\n3. 合并后数据衔接验证:")
print(f"  历史数据最后日期: {hist_df.iloc[-1]['交易日期']}")
print(f"  新数据最早日期: {new_df.iloc[0]['交易日期']}")