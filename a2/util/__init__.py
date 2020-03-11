import os
import sys
import time
import math
from functools import lru_cache

@lru_cache(maxsize=128)
def log_n(num_visits):
    """Calculates the log of the number of visits, this is cached"""
    return math.log(num_visits)

@lru_cache(maxsize=256)
def uct(reward, num_visits, Cp, ln_N):
    """Calculates the UCT value for the provided parameters"""
    return (reward / num_visits) + Cp * math.sqrt((2 * ln_N / num_visits))

def cls():
    """Clears the screen, depending on the OS level call, this is merely a small utility function"""
    if os.name == 'nt':
        temp = os.system('cls')
    else:
        temp = os.system('clear')

# Based on https://stackoverflow.com/questions/3160699/python-progress-bar
def progressbar(it, desc="", position=None, size=None, start=0, total=None, file = sys.stdout):

    count = total or len(it)

    def show(j, ips, sec_elapsed_total):
        _, columns = os.popen('stty size', 'r').read().split()

        # Terminal width - description length - spacing - completed count - spacing - total count - spacing - time - ips
        width = size or (int(columns) - len(desc) - 5 - len(str(start + j)) - 1 - len(str(count)) - 2 - 11 - 12) 

        min_elapsed, sec_elapsed = divmod(sec_elapsed_total, 60)
        sec_total = math.ceil(count / ips) - sec_elapsed_total if ips > 0 else 0
        min_rem, sec_rem = divmod(sec_total, 60)
        
        x = int(width * (start + j) / count)
        if position: moveto(file, position)
        file.write("%s: |%s%s| %i/%i [%02d:%02d<%02d:%02d, %.2fit/s]\r" % (desc, "█" * x, " " * (width - x), start + j, count, min_elapsed, sec_elapsed, min_rem, sec_rem, ips))
        file.flush()
        if position: moveto(file, -position)

    start_time = time.time()
    show(0, 0, 0)
    for i, item in enumerate(it):
        yield item
        sec_elapsed = time.time() - start_time
        ips = (i + 1) / sec_elapsed
        show(i + 1, ips, sec_elapsed)
    
    file.write("\n")
    file.flush()

# Based on https://github.com/tqdm/tqdm/blob/master/tqdm/std.py#L1401
def moveto(fp, n):
    fp.write(str('\n' * n + ('' if (os.name == 'nt') else '\x1b[A') * -n))
    fp.flush()