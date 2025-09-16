from sse_data_fetcher import sh_fetch_and_save_data
from szse_data_fetcher import sz_fetch_and_save_data
import datetime

# 代码数组
shcodes = ['510300','510310','510330','512100','560010']

# 代码数组
szcodes = ['159919','159845','159629']

# 使用系统当前日期(昨天 - datetime.timedelta(days=1))
current_date = datetime.date.today()
start_date = current_date
end_date = current_date

# 设定起始日期和结束日期
# start_date = datetime.date(2024, 1, 2)
# end_date = datetime.date(2024, 2, 21)

# 调用函数获取数据
sh_success_count, sh_fail_count = sh_fetch_and_save_data(shcodes, start_date, end_date)

# 调用函数获取数据
sz_success_count, sz_fail_count = sz_fetch_and_save_data(szcodes, start_date, end_date)

print(f"上证执行完成！成功获取 {sh_success_count} 次，失败 {sh_fail_count} 次")

print(f"深圳执行完成！成功获取 {sz_success_count} 次，失败 {sz_fail_count} 次")