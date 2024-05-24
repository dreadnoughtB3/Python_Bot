import os
import sys

sys.path.append(os.path.join(os.path.dirname("module"), ".."))

from modules.dice_roll import dice


# ?fn ファンブルコマンド
def fn():
    tmp = dice(3)
    if tmp == 1:
        return "```①深傷\n└1ターン行動不能、敵からの被ダメージ2倍```"
    elif tmp == 2:
        return "```②破損\n└武器の耐久値-2(90以上の武器耐久減少もプラスすると-3されます)、3ターン攻撃不可（攻撃不可になるのは事前に行使していた技能となる。魔法は魔法技能全て）```"
    else:
        return "```③挫折\n└2ターン全行動不可能```"