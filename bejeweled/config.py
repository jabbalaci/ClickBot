#!/usr/bin/env python

"""
Config. part.

Open http://www.digbejeweled.com/ in your browser and
take a screenshot of the whole screen (under Ubuntu
just press the PrintScreen key). Open the screenshot
in Gimp for instance and figure out the coordinates of
the top left corner of the game (it's a blue pixel).

Customize x0 and y0 below according to the coordinates.
"""

# top left corner, absolute position
# YOU MUST CUSTOMIZE THESE TWO VALUES

# university machine
#x0 = 587
#y0 = 158

# home machine
x0 = 747
y0 = 183

# for debug purposes
TEST = False

#############################################################################
## from here normally you don't need to modify anything
#############################################################################

# board size
SIZE = 8

# bottom right corner, relative to x0 and y0
# normally you don't need to hurt these values
width = 467
height = 341
# top left corner of the board
# relative values to x0 and y0
# normally you don't need to hurt these values
# board_right: from x0, step X pixels to the right
# board_down: from y0, step Y pixels down
board_right = 162
board_down = 18
# width and height of a board cell
cell_size = 36

def relx(x):
    """relative X position"""
    return x0 + x

def rely(y):
    """relative Y position"""
    return y0 + y

#############################################################################

if __name__ == "__main__":
    pass