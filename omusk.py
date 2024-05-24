#必要なライブラリをインポート
import random, discord, dice, re, csv
from math import floor
from discord.ext.commands import Bot
import pandas as pd

from command.r import r
from command.collection import gather, mine, fishing
from command.Explore import exp_numpy, get_current_time

from numpy import arange

#Bot関連設定
description = "Omusk v1.0"
intents = discord.Intents.all() #デフォルトのインテンツオブジェクトを生成
bot = Bot(command_prefix='?', description=description, help_command=None, intents=intents)

#時刻取得
daytime = get_current_time()

# 辞書
scherzo_list = ["1. 全武器物理、魔法ダメージ+2d", "2. HP30%回復(上限突破、効果が切れると本来の上限値まで戻る)", "3. 被ダメージ30%カット"]
achiv_ids = ["1","2","3","4","5","6","7"]
currency_list = ["Ti","G","H","Q","B","L","W"]
current_party = {}
current_status = {}
num_to_str = {1:"A", 2:"B", 3:"C", 4:"D", 5:"E", 6:"F", 7:"G", 8:"H"}
famble_list = ["```\n１．油断\n次の自分ターンがくるまで、被ダメージが2倍(+100%)となる\n```",
               "```\n２．転倒\n　攻撃ファンブルでこれになった場合、このターンと次の味方ターンで攻撃が不可能となる。また、この状態で敵ターンがきた場合、回避/庇う/弾くスキルが使用不可能、被ダメは<<等倍>>となる。アイテム使用は可能。\n※ただし、ファンブルになっていない味方が自分のターンを消費することで、攻撃不可ターンをこのターンのみにすることができる。ただし、次の敵ターンは回避/庇う/弾くスキル使用不可能、被ダメは<<等倍>>\n\n　回避ファンブルでこれになった場合、1発分のダメージは回避成功判定となるが、<<続けて攻撃を受ける場合、以降のダメージは被ダメ2倍(+100%)>>を受ける。また、次の味方ターンに攻撃ができず、回避/庇う/弾くスキルが使用不可能。その次の敵ターンに復帰する。アイテム使用は可能\n※ただし、転倒した味方が生きている場合、次の味方ターンでファンブルしていない味方が自分のターンを消費することで、攻撃不可ターンをそのターンのみにすることができる。ただし、次の敵ターンは回避/庇う/弾くスキル使用不可能、被ダメは<<等倍>>\n```",
"```\n３．故障\n・攻撃ファンブルでこれになった場合、このターンと次の味方ターンで攻撃ができなくなる。次の敵ターンで回避/庇うは可能、弾くは使用不可能。アイテム使用は可能。\n\
・回避ファンブルでこれになった場合、等倍でダメージを受ける。次の味方ターンは攻撃できず、その次の味方ターンで復帰する。回避/庇うは可能、弾くは使用不可能。アイテム使用は可能。\n```",
"```\n４．事故\n攻撃ファンブルでこれになった場合、ファンブルした回数分の威力を自分自身が受ける（防御力等は反映される）。また、状態異常の判定付きの攻撃だった場合はこれも判定をする。\n\
回避ファンブルでこれになった場合、自分は回避に成功するが、代わりに本来受ける予定だったダメージを他の味方が負う。\n1d〇（2人だったら確定で相方へ、3人→1d2、4人→1d3）で決まり、ダメージは前衛/後衛の効果は適用される。\
ただし対象になった味方が本来の攻撃の回避に成功していた場合でも、このダメージは確定で受ける（防御力等は反映される）\nただし、ソロで回避ファンブルだった場合、自分自身が<<被ダメージ1.5倍(+50%)>>で受ける。\n```",
"```5. 散漫\n攻撃ファンブルでこれになった場合、攻撃が命中せず、その後敵ターンが3ターン経過するまで命中率と回避率が半減する。\n回避ファンブルでこれになった場合等倍でダメージを受けるが、味方ターンが3ターン経過するまで(味方ターンに発生した場合は敵ターンが3ターン経過するまで)命中率と回避率が半減する。\n```"]
critical_list = ["```\n１．強攻撃\n物理攻撃（射撃含む）の場合、威力1d+「技量÷5」の数値、魔法攻撃の場合、威力1d+「信仰÷5」の数値が加わり、ダメージを与える。この場合敵の回避判定を行う。敵の場合は威力+2dになる\n\
なおこの+1dは武器威力(先頭に記載された威力のダイス部分)のみ反映される。敵の場合は先頭に記載された威力のダイス部分のみ反映される```",
                 "```\n２．確定攻撃\n物理攻撃（射撃含む）の場合「技量÷5」の数値、魔法攻撃の場合「信仰÷5」の数値が加わり、ダメージを与える。この場合敵の回避判定は<<行わない>>（確定ヒット）敵の場合は威力+1dになる（先頭に記載された威力のダイス部分のみ反映される）\n```"]

dfA = pd.read_csv("data/registed_commands.csv",encoding="cp932")
df = dfA.set_index("TRIG")
achiv_data = pd.read_csv("excel/achivments.csv",index_col=0,encoding="Shift-JIS")
level_df = pd.read_csv("excel/levels.csv",encoding="Shift-JIS")
level_data = dict(zip(level_df["level"],level_df["need"]))
user_achiv = pd.read_csv("data/user_achiv.csv",index_col=0,encoding="Shift-JIS")
user_level = pd.read_csv("data/user_level.csv",index_col=0, encoding="utf-8-sig")

quest_data = pd.read_csv("data/rewards.csv")
rewards_df = quest_data.set_index("id")
qid = arange(1,34)
item_ids = arange(1,42)

#Botログイン時処理
@bot.event
async def on_ready():
    global buy_channel, inn_channel
    print(f"{bot.user} が起動されました。\n起動時刻:{daytime}")
    buy_channel = bot.get_channel(1105899998723457074)
    inn_channel = bot.get_channel(1122760708250152960)

# 期待値
@bot.command(name="exp")
async def explore_calc(ctx,dice_body:str):
    if re.search(r"[^0-9+d*.]",dice_body) != None:
        await ctx.send("`>正しいダイスを入力してください`")
        return
    if "*" in dice_body:
        parts = dice_body.split("*")
        if re.search(r"[^0-9.]",parts[1]) != None:
            await ctx.send("`>正しい係数を入力してください`")
            return
        res = (await exp_numpy(parts[0]))
        final_res = res * float(parts[1])
        await ctx.send(f"> {dice_body}の期待値: **{final_res}**")
    else:
        res = (await exp_numpy(dice_body))
        await ctx.send(f"> {dice_body}の期待値: **{res}**")

# チャットパレット登録コマンド
@bot.command(name="cr")
async def register(ctx, command:str = "none", trig:str = "none", describe:str = "none"):
    global df, dfA
    usr_id = str(ctx.author.id)

    if command == "none":
        await ctx.send("`>コマンドを入力してください`")
        return
    elif trig == "none":
        await ctx.send("`>トリガーを入力してください`")
        return
    elif describe == "none":
        await ctx.send("`>説明を入力してください`")
        return
    
    if re.search(r"[^0-9*.()+-d]",command) != None:
        await ctx.send("正しいコマンドを入力してください")
        return
    
    trig_body = usr_id+trig
    
    if trig_body in df.index:
        await ctx.send("`>そのトリガーは既に登録されています`")
        return

    with open('data/registed_commands.csv', 'a', encoding="cp932") as f:
        writer = csv.writer(f)
        writer.writerow([trig_body, command, describe])

    #<-- データフレームを更新 -->
    dfA = pd.read_csv("data/registed_commands.csv",encoding="cp932")
    df = dfA.set_index("TRIG")
        
    await ctx.send(f"`>コマンド: {command}をトリガー: {trig}で登録しました`\n`説明: {describe}`")
    return

# チャットパレット使用コマンド
@bot.command(name="c")
async def chatpaletta(ctx, trigger:str = "none",com:str="no",option:str="no"):
    global df, dfA
    usr_id = str(ctx.author.id)
    
    #<-- トリガーが指定されていない場合 -->
    if trigger == "none":
        await ctx.send("`>トリガーを指定してください`")
        return
    
    com_trig = usr_id+trigger # トリガーを設定
    print(com_trig)
    #<-- コマンドが存在しない場合 -->
    if com_trig not in df.index:
        print(com_trig)
        await ctx.send("`>コマンドが登録されていません`")
        return
    
    if com == "del":
        df = df.drop(index=com_trig)
        df.to_csv('data/registed_commands.csv',encoding="cp932")
        #<-- データフレームを更新 -->
        dfA = pd.read_csv("data/registed_commands.csv",encoding="cp932")
        df = dfA.set_index("TRIG")
        await ctx.send(f"`>トリガー:{trigger}のコマンドを削除しました`")
    elif com.startswith("x"):
        if int(com.replace("x","")) > 20:
            await ctx.send("`>不正な回数です`")
            return
        com_body = df.loc[com_trig,"COM"]
        desc = df.loc[com_trig,"DESC"] 
        if "*" in option:
            # if float(option.replace("*","")) > 50.0:
            #     await ctx.send("`>不正な倍率です`")
            #     return
            com_body = "(" + com_body + ")" + option
            print(com_body)
        await dice_roll(ctx, dice_body=com_body, desc=desc, number=com) 
    elif com.startswith("*"):
        # if float(com.replace("*","")) > 50.0:
        #     await ctx.send("`>不正な倍率です`")
        #     return
        com_body = df.loc[com_trig,"COM"]
        desc = df.loc[com_trig,"DESC"]
        com_body = "(" + com_body + ")" + com
        print(com_body)
        if "x" in option:
            com_number = option.split("x")[1]
            if int(com_number) > 10: await ctx.send("`>不正な回数です`"); return
            await dice_roll(ctx, dice_body=com_body, desc=desc, number=option)
        else:
            await dice_roll(ctx, dice_body=com_body, desc=desc)
    else:
        #<-- データを取得 -->
        com_body = df.loc[com_trig,"COM"]
        desc = df.loc[com_trig,"DESC"]
        await dice_roll(ctx, dice_body=com_body, desc=desc)

# チャットパレット確認コマンド
@bot.command(name="cp")
async def chatpallet_show(ctx):
    global dfA
    TRIG_list = []
    COM_list = []
    DESC_list = []
    send_msg = ""
    usr_id = str(ctx.author.id)
    cp_df = (dfA[dfA["TRIG"].str.contains(usr_id)])
    if cp_df.empty:
        await ctx.send("`>チャットパレットが登録されていません`")
        return
    TRIG_list = cp_df["TRIG"].values.tolist()
    COM_list = cp_df["COM"].values.tolist()
    DESC_list = cp_df["DESC"].values.tolist()
    for i in range(len(TRIG_list)):
        trig = TRIG_list[i].replace(usr_id,"")
        send_msg += f"`{trig}: {COM_list[i]} | {DESC_list[i]}`\n"
    await ctx.send(send_msg)

# ダイスロール
@bot.command(name="r")
async def dice_roll(ctx, dice_body:str = "1d100", desc:str = " ", number:str="x0"):
    if number == "x0":
        send_message = "使用者:<@{}> {}\n".format(ctx.author.id, desc) + r(dice_body)
        await ctx.send(send_message)
    elif number.startswith("x"):
        send_message = "使用者:<@{}> {}\n".format(ctx.author.id, desc) + r(dice_body, number)
        await ctx.send(send_message)  
    else:
        await ctx.send("`>不正なコマンドです`")

# 購入コマンド
@bot.command(name="buy")
async def buying(ctx, name:str="nan", money:str="0", desc:str="nan"):
    global buy_channel
    send_message = "購入者:<@{}>\n".format(ctx.author.id)
    await buy_channel.send(f"{send_message}```\n{name}\n購入物:{money}\n消費金額:{desc}\n```")
    
# 宿屋コマンド
@bot.command(name="inn")
async def inn(ctx, name:str="nan", world:str="nan", level:int=0):
    global inn_channel
    spend = level * 30
    send_message = "利用者:<@{}>\n".format(ctx.author.id)
    await inn_channel.send(f"{send_message}```\n名前:{name}\n出身世界:{world}\nレベル:{level}\n支払い:{spend}\n```")

# レベル管理コマンド       
@bot.command(name="lv")
async def level(ctx,chara = 0,exp:str = "0"):
    global num_to_str, user_level, level_data
    
    if chara == 0:
        await ctx.send("`>キャラを指定してください`")
        return
    
    usr_id = str(ctx.author.id)
    chara_id = usr_id + "_" + num_to_str[chara]
    if chara_id not in user_level.index:
        await ctx.send("`>キャラクターが登録されていません`")
        return
    chara_name = user_level.loc[chara_id, ["name"]] # キャラ名
    chara_name = chara_name.iloc[-1]
    current_lvl = user_level.loc[chara_id,["lv"]] # 現在レベルを取得
    current_lvl = current_lvl.iloc[-1]
    current_exp = user_level.loc[chara_id,["exp"]] # 現在の経験値
    current_exp = current_exp.iloc[-1]
    next_1lvl_need = level_data[current_lvl+1] # 次のレベルに必要な経験値
    print(chara_name)
    print(current_lvl)
    
    if exp == "0":
        send_msg = f"> **名前: {chara_name}**\n> **レベル: {current_lvl} | 経験値: {current_exp}/{next_1lvl_need}**"
        await ctx.send(send_msg)
    else:
        if exp.isdecimal() == False:              # 経験値増加量が数値でなければ
            await ctx.send("`>増加量が不正です`")
            return
        
        lat_exp = int(current_exp) + int(exp) # 最新の経験値
        next_2lvl_need = int(level_data[current_lvl+2]) + int(next_1lvl_need)
        next_3lvl_need = int(level_data[current_lvl+3]) + int(next_1lvl_need) + int(next_2lvl_need)
        
        #<-- 1レベル上 -->
        if  next_2lvl_need > lat_exp >= next_1lvl_need:          # 現在経験値が必要経験値以上なら
            lat_exp -= next_1lvl_need # 最新の経験値
            lat_lvl = current_lvl + 1      # 最新のレベル
            await ctx.send(f"**LEVEL UP** | `{current_lvl} >> {lat_lvl}`")
        #<-- 2レベル上 -->
        elif next_3lvl_need > lat_exp >= next_2lvl_need:
            lat_exp -= next_2lvl_need
            lat_lvl = current_lvl + 2
            await ctx.send(f"**LEVEL UP** | `{current_lvl} >> {lat_lvl}`")
        #<-- 3レベル上 -->
        elif lat_exp >= next_3lvl_need:
            lat_exp -= next_3lvl_need
            lat_lvl = current_lvl + 3
            await ctx.send(f"**LEVEL UP** | `{current_lvl} >> {lat_lvl}`")
        else:
            lat_lvl = current_lvl
        user_level.loc[chara_id,["exp"]] = lat_exp # 更新
        user_level.loc[chara_id,["lv"]] = lat_lvl # 更新
        next_1lvl_need = level_data[lat_lvl+1] # 次のレベルに必要な経験値
        await ctx.send(f"> **名前: {chara_name}**\n> **レベル: {lat_lvl} | 経験値: {lat_exp}/{next_1lvl_need}**")
            
        user_level.to_csv('data/user_level.csv')
        user_level = pd.read_csv("data/user_level.csv",index_col=0, encoding="utf-8-sig")

# キャラ登録コマンド
@bot.command(name="regist")
async def level_register(ctx, name:str = "nan",level:int = "0", exp:int = "0",lp:int="0"):
    global num_to_str, user_level
    usr_id = str(ctx.author.id)
    chara_index = user_level.index.values.tolist()
    # キャラID生成
    cnt = 0
    for i in chara_index:
        cnt += i.count(usr_id)
    chara_id = usr_id + "_" + num_to_str[cnt+1]
    # データ更新
    with open('data/user_level.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([chara_id, name, level, exp, lp,0,0,0,0,0,0,0])
    await ctx.send(f"> `番号: {cnt+1} | 名前: {name}`\n> `LP: {lp} | レベル: {level} | 経験値: {exp}`\n`>以上の情報で登録しました`")
    # DF読み込み
    user_level = pd.read_csv("data/user_level.csv",index_col=0, encoding="utf-8-sig")
  
# キャラ編集コマンド  
@bot.command(name="edit")
async def chara_edit(ctx, chara:str = "nan",name:str="nan",level:int="0",exp:int="0"):
    global num_to_str, user_level
    if chara.isdecimal() == False:
        await ctx.send("`>キャラIDが不正です`")
        return  
    
    usr_id = str(ctx.author.id)
    chara_id = usr_id + "_" + num_to_str[int(chara)]
    
    if chara_id not in user_level.index:
        await ctx.send("`>キャラIDが存在しません`")
        return
    
    user_level.loc[chara_id, ["name"]] = name
    user_level.loc[chara_id, ["lv"]] = level
    user_level.loc[chara_id, ["exp"]] = exp
    
    user_level.to_csv('data/user_level.csv')
    user_level = pd.read_csv("data/user_level.csv",index_col=0, encoding="utf-8-sig")
    await ctx.send(f"`{chara}番のキャラを以下の情報に編集しました`\n`名前: {name}`\n`レベル: {level} | 経験値: {exp}`")

# LP管理コマンド
@bot.command(name="lp")
async def lp_control(ctx,chara:str = "nan", lp:str = "0"):
    global num_to_str, user_level
    if chara.isdecimal() == False:
        await ctx.send("`>キャラIDが不正です`")
        return  
    
    usr_id = str(ctx.author.id)
    chara_id = usr_id + "_" + num_to_str[int(chara)]
    
    if chara_id not in user_level.index:
        await ctx.send("`>キャラIDが存在しません`")
        return
    
    chara_name = user_level.loc[chara_id, ["name"]] # キャラ名
    chara_name = chara_name.iloc[-1]
    current_lp = user_level.loc[chara_id, ["lp"]] # LP取得
    current_lp = current_lp.iloc[-1]
    if lp == "0":
        await ctx.send(f"> **`名前: {chara_name}`**\n> **`LP : {current_lp}/100`**")
    else:
        if re.search(r"[^0-9+-.]",lp) != None:
            await ctx.send("`>正しい数値を入力してください`")
            return
        if "-" in lp:
            current_lp -= int(lp.replace("-", ""))
        elif "+" in lp:
            current_lp += int(lp.replace("+", ""))
        else:
            current_lp += int(lp)
        if current_lp < 0: current_lp = 0 # 0以下になったら0にする
        
        user_level.loc[chara_id, ["lp"]] = current_lp
        user_level.to_csv('data/user_level.csv')
        user_level = pd.read_csv("data/user_level.csv",index_col=0, encoding="utf-8-sig")
        await ctx.send(f"`LPを{lp}変動させました`\n> **`名前: {chara_name}`**\n> **`LP: {current_lp}/100`**")

# クリティカルコマンド
@bot.command(name="fn")
async def fanble(ctx):
    global famble_list
    tmp = random.randrange(5)
    await ctx.send(famble_list[tmp])
  
# ファンブルコマンド  
@bot.command(name="ct")
async def critical(ctx):
    global critical_list
    tmp = random.randrange(2)
    await ctx.send(critical_list[tmp])
    
# パーティー登録 
@bot.command(name="stat")
async def status(ctx):
    usr_id = ctx.author.id
    # 表示
    if usr_id in current_party:
        status_list = current_party[usr_id]
        hp = status_list[0]
        mp = status_list[1]
        stamina = status_list[2]
        await ctx.send(f"`現在のステータス:`\n`HP:{hp} | MP:{mp} | スタミナ:{stamina}`")
        return
    # 登録
    else:
        channelID = ctx.channel.id   # コマンドが実行されたチャンネルIDを取得
        usr_name = ctx.author.display_name #ニックネームを取得
        if channelID not in current_status:
            current_status[channelID] = {}
            current_party[channelID] = {}
        current_status[channelID] = {usr_name:"生存"}
        current_party[channelID][usr_id] = [0,0,0,0]
        await ctx.send(f"`ステータスを登録します。`\n`?hp [数値]` | `?mp [数値]` | `?st [数値]`\nで初期値を入力してください")
        return
    
# パーティー確認コマンド
@bot.command(name="party")
async def party_stat(ctx, command:str="nan"):
    channelID = ctx.channel.id   # コマンドが実行されたチャンネルIDを取得
    if channelID not in current_status:
        await ctx.send("`>パーティーが編成されていません`")
        return
    if command == "nan":
        formated_text = ""
        for k, v in current_status[channelID].items():
            formated_text += f"**`{k}`**:**`{v}`**\n"
        await ctx.send(formated_text)
    elif command == "del":
        del current_status[channelID], current_party[channelID]
        await ctx.send("`>パーティーを解散します`")
    else:
        await ctx.send("`>不正なコマンドです`")
           
# HP変動
@bot.command(name="hp")
async def hitpoint(ctx, num:str = "0"):
    usr_id = ctx.author.id
    usr_name = ctx.author.display_name #ニックネームを取得
    channelID = ctx.channel.id   # コマンドが実行されたチャンネルIDを取得
    if re.search(r"[^0-9+-.]",num) != None:
        await ctx.send("`>正しい数値を入力してください`")
        return
    if usr_id not in current_party[channelID]:
        await ctx.send("`>ステータスが登録されていません`")
        return
    stat_list = current_party[channelID][usr_id]
    if "-" in num:
        stat_list[0] -= int(num.replace("-", ""))
    elif "+" in num:
        stat_list[0] += int(num.replace("+", ""))
    else:
        stat_list[0] += int(num)
        
    current_party[channelID][usr_id] = stat_list
    current_hp = stat_list[0]
    # もしHPが0になったら
    if current_hp <= 0:
        current_status[channelID][usr_name] = "死亡"
    # 死亡している状態でHPが増加したら
    if current_status[channelID][usr_name] == "死亡" and current_hp > 0:
        current_status[channelID][usr_name] = "生存"
        
    await ctx.send(f"`HPを{num}変動させました | 現在HP:{current_hp}`")
    return

# MP変動
@bot.command(name="mp")
async def magicpoint(ctx, num:str = "0"):
    usr_id = ctx.author.id 
    channelID = ctx.channel.id   # コマンドが実行されたチャンネルIDを取得
    if re.search(r"[^0-9+-.]",num) != None:
        await ctx.send("`>正しい数値を入力してください`")
        return
    if usr_id not in current_party[channelID]:
        await ctx.send("`>ステータスが登録されていません`")
        return
    stat_list = current_party[channelID][usr_id]
    if "-" in num:
        stat_list[1] -= int(num.replace("-", ""))
    elif "+" in num:
        stat_list[1] += int(num.replace("+", ""))
    else:
        stat_list[1] += int(num)
    
    current_party[channelID][usr_id] = stat_list
    current_mp = stat_list[1]
    await ctx.send(f"`MPを{num}変動させました | 現在MP:{current_mp}`")
    return

# スタミナ変動
@bot.command(name="st")
async def stamina(ctx, num:str = "0"):
    usr_id = ctx.author.id
    channelID = ctx.channel.id   # コマンドが実行されたチャンネルIDを取得
    if re.search(r"[^0-9+-.]",num) != None:
        await ctx.send("`>正しい数値を入力してください`")
        return
    if usr_id not in current_party[channelID]:
        await ctx.send("`>ステータスが登録されていません`")
        return
    stat_list = current_party[channelID][usr_id]
    if "-" in num:
        stat_list[2] -= int(num.replace("-", ""))
    elif "+" in num:
        stat_list[2] += int(num.replace("+", ""))
    else:
        stat_list[2] += int(num)
        
    current_party[channelID][usr_id] = stat_list
    current_stmn = stat_list[2]
    await ctx.send(f"`スタミナを{num}変動させました | 現在スタミナ:{current_stmn}`")
    return  

# 釣りコマンド
@bot.command(name="fishing")
async def fishing_com(ctx):
    arg = ctx.message.content.split(" ")
    if len(arg) == 4:
        if arg[1].startswith("l"):
            kind = arg[1]
            if arg[2].isdecimal():
                count = int(arg[2])
                if arg[3].isdecimal():
                    skill = int(arg[3])
                    results = (await fishing(kind, count, skill))
                    send_message = "使用者:<@{}>\n".format(ctx.author.id)
                    await ctx.send(send_message)
                    await ctx.send(results)  
                else:
                    await ctx.send("`>技能値は整数で入力してください`")
            else:
                await ctx.send("`>回数は整数で入力してください`")      
        else:
            await ctx.send("`>場所IDが不正です`")
    else:
        await ctx.send("`>引数が不正です`")
        
# 採取コマンド
@bot.command(name="gather")
async def gatherring(ctx): # [種類] [回数]
    arg = ctx.message.content.split(" ")
    if len(arg) == 3: 
        if arg[1].startswith("l"):     # 種類がlで始まっているか
            kind = arg[1]              # 場所ID
            if arg[2].isdecimal():     # 回数が整数か
                count = int(arg[2])    # 回数
                results = (await gather(kind, count))
                send_message = "使用者:<@{}>\n".format(ctx.author.id)
                await ctx.send(send_message)
                await ctx.send(results)
            else:
                await ctx.send("`>回数は整数で入力してください`")
        else:
            await ctx.send("`>場所IDが不正です`")
    else:
        print(arg)
        await ctx.send("`>引数が不正です`")

# 採掘コマンド
@bot.command(name="mine")
async def mining(ctx): # [種類] [回数]
    arg = ctx.message.content.split(" ")
    if len(arg) == 3: 
        if arg[1].startswith("l"):     # 種類がlで始まっているか
            kind = arg[1]              # 場所ID
            if arg[2].isdecimal():     # 回数が整数か
                count = int(arg[2])    # 回数
                results = (await mine(kind, count))
                send_message = "使用者:<@{}>\n".format(ctx.author.id)
                await ctx.send(send_message)
                await ctx.send(results)
            else:
                await ctx.send("`>回数は整数で入力してください`")
        else:
            await ctx.send("`>IDが不正です`")
    else:
        print(arg)
        await ctx.send("`>引数が不正です`")

@bot.command(name="configs")
async def save_config(ctx):
    channel=bot.get_channel(1099566886183763989)
    file1=discord.File("data/registed_commands.csv")
    file2=discord.File("data/user_achiv.csv")
    file3=discord.File("data/user_level.csv")
    await channel.send(file=file1)
    await channel.send(file=file2)
    await channel.send(file=file3)

# クエスト報酬算出
@bot.command(name="reward")
async def reward(ctx, quest_id:str = "0", level:str = "0", enemy_num:str = "0"):
    if quest_id.isdecimal() == False: await ctx.send("`>クエストIDは整数で入力してください`"); return
    if level.isdecimal() == False: await ctx.send("`>最大レベルは整数で入力してください`"); return
    if int(quest_id) not in qid: await ctx.send("`>クエストIDが存在しません`"); return
    level = int(level)
    
    high_level = rewards_df.loc[quest_id,"high"]
    if level >= int(high_level):
        quest_id = f"{quest_id}h"
    
    gold_result = 0
    exp_result = 0
    item_result = ""
    item_temp = {}
    send_text = ""
    extra_enemy = None
    
    item_list = rewards_df.loc[quest_id,"item"]
    quest_name = rewards_df.loc[quest_id,"name"]
    world = rewards_df.loc[quest_id,"world"]

    # アイテム関連処理
    if "/" not in item_list:
        item_data = [item_list]
    else:
        item_data = item_list.split("/")

    for item in item_data:
        if "ｘ" in item: continue
        item_temp[item.split("：")[1]] = 0
    
        
    # 討伐数
    if "/" in enemy_num:
        if enemy_num.endswith("/"): enemy_num = enemy_num[:-1]
        enemy_splited = enemy_num.split("/")
    else:
        enemy_splited = [enemy_num]

    for i in range(len(enemy_splited)):
        if enemy_splited[i].endswith("+"): await ctx.send("`>敵の数が不正です`"); return
        if "+" in enemy_splited[i]:
            normal_enemy = enemy_splited[i].split("+")[0]
            extra_enemy = enemy_splited[i].split("+")[1]
            if int(normal_enemy) > 10: await ctx.send("`>敵の数が不正です`"); return
            if int(extra_enemy) > 10: await ctx.send("`>敵の数が不正です`"); return
            if int(normal_enemy) <= 0: await ctx.send("`>敵の数が不正です`"); return
            if int(extra_enemy) <= 0: await ctx.send("`>敵の数が不正です`"); return
        else:
            if int(enemy_splited[i]) > 10: await ctx.send("`>敵の数が不正です`"); return
            if int(enemy_splited[i]) <= 0: await ctx.send("`>敵の数が不正です`"); return
        
        tmp = dice.roll("1d100+0")
        for x in item_data:
            suc = x.split("：")[0]
            item = x.split("：")[1]
            if "-" in suc:
                if int(suc.split("-")[0]) <= tmp <= int(suc.split("-")[1]):
                    item_temp[item.split("ｘ")[0]] += int(item.split("ｘ")[1]); break
            elif tmp <= int(suc):
                if "ｘ" in item: item_temp[item.split("ｘ")[0]] += int(item.split("ｘ")[1]); break # 複数個の場合
                item_temp[x.split("：")[1]] += 1; break                                           # 単数の場合
        gold_result += dice.roll(rewards_df.loc[quest_id,"money"])
        
        exp = rewards_df.loc[quest_id,"exp"]
        if "/" in rewards_df.loc[quest_id,"exp"]:
            exp_normal = rewards_df.loc[quest_id,"exp"].split("/")[0]
            exp_extra = rewards_df.loc[quest_id,"exp"].split("/")[1]
        if extra_enemy:
            exp_result += int(exp_normal) * int(normal_enemy)
            exp_result += int(exp_extra) * int(extra_enemy)
        else:
            exp_result += int(exp) * int(enemy_splited[i])
    
    for key, value in item_temp.items():
        if value == 0: continue
        item_result += f"{key}×{value}、"
    if not item_result:
        item_result = "なし"
    else:
        item_result = item_result[:-1]
        
    send_text = f"使用者:<@{ctx.author.id}>\n`クエスト名: {quest_name}` | `お金: {gold_result}{world}` | `経験値: {exp_result}`\n`アイテム: {item_result}`"
    await ctx.send(send_text)
         
# お金     
@bot.command(name="money")
async def money(ctx, chara:str = "0", num:str = "none", currency:str = "none", desc:str = "N/A"):
    global user_level, currency_list
    if chara.isdecimal() == False: await ctx.send("`>キャラ番号は整数で入力してください`"); return
    if int(chara) > 8: await ctx.send("`>キャラ番号が不正です`"); return
    if num == "none":
        usr_id = str(ctx.author.id)
        chara_id = usr_id + "_" + num_to_str[int(chara)]
        
        if chara_id not in user_level.index: await ctx.send("`>キャラIDが存在しません`"); return
        
        chara_name = user_level.loc[chara_id, ["name"]] # キャラ名
        chara_name = chara_name.iloc[-1]
        send_msg = f"> **`名前: {chara_name}`**\n > **`通貨`**"
        current_money = user_level.loc[chara_id, ["Ti","G","H","Q","B","L","W"]].values.tolist()
        for i in range(7):
            if current_money[i] == 0: continue
            send_msg += f" | `{currency_list[i]}:{current_money[i]}`"
            
        await ctx.send(send_msg)
    else:
        if re.search(r"[^0-9+-]",num) != None: await ctx.send("`>増減値が不正です`"); return
        
        usr_id = str(ctx.author.id)
        chara_id = usr_id + "_" + num_to_str[int(chara)]
        
        if chara_id not in user_level.index: await ctx.send("`>キャラIDが存在しません`"); return
        if re.fullmatch("Ti|G|H|Q|B|L|W",currency) == None: await ctx.send("`>通貨が不正です`"); return
        
        chara_name = user_level.loc[chara_id, ["name"]] # キャラ名
        chara_name = chara_name.iloc[-1]
        current_currency = user_level.at[chara_id, currency]
        
        if "-" in num:
            value = num.replace("-","")
            latest_currency = current_currency - int(value)
        elif "+" in num:
            value = num.replace("+","")
            latest_currency = current_currency + int(value)
        else:
            value = num
            latest_currency = current_currency + int(value)
        
        user_level.at[chara_id, currency] = latest_currency
        user_level.to_csv('data/user_level.csv')
        user_level = pd.read_csv("data/user_level.csv",index_col=0, encoding="utf-8-sig")
        now_time = get_current_time()
        if "-" in num:
            await ctx.send(f"> **`名前: {chara_name}`**\n> `{value}{currency}を出金しました。残金は{latest_currency}{currency}です。`\n> `理由: {desc}`\n`時刻:{now_time}`")
        else:   
            await ctx.send(f"> **`名前: {chara_name}`**\n> `{value}{currency}を入金しました。残金は{latest_currency}{currency}です。`\n> `理由: {desc}`\n`時刻:{now_time}`")

# カウント
@bot.command(name="count")
async def count(ctx, num:str='0', suc:str='0'):
    if not num.isdecimal() or not suc.isdecimal():
        await ctx.send('`> 不正な引数です。`'); return
    elif int(num) == 0 or int(suc) == 0:
        await ctx.send('`> 0は入力できません。`'); return
    elif int(num) > 100 or int(suc) >= 100:
        await ctx.send('`> 100以上の数値は入力できません。`'); return
        
    results = [0,0,0,0]
    
    for i in range(int(num)):
        res = random.randint(1,100)
        if res <= 5:
            results[2] += 1
        elif res >= 96:
            results[3] += 1
        elif res <= int(suc):
            results[0] += 1
        else:
            results[1] += 1
    
    await ctx.send(f'> 回数:{num} | 成功値:{suc}\n`成功:{results[0]} | 失敗:{results[1]}`\n`クリティカル:{results[2]} | ファンブル:{results[3]}`')
 
@bot.command(name="farm")
async def farm(ctx, base:str='0', plant:str='0', crit:str='5'):
    if base == '0' or plant == '0':
        await ctx.send('`> 基本収穫数か、植えた数が間違っています。`'); return
    elif re.search(r"[^0-9*.()+-d]",base) != None:
        await ctx.send("`> 基本収穫数に不正な文字が含まれています。`"); return
    elif not crit.isdecimal() or int(crit) >= 10:
        await ctx.send('> クリティカル値が不正です。`'); return
    elif int(plant) > 20:
        await ctx.send("`> 20回以上はできません。`"); return
    elif "50" in base:
        await ctx.send("`> 基本収穫数が不正です。`"); return
    facts = [1.0, 1.0]
    results = [0] * int(plant)
    crit = int(crit)
    # 1回目
    tmp = random.randint(1,100)
    if tmp <= 89:
        facts[0] = 1.0
    elif tmp <= 95:
        facts[0] = 0.9
    else:
        facts[0] = 0.6
    # 2回目
    tmp = random.randint(1,100)
    if tmp <= crit:
        facts[1] = 1.2
    elif tmp <= 70:
        facts[1] = 1
    elif tmp <= 95:
        facts[1] = 0.8
    else:
        facts[1] = 0.5
    for i in range(int(plant)):
        results[i] = dice.roll(base)*facts[0]*facts[1]
    res = floor(sum(results))
    await ctx.send(f"> 基本収穫数: {base}\n> 植えた数: {plant}\n> クリティカル値: {crit}\n`合計収穫数: {res}`")
            
  
bot.run("TOKEN")