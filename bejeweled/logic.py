#!/usr/bin/env python

"""
Game solver.
The artificial intelligence part is here.
"""

import config as cfg
from grab import grab_screen
import Image


class Board(object):
    """
    For representing the game board (default size: 8 x 8). 
    """
    def __init__(self):
        """
        Create the empty board (a matrix).
        """
        self.board = [ [0 for _ in range(cfg.SIZE)] for _ in range(cfg.SIZE) ]
        
    def __getitem__(self, key):
        return self.board[key]
    
    def __setitem__(self, key, value):
        self.board[key] = value
        
    def show(self):
        """
        Show the board (for debugging).
        """
        for i in range(cfg.SIZE):
            for j in range(cfg.SIZE):
                print self.board[i][j],
            print
        
    def simplify(self):
        """
        RGB values are replaced by small positive numbers.
        """
        board = self.board
        cnt = 1
        d = {}
        for i in range(cfg.SIZE):
            for j in range(cfg.SIZE):
                if not d.has_key(board[i][j]):
                    d[board[i][j]] = cnt
                    cnt += 1
                board[i][j] = d[board[i][j]] 
        
    def read_board(self, fname=None):
        """
        Fill the matrix according to the game board.
        * grab the screen
        * get the middle pixel of each cell and store its RGB value
        * simplify the matrix (RGB values are replaced by small positive integers)
        """
        if not cfg.TEST:
            im = grab_screen()
        else:
            if cfg.TEST:
                fname = '/tmp/problem.png'
            im = Image.open(fname)
        pix = im.load()
        for i in range(cfg.SIZE):
            for j in range(cfg.SIZE):
                x = cfg.board_right + j * cfg.cell_size + (cfg.cell_size / 2)
                y = cfg.board_down + i * cfg.cell_size + (cfg.cell_size / 2)
                self.board[i][j] = pix[x,y]
    #            mouse.move(cfg.relx(x),cfg.rely(y))
    #            print '# pos:', (x,y), '; color:', pix[x,y] 
    #            sleep(.2)
    #        print
        #
        self.simplify()


class Bejeweled(object):
    """
    Game logic. This is the solver.
    """
    def __init__(self):
        """
        Initialisation. Create the empty board.
        """
        self.board = Board()
        
    def read_board(self):
        """
        Update the board.
        """
        self.board.read_board()
        
    def show_board(self):
        """
        Show the board (for debugging).
        """
        self.board.show()
        
    ####################
        
    # operators
        
    def same_gem_up_left(self, curr, color):
        """
        Is there a same gem in the up left position?
        """
        x, y = curr
        return x-1 >= 0 and y-1 >= 0 and self.board[x-1][y-1] == color
    
    def same_gem_down_left(self, curr, color):
        x, y = curr
        return x+1 < cfg.SIZE and y-1 >= 0 and self.board[x+1][y-1] == color
    
    def same_gem_up_right(self, curr, color):
        x, y = curr
        return x-1 >= 0 and y+1 < cfg.SIZE and self.board[x-1][y+1] == color
    
    def same_gem_down_right(self, curr, color):
        x, y = curr
        return x+1 < cfg.SIZE and y+1 < cfg.SIZE and self.board[x+1][y+1] == color
    
    def same_gem_two_left(self, curr, color):
        x, y = curr #@UnusedVariable
        return y-2 >= 0 and self.board[x][y-2] == color
    
    def same_gem_two_right(self, curr, color):
        x, y = curr #@UnusedVariable
        return y+2 < cfg.SIZE and self.board[x][y+2] == color
    
    def same_gem_two_up(self, curr, color):
        x, y = curr #@UnusedVariable
        return x-2 >= 0 and self.board[x-2][y] == color
    
    def same_gem_two_down(self, curr, color):
        x, y = curr #@UnusedVariable
        return x+2 < cfg.SIZE and self.board[x+2][y] == color
    
    ####################
        
    def search_horizontally_double(self, row_nb):
        """
        In the current row, find this pattern: gem, gem.
        """
        row = self.board[row_nb]
        for i in range(cfg.SIZE-1):
            if row[i] == row[i+1]:
                (c1, c2) = self.verify_horizontal_double((row_nb, i), (row_nb, i+1), row[i])
                if c1:
                    return (c1, c2)
        # else
        return (None, None)
    
    def search_horizontally_double_plus_one(self, row_nb):
        """
        In the current row, find this pattern: gem, gem, anything, gem.
        """
        row = self.board[row_nb]
        for i in range(cfg.SIZE-1):
            if row[i] == row[i+1]:
                (c1, c2) = self.verify_horizontal_double_plus_one((row_nb, i), (row_nb, i+1), row[i])
                if c1:
                    return (c1, c2)
        # else
        return (None, None)
    
    def search_horizontally_hole(self, row_nb):
        """
        In the current row, find this pattern: gem, anything, gem.
        """
        row = self.board[row_nb]
        for i in range(cfg.SIZE-2):
            if row[i] == row[i+2]:
                (c1, c2) = self.verify_horizontal_hole((row_nb, i), (row_nb, i+2), row[i])
                if c1:
                    return (c1, c2)
        # else
        return (None, None)
    
    def search_vertically_double(self, row_nb):
        """
        For each stone in the row, verify if the following pattern
        holds vertically: gem, gem.
        """
        if row_nb > 0:
            row = self.board[row_nb]
            for i in range(cfg.SIZE):
                if row[i] == self.board[row_nb-1][i]:
                    (c1, c2) = self.verify_vertical_double((row_nb, i), (row_nb-1, i), row[i])
                    if c1:
                        return (c1, c2)
        # else        
        return (None, None)
    
    def search_vertically_double_plus_one(self, row_nb):
        """
        For each stone in the row, verify if the following pattern
        holds vertically: gem, gem, anything, gem.
        """
        if row_nb > 0:
            row = self.board[row_nb]
            for i in range(cfg.SIZE):
                if row[i] == self.board[row_nb-1][i]:
                    (c1, c2) = self.verify_vertical_double_plus_one((row_nb, i), (row_nb-1, i), row[i])
                    if c1:
                        return (c1, c2)
        # else        
        return (None, None)
    
    def search_vertically_hole(self, row_nb):
        """
        For each stone in the row, verify if the following pattern
        holds vertically: gem, anything, gem.
        """
        if row_nb >= 2:
            row = self.board[row_nb]
            for i in range(cfg.SIZE):
                if row[i] == self.board[row_nb-2][i]:
                    (c1, c2) = self.verify_vertical_hole((row_nb, i), (row_nb-2, i), row[i])
                    if c1:
                        return (c1, c2)
        # else
        return (None, None)
    
    ####################
                
    def verify_horizontal_double(self, one, two, color):
        """
        'one' and 'two' are two gems next to each other with the same color.
        Verify if there is a gem around them to make a triple.
        """
        if self.same_gem_up_left(one, color):
            print 'up left'
            x, y = one
            click1 = (x, y-1)
            click2 = (x-1, y-1)
            return (click1, click2)
        if self.same_gem_down_left(one, color):
            print 'down left'
            x, y = one
            click1 = (x, y-1)
            click2 = (x+1, y-1)
            return (click1, click2)
        if self.same_gem_up_right(two, color):
            print 'up right'
            x, y = two
            click1 = (x, y+1)
            click2 = (x-1, y+1)
            return (click1, click2)
        if self.same_gem_down_right(two, color):
            print 'down right'
            x, y = two
            click1 = (x, y+1)
            click2 = (x+1, y+1)
            return (click1, click2)
        if self.same_gem_two_left(one, color):
            print 'two left'
            x, y = one
            click1 = (x, y-1)
            click2 = (x, y-2)
            return (click1, click2)
        if self.same_gem_two_right(two, color):
            print 'two right'
            x, y = two
            click1 = (x, y+1)
            click2 = (x, y+2)
            return (click1, click2)
        # else
        return (None, None)
    
    def verify_horizontal_double_plus_one(self, one, two, color):
        """
        'one' and 'two' are two gems next to each other with the same color.
        Verify if there is a gem in their rows with the same color that is only
        two stones away. If there exists one, then verify if there is another gem 
        with the same color to pair four or five gems.
        """
        if self.same_gem_two_left(one, color):
        #{
            if self.same_gem_up_left(one, color):
                print 'up left'
                x, y = one
                click1 = (x, y-1)
                click2 = (x-1, y-1)
                return (click1, click2)
            if self.same_gem_down_left(one, color):
                print 'down left'
                x, y = one
                click1 = (x, y-1)
                click2 = (x+1, y-1)
                return (click1, click2)
        #}
        
        if self.same_gem_two_right(two, color):
        #{
            if self.same_gem_up_right(two, color):
                print 'up right'
                x, y = two
                click1 = (x, y+1)
                click2 = (x-1, y+1)
                return (click1, click2)
            if self.same_gem_down_right(two, color):
                print 'down right'
                x, y = two
                click1 = (x, y+1)
                click2 = (x+1, y+1)
                return (click1, click2)
        #}
        # else
        return (None, None)
    
    def verify_horizontal_hole(self, one, two, color):
        """
        'one' and 'two' are two gems in a row with a different gem between them.
        Verify if there is a gem in the previous or next row with which they could
        form a triple.
        """
        if self.same_gem_up_right(one, color):
            print 'up right', one, two
            x, y = one
            click1 = (x, y+1)
            click2 = (x-1, y+1)
            return (click1, click2)
        if self.same_gem_down_right(one, color):
            print 'down right', one, two
            x, y = one
            click1 = (x, y+1)
            click2 = (x+1, y+1)
            return (click1, click2)
        # else
        return (None, None)
    
    def verify_vertical_double(self, one, two, color):
        """
        'one' and 'two' are two gems below each other with the same color.
        Verify if there is a gem around them to make a triple.
        """
        if self.same_gem_down_left(one, color):
            print 'down left'
            x, y = one
            click1 = (x+1, y)
            click2 = (x+1, y-1)
            return (click1, click2)
        if self.same_gem_down_right(one, color):
            print 'down right'
            x, y = one
            click1 = (x+1, y)
            click2 = (x+1, y+1)
            return (click1, click2)
        if self.same_gem_two_down(one, color):
            print 'two down'
            x, y = one
            click1 = (x+1, y)
            click2 = (x+2, y)
            return (click1, click2)
        if self.same_gem_up_left(two, color):
            print 'up left'
            x, y = two
            click1 = (x-1, y)
            click2 = (x-1, y-1)
            return (click1, click2)
        if self.same_gem_up_right(two, color):
            print 'up right'
            x, y = two
            click1 = (x-1, y)
            click2 = (x-1, y+1)
            return (click1, click2)
        if self.same_gem_two_up(two, color):
            print 'two up'
            x, y = two
            click1 = (x-1, y)
            click2 = (x-2, y)
            return (click1, click2)
        # else
        return (None, None)
    
    def verify_vertical_double_plus_one(self, one, two, color):
        """
        'one' and 'two' are two gems below each other with the same color.
        Verify if there is a gem in their column with the same color that is only
        two stones away. If there exists one, then verify if there is another gem 
        with the same color to pair four or five gems.
        """
        if self.same_gem_two_down(one, color):
        #{
            if self.same_gem_down_left(one, color):
                print 'down left'
                x, y = one
                click1 = (x+1, y)
                click2 = (x+1, y-1)
                return (click1, click2)
            if self.same_gem_down_right(one, color):
                print 'down right'
                x, y = one
                click1 = (x+1, y)
                click2 = (x+1, y+1)
                return (click1, click2)
        #}
        
        if self.same_gem_two_up(two, color):
        #{
            if self.same_gem_up_left(two, color):
                print 'up left'
                x, y = two
                click1 = (x-1, y)
                click2 = (x-1, y-1)
                return (click1, click2)
            if self.same_gem_up_right(two, color):
                print 'up right'
                x, y = two
                click1 = (x-1, y)
                click2 = (x-1, y+1)
                return (click1, click2)
        #}
        # else
        return (None, None)
    
    def verify_vertical_hole(self, one, two, color):
        """
        'one' and 'two' are two gems in a column with a different gem between them.
        Verify if there is a gem in the previous or next column with which they could
        form a triple.
        """
        if self.same_gem_up_left(one, color):
            print 'up left'
            x, y = one
            click1 = (x-1, y)
            click2 = (x-1, y-1)
            return (click1, click2)
        if self.same_gem_up_right(one, color):
            print 'up right'
            x, y = one
            click1 = (x-1, y)
            click2 = (x-1, y+1)
            return (click1, click2)
        # else
        return (None, None)