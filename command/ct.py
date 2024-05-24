import os
import sys

sys.path.append(os.path.join(os.path.dirname("module"), ".."))

from modules.dice_roll import dice


# ?ct クリティカルコマンド
def ct():
    tmp = dice(2)
    if tmp == 1:
        return "```①重撃\n└ダメージ2倍```"
    else:
        return "```②連撃\n└即時追加ターン（追加ターンなのでアイテム使用なども行えます）```"