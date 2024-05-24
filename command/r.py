import os
import sys
import re
from lark import Lark
from lark import Transformer

sys.path.append(os.path.join(os.path.dirname("data"), ".."))

from modules.dice_roll import dice, multi_dice


# ?r ダイスロールコマンド
def r(*args):
    result = ""
    # 引数0　1D100を振る
    if len(args) == 0:
        result += "```(1D100) ＞ {}```".format(dice(100))
    # 引数1　nDm+αを振る
    elif len(args) == 1:
        if re.search("[^0-9d\.\(\)\+\-\*/<>=]+", args[0]) == None:
            with open("data/str_grammar.lark") as grammar:
                parser = Lark(grammar.read(), start="compeq")
                tree = parser.parse(args[0])
            process = StrTransformer().transform(tree)
            with open("data/calc_grammar.lark") as grammar:
                parser = Lark(grammar.read(), start="compeq")
                tree = parser.parse(process)
            value = CalcTransformer().transform(tree)
            result += "```({}) ＞ {} ＞ {}```".format(args[0].replace("d", "D"), process, round(value, 2))
        else:
            result = "```式に不適切な文字が含まれています```"
    # 引数2
    elif len(args) == 2:
        if args[1].startswith("x"):
            print("xから始まる")
            print(args[0])
            if re.search("[^0-9d\.\(\)\+\-\*/<>=]+", args[0]) == None:
            # if re.search(r"[^0-9*.()+-d<>=]",args[0]) == None:
                print("正常なダイス")
                result += "```"
                # 繰り返し部分
                for i in range(int(args[1][1:])):
                    with open("data/str_grammar.lark") as grammar:
                        parser = Lark(grammar.read(), start="compeq") #comp
                        tree = parser.parse(args[0])
                    process = StrTransformer().transform(tree)
                    with open("data/calc_grammar.lark") as grammar:
                        parser = Lark(grammar.read(), start="compeq") #comp
                        tree = parser.parse(process)
                    value = CalcTransformer().transform(tree)
                    result += "#{} : ({}) ＞ {} ＞ {}\n".format(i, args[0].replace("d", "D"), process, round(value, 2))
                result += "```"
            else:
                result = "```式に不適切な文字が含まれています```"
    return result


class StrTransformer(Transformer):
    def lesseq(self, tree):
        result = "{}<={}".format(tree[0], tree[1])
        return result

    def less(self, tree):
        result = "{}<{}".format(tree[0], tree[1])
        return result

    def moreeq(self, tree):
        result = "{}>={}".format(tree[0], tree[1])
        return result

    def more(self, tree):
        result = "{}>{}".format(tree[0], tree[1])
        return result
    
    def add(self, tree):
        result = "{}+{}".format(tree[0], tree[1])
        return result
      
    def sub(self, tree):
        result = "{}-{}".format(tree[0], tree[1])
        return result
      
    def mul(self, tree):
        result = "{}*{}".format(tree[0], tree[1])
        return result
      
    def div(self, tree):
        result = "{}/{}".format(tree[0], tree[1])
        return result
      
    def dice(self, tree):
        tmp = multi_dice(eval(str(tree[0])), eval(str(tree[1])))
        result = "{}{}".format(sum(tmp), tmp)
        return result
      
    def bracket(self, tree):
        result = "({})".format(tree[0])
        return result
      
    def number(self, tree):
        result = int(tree[0]) if tree[0].isdecimal() else float(tree[0])
        return result


class CalcTransformer(Transformer):
    def lesseq(self, tree):
        result = 1 if tree[0] <= tree[1] else 0
        return result

    def less(self, tree):
        result = 1 if tree[0] < tree[1] else 0
        return result

    def moreeq(self, tree):
        result = 1 if tree[0] >= tree[1] else 0
        return result

    def more(self, tree):
        result = 1 if tree[0] > tree[1] else 0
        return result
    
    def add(self, tree):
        result = tree[0] + tree[1]
        return result
      
    def sub(self, tree):
        result = tree[0] - tree[1]
        return result
      
    def mul(self, tree):
        result = tree[0] * tree[1]
        return result
      
    def div(self, tree):
        result = tree[0] / tree[1]
        return result
      
    def roll(self, tree):
        result = tree[0]
        return result

    def inner(self, tree):
        return None
      
    def bracket(self, tree):
        result = tree[0]
        return result
      
    def number(self, tree):
        result = int(tree[0]) if tree[0].isdecimal() else float(tree[0])
        return result