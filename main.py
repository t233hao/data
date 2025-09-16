import os

# 顺序执行
os.system("python ./py/crawler.py")
os.system("python ./py/sse_csv.py")
os.system("python ./py/szse_csv.py")
os.system("python ./py/draw300.py")
os.system("python ./py/draw1000.py")