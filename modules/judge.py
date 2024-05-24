# xがrangeに入っているか
def is_range(x, range):
    tmp = range.split("-")
    if len(tmp) == 2:
        if int(tmp[0]) <= x and x <= int(tmp[1]):
            return True
    elif len(tmp) == 1:
        if int(tmp[0]) == x:
            return True
    return False