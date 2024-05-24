import os
import sys
from lark import Lark
from lark import Transformer

sys.path.append(os.path.join(os.path.dirname("data"), ".."))

from modules.dice_roll import dice, multi_dice


# 個別ダイスコマンド
def b(*args):
    result = ""
    # 引数1　1D100を振り，成功か判定する
    if len(args) == 1:
        count = {"成功":0, "失敗":0, "クリティカル":0, "ファンブル":0}
        tmp = dice(100)
        # 成功
        if tmp < int(args[0]):
            # クリティカル
            if tmp >= int(args[0])-5:
                count["クリティカル"] += 1
            # 通常成功
            else:
                count["成功"] += 1
        # 失敗
        else:
            # ファンブル
            if tmp > 95:
                count["ファンブル"] += 1
            # 通常失敗
            else:
                count["失敗"] += 1
              
        result += "```(1D100) ＞ {} ＞ {}```".format(tmp, count)
    # 引数2　1Dmをn個振り，成功か判定する
    elif len(args) == 2:
        count = {"成功":0, "失敗":0, "クリティカル":0, "ファンブル":0}
        dice_info = args[0].split("d")
        tmp = multi_dice(int(dice_info[0]), int(dice_info[1]))
        for ind_dice in tmp:
            # 成功
            if ind_dice <= int(args[1]):
                # クリティカル
                if ind_dice >= int(args[1])-5:
                    count["クリティカル"] += 1
                # 通常成功
                else:
                    count["成功"] += 1
            # 失敗
            else:
                # ファンブル
                if ind_dice > 95:
                    count["ファンブル"] += 1
                # 通常失敗
                else:
                    count["失敗"] += 1
              
        result += "```({}) ＞ {} ＞ {}```".format(args[0].replace("d", "D"),tmp, count)

    return result