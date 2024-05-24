import csv, os, sys, asyncio

sys.path.append(os.path.join(os.path.dirname("module"), ".."))
sys.path.append(os.path.join(os.path.dirname("data"), ".."))

from modules.dice_roll import dice
from modules.judge import is_range

seed_list = ["ニンジン","ジャガイモ","ハーブ","花","トマト"]

# ?gather 採取コマンド
async def gather(kind, count):
    # ファイル読み込み
    with open("data/gather.csv", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for data in reader:
            # 場所指定が一致している場合
            if kind == data["kind"]:
                area = "採取場所：" + data["area"]  # 場所名称
                info = data["info"]  # 採取物情報
                result = await collection_module(info, kind, count)  # 採取結果
                return area + "\n" + result
        # 場所が一致しない場合
        return "```対応する採取場所がありません```"

# ?fell 伐採コマンド
async def fell(kind, count):
    # ファイル読み込み
    with open("data/fell.csv") as f:
        reader = csv.DictReader(f)
        for data in reader:
            # 場所指定が一致している場合
            if kind == data["kind"]:
                area = "伐採場所：" + data["area"]  # 場所名称
                info = data["info"]  # 伐採物情報
                result = await collection_module(info, kind, count)  # 採取結果
                return area + "\n" + result
        # 場所が一致しない場合
        return "```対応する伐採場所がありません```"


# ?mine 採掘コマンド
async def mine(kind, count):
    # ファイル読み込み
    with open("data/mine.csv", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for data in reader:
            # 場所指定が一致している場合
            if kind == data["kind"]:
                area = "採掘場所：" + data["area"]  # 場所名称
                info = data["info"]  # 採掘物情報
                result = await collection_module(info, kind, count)  # 採取結果
                return area + "\n" + result
        # 場所が一致しない場合
        return "```対応する採掘場所がありません```"


async def fishing(kind, count, skill):
    with open("data/fishing.csv", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for data in reader:
            if kind == data["kind"]:    # IDが一致した行があれば
                area = "釣り場所：" + data["area"] # 場所名称を設定
                info = data["info"]              # データを取得
                args = info.split("/")
                item = [0] * len(args)
                cnt = 0
                for i in range(count):           # カウント回繰り返し
                    if dice(100) <= skill:       # 成功したら
                        cnt += 1 
                        tmp = dice(6)
                        tmp2 = dice(6)
                        for j, arg in enumerate(args):
                            if is_range(tmp, arg.split("：")[0]):
                                item[j] += 1
                        for j, arg in enumerate(args):
                            if is_range(tmp2, arg.split("：")[0]):
                                item[j] += 1
                result = "```"
                for j, arg in enumerate(args):
                    result += "{}×{} ".format(arg.split("：")[1], item[j])
                result += f"| 回数:{count} | 成功回数:{cnt}```"
                return area + "\n" + result
                    
        return "```対応する釣り場所がありません```" 
    

# 採取物の情報を与えて判定をおこなう
async def collection_module(info, kind, count):
    args = info.split("/")
    item = [0] * len(args)
    # count回の繰り返し
    for i in range(count):
        tmp = dice(100)
        for j, arg in enumerate(args):
            if is_range(tmp, arg.split("：")[0]):
                item[j] += 1
    # もし種があれば
    if args[2] == "10-80：種(1d5)" and item[2] != 0:
        seeds = [0,0,0,0,0]
        for i in range(item[2]):
            seeds[dice(5)-1] += 1
        item.extend(seeds)
    # 成果物出力
    result = "```"
    for j, arg in enumerate(args):
        if item[j] != 0:
            result += "{}×{} ".format(arg.split("：")[1], item[j])
    if args[2] == "10-80：種(1d5)" and item[2] != 0:
        result += "|\n>種の結果: "
        for i in range(5):
            if item[i+6] != 0:
                result += f"{seed_list[i]}×{item[i+6]} "
    result += "| 回数:{}```".format(count)
    return result