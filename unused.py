# 迷宮関連変数
# 配列
checkpoint = [10,20,30,40,50,60,70,80,90]
mid_boss = [5,15,25,35,45,55,65,75,85,95]
tower_mem = {}
tower_floor = {}
maze_party = {}

# データ
maze_enemy = pd.read_excel("data/maze_enemy.xlsx", index_col=0)
maze_data = pd.read_csv("data/maze_data.csv",index_col=0, encoding="utf-8-sig")

conn = sqlite3.connect('lapis.sqlite3')
cur = conn.cursor()

# アイテム図鑑
@bot.command(name="item")
async def items(ctx,item_id:str = "nan"):
    if item_id == "nan": return
    #<!-- IDで取得 -->
    if item_id.isdecimal() == True:
        if int(item_id) not in item_ids: await ctx.send("`>アイテムIDが存在しません。`"); return
        res = await get_item(item_id)
        item_embed=discord.Embed(title=f"**❖{res[1]}**", description=f"`—————————————————————————————`\n{res[2]}")
        item_embed.add_field(name="**❑用途**", value=f"> {res[3]}", inline=False)
        if res[4] == 0:
            item_embed.add_field(name="**❑NPC売却価格**", value=f"> 売却不可", inline=True)
        else:
            item_embed.add_field(name="**❑NPC売却価格**", value=f"> {res[4]}", inline=True)
        if res[5] == 0:
            item_embed.add_field(name="**❑PC最低取引価格**", value=f"> {res[5]}", inline=True)
        else:
            item_embed.add_field(name="**❑PC最低取引価格**", value=f"> 取引不可", inline=True)
        item_embed.set_footer(text="Powered by Kairos | Lapis Memory Item Database")
        await ctx.send(embed=item_embed)
    #<!-- 文字列で検索 -->
    else:
        res = await search_item(item_id)
        if res == "null": await ctx.send("`>検索結果: 0件`"); return
        send_msg = "`>アイテム検索結果:`"
        for parts in res:
            send_msg += f"\n`{parts[1]}：{parts[0]}`"
        await ctx.send(send_msg)
        
async def get_item(item_id):
    cur.execute(f"SELECT * FROM items WHERE ID = '{item_id}'")
    item_data = cur.fetchall()
    if not item_data:
        return "null"
    else:
        return item_data[0]

async def search_item(item_name):
    cur.execute(f"SELECT Name, ID FROM items WHERE Name LIKE '%{item_name}%'")
    item_data = cur.fetchall()
    if not item_data:
        return "null"
    else:
        return item_data
    
# 歌のコマンド
@bot.command(name="sch")
async def scherzo(ctx):
    tmp = int(dice.roll("1d3+0"))-1
    res = scherzo_list[tmp]
    await ctx.send(f"**>無想のScherzo:**\n`{res}`")
   
# 称号コマンド
@bot.command(name="achive")
async def achivment(ctx, com:str = "show", id:str = "0"):
    global achiv_data, user_achiv, achiv_ids
    usr_id = ctx.author.id
    # 所持称号を表示
    if com == "show":
        send_msg = ""
        if usr_id not in user_achiv.index:
            await ctx.send("`>未登録です`")
            return
        ids = user_achiv.loc[usr_id,['achiv_id']]
        ids = (ids.values.tolist()[0]).split(",")
        for i in range(len(ids)):   # 所有する称号の数分繰り返し
            acv_id = int(ids[i])
            name = achiv_data.iloc[acv_id-1,0]
            effect = achiv_data.iloc[acv_id-1,1]
            send_msg += (f"`ID:{acv_id}` | **`{name}`**\n**└[ {effect} ]**\n")
        await ctx.send(f"<@{ctx.author.id}>の所有する称号:")
        await ctx.send(send_msg)
    # 称号を追加
    elif com == "add":
        if id.isdecimal() == False:
            await ctx.send("`>IDが不正です`")
            return
        if id not in achiv_ids:
            await ctx.send("`>IDが存在しません`")
            return
        # UIDが存在しない場合、一番下に追記
        if usr_id not in user_achiv.index:
            print(user_achiv.index)
            with open('data/user_achiv.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow([usr_id, id])
        else:
            ids = user_achiv.loc[usr_id,['achiv_id']]
            ids = ids.values.tolist()[0]
            if id in ids:
                await ctx.send("`>既に所有済みです`")
                return
            late_ids = ids + f",{id}"
            user_achiv.loc[usr_id,['achiv_id']] = late_ids
            user_achiv.to_csv('data/user_achiv.csv')
    
        user_achiv = pd.read_csv("data/user_achiv.csv",index_col=0,encoding="utf-8-sig")
        print("上書き保存しました")
        await ctx.send(f"`>ID:{id}の称号を追加しました`")
            

    # 称号を切り替え
    elif com == "set":
        if id == "nan":
            await ctx.send("`>称号IDが不正です`")
            return
    
    # 称号削除    
    elif com == "del":
        if id.isdecimal() == False: # IDが数字か
            await ctx.send("`>IDが不正です`")
            return
        if id not in achiv_ids:     # 称号IDがない
            await ctx.send("`>IDが存在しません`")
            return
        if usr_id not in user_achiv.index: # データ登録がされていない
            await ctx.send("`>称号登録を行っていません`")
            return
        ids = user_achiv.loc[usr_id,['achiv_id']]
        ids = ids.values.tolist()[0]
        if id in ids:
            late_ids = ids.replace(f",{id}","")
            user_achiv.loc[usr_id,['achiv_id']] = late_ids
            user_achiv.to_csv('data/user_achiv.csv')
            await ctx.send(f"`>ID:{id}の称号を削除しました`")
            user_achiv = pd.read_csv("data/user_achiv.csv",index_col=0,encoding="utf-8-sig")
        else:
            await ctx.send("`>存在しません`")
    # それ以外
    else:
        await ctx.send("`>コマンドが不正です`")
        return   
       
# 迷宮コマンド
@bot.command(name="maze")
async def backrooms(ctx, command:str="forward"):
    global maze_data, maze_party
    channelID = ctx.channel.id         # コマンドが実行されたチャンネルIDを取得
    user_id = ctx.author.id             # UIDを取得
    #<-- 開始 -->
    if command == "start":
        await ctx.send(f"`>チャンネル: {ctx.channel.name}`\n`>迷宮への侵入準備を開始します。`")
        maze_party[channelID] = [1,1] # 階層/カウンタ
        return
    #<-- 参加 -->
    elif command == "join":
        tmp_list = maze_party[channelID]
        if user_id in tmp_list:
            await ctx.send("`>既に参加済みです。`")
            return
        tmp_list.append(user_id)
        maze_party[channelID] = tmp_list
        await ctx.send("`>パーティーに参加しました。`")
        return
    #<-- 前進 -->
    elif command == "forward":
        #<-- チャンネルIDが存在しない場合 -->
        if channelID not in maze_party:
            await ctx.send("`>迷宮へ侵入していません。`")
            return
        area = maze_party[channelID][0]
        if area == 6:
            await ctx.send("`>迷宮の最上層に出た。そこに広がる景色は、どこまでも続く無数の尖塔に埋め尽くされた世界だった。`\n> [ ここから脱出しよう ]")
            return
        situation = maze_data.iloc[0,random.randrange(17)]   #0
        scale = maze_data.iloc[1,random.randrange(3)]        #1
        if scale == "-":
            scale = scale.replace("-","")
        bright = maze_data.iloc[2,random.randrange(9)]       #2
        effect = maze_data.iloc[3,random.randrange(18)]      #3
        #objects_type = maze_data.iloc[4,random.randrange(11)]#4
        light_type = maze_data.iloc[5,random.randrange(5)]   #5
        location = maze_data.iloc[area+5,random.randrange(26)]    #6/7/8/9/10 (26種類)
        light = maze_data.iloc[area+10,random.randrange(7)]        #11/12/13/14/15 (7種類)
        flavour = maze_data.iloc[21,random.randrange(21)]     #21/22/23/24/25 (17種類)
        
        send_msg = f"`{situation}{scale}{location}だ。`\n`{light_type}{light}が{bright}照らしている。`\n`{flavour}`"
        #<-- アイテム入手の場合 -->
        if "入手" in effect:
            item = maze_data.iloc[area+15,random.randrange(94)] # 16/17/18/19/20 (94種類)
            send_msg += f"\n> **`>効果: {item}を入手`**"
        elif "回復" in effect:
            send_msg += f"\n> **`>効果: {effect}`**"
        elif "接敵" in effect:
            send_msg += f"\n> **`>効果: {effect}`**"
        else:
            send_msg += f"\n> **`>効果: {effect}`**"
        
        await ctx.send(send_msg)
        maze_party[channelID][1] += 1
        #<-- カウンタが50を超えたら -->
        if maze_party[channelID][1] > 50:
            maze_party[channelID][1] = 1  # カウンタをリセット
            maze_party[channelID][0] += 1 # 階層を1上昇
    #<-- 接敵 -->
    elif command == "encount":
        enemy_selc = random.randrange(4)
        enemy_data = maze_enemy.iloc[enemy_selc,maze_party[channelID][0]-1]
        if "_x000D_" in enemy_data:
            enemy_data = enemy_data.replace("_x000D_"," ")
        num = len(maze_party[channelID])-2
        if num < 1:
            num = 1
        #num = 1
        await ctx.send(enemy_data+f"ｘ{num}体")
    #<-- 脱出 -->
    elif command == "exit":
        await ctx.send("`>迷宮を脱出しました。`")
        del maze_party[channelID]    