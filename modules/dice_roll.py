import random


def dice(num):
    return random.randint(1, num)


def multi_dice(count, num):
    list = []
    for i in range(count):
        list.append(dice(num))
    return list