import akshare as ak
import pandas as pd

# 获取所有历史交易日数据（数据来自新浪）
# 该接口返回所有有记录的交易日列表
trade_cal_df = ak.tool_trade_date_hist_sina()

# 转换日期列为 datetime 格式
trade_cal_df["trade_date"] = pd.to_datetime(trade_cal_df["trade_date"]).dt.date

# 筛选 2025 年的交易日
# 注意：只有当交易所公布了2025年安排且接口更新后，此处才能查到2025年的数据
start_date = pd.to_datetime("2025-01-01").date()
end_date = pd.to_datetime("2025-12-31").date()

calendar_2025 = trade_cal_df[
    (trade_cal_df["trade_date"] >= start_date) & 
    (trade_cal_df["trade_date"] <= end_date)
]

# 输出结果
print(f"2025年A股全年交易日天数为: {len(calendar_2025)}")
print(calendar_2025)