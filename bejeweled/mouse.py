#!/usr/bin/env python

"""
Mouse actions.

What we need is:
* move the mouse pointer to a given position 
* perform a simple left click
"""

import time
import autopy as ap
from autopy.mouse import LEFT_BUTTON
import config as cfg

def leftClick():
    ap.mouse.click(LEFT_BUTTON)
    time.sleep(.1)
    print "# click"
    
def leftDown():
    ap.mouse.toggle(True, LEFT_BUTTON)
    time.sleep(.1)
    print '# left down'

def leftUp():
    ap.mouse.toggle(False, LEFT_BUTTON)
    time.sleep(.1)
    print '# left release'
    
def move(x, y):
    ap.mouse.move(x, y)
    
def mousePos(pos):
    move(pos[0], pos[1])
 
def click_to(pos):
    mousePos(pos)
    leftClick()
 
def get_pos():
    pos = ap.mouse.get_pos()
    print '# relative pos:', (pos[0]-cfg.x0, pos[1]-cfg.y0)
    
#############################################################################
    
if __name__ == "__main__":
    time.sleep(3)
    get_pos()