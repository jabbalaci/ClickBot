#!/usr/bin/env python

"""
Open http://www.digbejeweled.com/ in Chromium.
Let zoom be 100%.
In config.py, set x0 and y0 to the top left corner of the game (a blue pixel).
"""

from time import sleep
import config as cfg
import mouse
from mouse import click_to
from logic import Bejeweled
from grab import grab_screen
from random import shuffle


def unselect_if_selected(solver):
    """
    It can happen that a cell gets selected alone (green frame around it).
    Unselect it.
    """
    GREEN = (0, 255, 0)

    def is_green(x, y):
        return pix[x + 2,  y + 2] == GREEN or \
               pix[x + 34, y + 2] == GREEN or \
               pix[x + 2,  y + 34] == GREEN or \
               pix[x + 34, y + 34] == GREEN
    #
    pix = grab_screen().load()
    for i in range(cfg.SIZE):
        for j in range(cfg.SIZE):
            x = cfg.board_right + j * cfg.cell_size
            y = cfg.board_down + i * cfg.cell_size
            if is_green(x, y):
                x += (cfg.cell_size / 2)
                y += (cfg.cell_size / 2)
                mouse.click_to((cfg.relx(x), cfg.rely(y)))
                return


def game_window():
    """
    Check if you still have the game window.

    If you switch away from the game window, the script will stop.
    Thus you have a chance to get back the mouse :)
    """
    # pixel position => pixel color (RGB)
    pixel_colors = {
        (118, 36):   (228, 20, 197),
        (93, 262):   (104, 60, 188),
        (146, 322):  (231, 222, 132),
        (113, 286):  (0, 255, 255)
    }
    pix = grab_screen().load()
    for k, v in pixel_colors.iteritems():
        if pix[k[0], k[1]] != v:
#            print '# oops, different window detected => stop'
            return False
    # else
    return True


def game_over():
    """
    Return true if the game is over.
    """
    pix = grab_screen().load()
    return pix[234, 77] == (224, 17, 255)

##########


def play():
    """
    Play (or resume) a game.
    """
    click_to((cfg.relx(416), cfg.rely(293)))


def start_new_game():
    """
    Start a new game.
    """
    click_to((cfg.relx(61), cfg.rely(123)))
    sleep(.2)
    click_to((cfg.relx(187), cfg.rely(284)))


def pause():
    """
    Pause the game. Call play() to resume.
    """
    click_to((cfg.relx(70), cfg.rely(313)))


def move_mouse_away():
    mouse.mousePos((cfg.x0, cfg.y0))

##########


def click_on_cell(cell):
    """
    cell contains the matrix coordinates of a gem. Click on it.
    """
#    print '# clicking on', cell
    y1, x1 = cell
    x = cfg.board_right + x1 * cfg.cell_size + (cfg.cell_size / 2)
    y = cfg.board_down + y1 * cfg.cell_size + (cfg.cell_size / 2)
#    print '# position: ', ((cfg.relx(x), cfg.rely(y)))
    click_to((cfg.relx(x), cfg.rely(y)))


def click_on_cells(cell1, cell2, solver):
    """
    Click on two neighboring cells to switch them.
    """
    click_on_cell(cell1)
    sleep(.1)
    click_on_cell(cell2)


def get_percent():
    pix = grab_screen().load()
    start = 155
    end = 406
    line = 325
    green = (0, 247, 0)
    #
    cnt = 0
    for col in xrange(start, end + 1):
        if pix[col, line] == green:
            cnt += 1
    #
    return float(cnt) / (end - start) * 100


def search_moves(solver):
    """
    Search for possible moves.
    """
    # the different cases
    funcs = [solver.search_horizontally_double_plus_one,
             solver.search_vertically_double_plus_one,
             solver.search_horizontally_double,
             solver.search_horizontally_hole,
             solver.search_vertically_double,
             solver.search_vertically_hole]

    # start at the bottom row and go upwards
    row_nb = cfg.SIZE - 1
    found = False
    while row_nb >= 0:  # 7,6,...,0
        shuffle(funcs)
        solver.read_board()

        while get_percent() > 95.0:
            sleep(.5)
        #
        if not game_window() or game_over():
            return
        #
        print row_nb
        # Let's try all possible cases. If we made a move, go on (break out of this loop).
        for f in funcs:
            (cell1, cell2) = f(row_nb)
            if cell1:
                found = True
                click_on_cells(cell2, cell1, solver)
                break

        # If we made a move in the previous loop.
        if found:
            row_nb = cfg.SIZE - 1   # restart from the bottom
            found = False
        else:    # no move was found in the row => check the previous row
            row_nb -= 1


def main():
    """
    It has the game loop.
    """
    solver = Bejeweled()
    sleep(2)
    play()
    sleep(1.5)

    while not game_over() and game_window():
        unselect_if_selected(solver)
        search_moves(solver)

    print '__END__'

#############################################################################

if __name__ == "__main__":
    if not cfg.TEST:
        main()
    else:
        solver = Bejeweled()
        fname = '/tmp/problem.png'
        solver.board.read_board(fname)
        solver.show_board()
        print
        search_moves(solver)
