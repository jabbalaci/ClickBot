#!/usr/bin/env python

"""
Play http://www.google.com/doodles/hurdles-2012 .
Code based on https://gist.github.com/3287367 . 
"""

import time
from autopy import key


def play():
    print '# switch to Hurdles 2012 in your browser (you have 3 seconds)'
    time.sleep(3)
    s = time.time()
    while time.time() - s < 15:
        for _ in range(15):
            key.tap(key.K_LEFT)
            key.tap(key.K_RIGHT)
        key.tap(' ')
        time.sleep(0.1)

#############################################################################

if __name__ == "__main__":
    play()