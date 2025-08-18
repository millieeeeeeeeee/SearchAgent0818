"""設置今日為2024-09-01"""
from datetime import datetime, timedelta

#變數設定
import config
today=config.today
#today = datetime(2024, 9, 1)

#上週
def get_last_week_range(today):
    start_of_this_week = today - timedelta(days=today.weekday())
    start = start_of_this_week - timedelta(days=7)
    end = start + timedelta(days=6)
    return start, end

#上月
def get_last_month_range(today):
    first_of_this_month = today.replace(day=1)
    last_day_of_last_month = first_of_this_month - timedelta(days=1)
    first_day_of_last_month = last_day_of_last_month.replace(day=1)
    return first_day_of_last_month, last_day_of_last_month

#str_date = start.strftime('%Y-%m-%d')       # '2024-08-19'
#iso_date = start.isoformat()           # 也是 '2024-08-19'
#print(str_date ,iso_date)
