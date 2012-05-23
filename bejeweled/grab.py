#!/usr/bin/env python

"""
Take a screenshot of the screen.

# from grab import grab_screen
"""

import pyscreenshot as ImageGrab
import Image
from time import sleep, time
import config as cfg


def grab_screen():
    """
    Grab just the game area.
    """
    if not cfg.TEST:
        im = ImageGrab.grab(bbox=(cfg.x0, cfg.y0, cfg.x0+cfg.width, cfg.y0+cfg.height))
        return im
    else:   # TEST
        fname = '/tmp/problem.png'
        im = Image.open(fname)
        return im
 
def main():
    im = grab_screen()
    fname = '/tmp/full_snap__' + str(int(time())) + '.png'
    im.save(fname)
    print '# grabbed to', fname
 
#############################################################################
 
if __name__ == '__main__':
    sleep(3)
    main()