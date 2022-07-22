import time
from colorama import Fore, Style

def log(msg, colour=None):
    print(f"{colour if colour else ''}{time.ctime()} {msg}{Style.RESET_ALL if colour else ''}")

def join_nicely(col):
    s = ""
    l = len(col)

    for i, e in enumerate(col):
        s += str(e) + (', ' if i <= l - 3 else ' and ' if i == l - 2 else '')

    return s
