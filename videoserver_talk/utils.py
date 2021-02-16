import datetime
import time
import random

def random_alphanumeric(length=9):
    chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXY'
    code = ""
    for x in range(length):
        code += random.choice(chars)
    return code

def getDateAtGap(day_increment=0):
    per_day_time_microseconds = 24 * 60 * 60 * 1000 * 1000
    now_time = time.time() * 1000 * 1000
    millsGap = (per_day_time_microseconds * abs(day_increment))
    if day_increment<0:
        target_time = now_time - millsGap
    else:
        target_time = now_time + millsGap
    final_date = datetime.date.fromtimestamp(target_time/1000000)
    return final_date.strftime("%Y-%m-%d")    