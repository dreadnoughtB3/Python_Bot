import numpy as np
from datetime import datetime, timezone, timedelta

async def exp_numpy(dice_body):
    if "+" in dice_body: 
        dice_list = []
        means = []
        plus = [0]
        args_full = dice_body.split("+") # +でダイス単位に分割
        for items in args_full:          # ダイスをdで数字に分割
            if "d" not in items:         # ただの足し算なら
                plus.append(int(items))
                continue
            dice_list.append(items.split("d"))
        for i in range(len(dice_list)):
            args = [int(n) for n in dice_list[i]]
            value = np.arange(args[0],((args[0]*args[1])+1))
            means.append(np.mean(value))
        return sum(means) + sum(plus)
    else:
        args_str = dice_body.split("d")
        args = [int(n) for n in args_str]
        value = np.arange(args[0],((args[0]*args[1])+1))
        mean = np.mean(value)
        return mean



# 日付取得関数
def get_current_time():
    JST = timezone(timedelta(hours=+9), 'JST')
    now = datetime.now(JST)
    daytime = now.strftime('%Y/%m/%d %H:%M:%S')
    return daytime