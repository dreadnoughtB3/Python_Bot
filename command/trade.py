import japanize_matplotlib
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
from datetime import datetime, timezone, timedelta
import random, asyncio, gc

async def make_trade():
    trade_data = pd.read_csv("data/trade.csv",encoding="utf-8-sig")
    #<!-- 現在時刻を取得 -->
    JST = timezone(timedelta(hours=+9), 'JST')
    now = datetime.now(JST)
    daytime = now.strftime('%Y/%m/%d %H:%M:%S')
    current_stock = f"**株価推移: {daytime}**\n"

    #株価
    x = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]           # 横軸を日付に
    title_set = ["ニューヨーク証券取引所", "ナスダック証券取引所","上海証券取引所", "東京証券取引所"]

    # figオブジェクトの作成
    fig = plt.figure(figsize=(10,7)) # 図のサイズを指定
    fig.suptitle(f"テラ - 証券取引所 | {daytime}",size = 20, color = "red")
    mpl.rcParams['axes.xmargin'] = 0
    mpl.rcParams['axes.ymargin'] = 0
    
    #グラフを描画するsubplot領域を作成。
    for i in range(1,5):
        await asyncio.sleep(10)
        addment = int(trade_data.iloc[i-1,2])           # 加算値を取得
        base = int(random.randrange(25,70,1) + addment) # 基礎値を決定

        if base>=95:    #基礎値が95以上であれば
            plus = 50   #補正を+40
            addment = 40#次回基礎値の補正を+40
        elif 75<=base<95:
            plus = 35
            addment = 30
        elif 60<=base<75:
            plus = 20
            addment = 15
        elif 30<=base<60:
            plus = 10
            addment = 5
        elif 15<base<30:
            plus = 0
            addment = -10
        elif 5<base<=15:
            plus = -15
            addment = -25
        elif base<=5: 
            plus = -30
            addment = -40
            
        Stock = int(random.randrange(15,101,1)) + plus   # 株価を決定
        y = trade_data.iloc[i-1,1].split(",")
        y = ([int(s) for s in y])
        y.pop(0)
        y.append(Stock)
        stock_list = [str(n) for n in y]
        trade_data.iloc[i-1,1] = ",".join(stock_list)    # 株価推移を更新
        trade_data.iloc[i-1,2] = str(addment)            # 加算値を更新
        
        #<-- グラフ作成 -->
        ax = fig.add_subplot(2, 2, i)
        ax.plot(x, y, lw=1,markersize=3,marker="o")
        ax.set_xticks([24,23,22,21,20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0],
                    ["0","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24"])
        ax.set_yticks(range(-75, 175, 25))
        ax.tick_params(labelsize="7")
        ax.set_title(title_set[i-1])
        ax.grid()
        
        current_stock += f"`{title_set[i-1]}: {Stock}$`\n"

    # グラフを保存
    plt.savefig('output/trade.png', bbox_inches='tight', dpi=500)
    plt.clf()
    plt.close()
    trade_data.to_csv('data/trade.csv',index=False)
    del trade_data
    gc.collect()
    
    return current_stock
  
async def fx_trade():
    now = datetime.now(timezone(timedelta(hours=+9), "JST")).strftime('%Y/%m/%d %H:%M:%S')
    send_msg = f"**為替レート: {now}**\n"
    name_set = ["ドル/ポンド", "ドル/人民元","ドル/ユーロ", "ドル/ルーブル"]
    currency_set = ["ポンド","人民元", "ユーロ", "ルーブル"]
    for i in range(4):
        if random.randrange(2) == 0:
            fx_price = 1 + random.random()
        else:
            fx_price = 1 - random.random()
        fx_price = round(fx_price,2)
        send_msg += f"`{name_set[i]}: 1ドル{fx_price}{currency_set[i]}`\n"
    return send_msg