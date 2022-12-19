# https://boot.dev/project/2b266bb4-2262-49c0-b6d1-75cd8c5e8be8/5b463508-3371-4df9-8a5c-228431af21b9
from __future__ import annotations # type hinting stuff
from tkinter import Tk, BOTH, Canvas
import time
import random

class Point:
    def __init__(self, x=0, y=0):
        # x=0, y=0 top left corner
        self.x = x
        self.y = y

class Line:
    def __init__(self, pt1 : Point, pt2 : Point):
        self.pt1 = pt1
        self.pt2 = pt2

    def draw(self, canvas : Canvas, fill_color : str):
        canvas.create_line(
            self.pt1.x, self.pt1.y, self.pt2.x, self.pt2.y, fill=fill_color, width=2
        )
        canvas.pack()

class Cell:
    def __init__(self, top_left_corner : Point, bottom_right_corner : Point, win : Window = None):
        # init all 4 walls to be on, order: (left, right, top, down)
        self.walls = [1,1,1,1]
        # top left x/y, bottom right x/y
        self.top_left_corner = top_left_corner
        self.bottom_right_corner = bottom_right_corner
        # extras
        self.win = win
        self.canvas = win.canvas if win != None else None
        if self.canvas == None:
            print("NOTE: self.canvas is None")
        # for traversal
        self.visited = False
    
    def draw(self, fill_color : str):
        # left
        if self.walls[0] == 1 and self.canvas != None:
            l = Line(self.top_left_corner, Point(self.top_left_corner.x, self.bottom_right_corner.y))
            l.draw(self.canvas, fill_color)
        else:
            l = Line(self.top_left_corner, Point(self.top_left_corner.x, self.bottom_right_corner.y))
            l.draw(self.canvas, "white")

        # right
        if self.walls[1] == 1 and self.canvas != None:
            l = Line(Point(self.bottom_right_corner.x, self.top_left_corner.y), self.bottom_right_corner)
            l.draw(self.canvas, fill_color)
        else:
            l = Line(Point(self.bottom_right_corner.x, self.top_left_corner.y), self.bottom_right_corner)
            l.draw(self.canvas, "white")

        # top
        if self.walls[2] == 1 and self.canvas != None:
            l = Line(self.top_left_corner, Point(self.bottom_right_corner.x, self.top_left_corner.y))
            l.draw(self.canvas, fill_color)
        else:
            l = Line(self.top_left_corner, Point(self.bottom_right_corner.x, self.top_left_corner.y))
            l.draw(self.canvas, "white")

        # bottom
        if self.walls[3] == 1 and self.canvas != None:
            l = Line(Point(self.top_left_corner.x, self.bottom_right_corner.y), self.bottom_right_corner)
            l.draw(self.canvas, fill_color)
        else:
            l = Line(Point(self.top_left_corner.x, self.bottom_right_corner.y), self.bottom_right_corner)
            l.draw(self.canvas, "white")
            

    def draw_move(self, to_cell : Cell, undo=False):
        '''
        draw a line from the center of self to the center of to_cell
        '''
        fill_color = "red"
        from_point = Point((self.top_left_corner.x+self.bottom_right_corner.x)//2, (self.top_left_corner.y+self.bottom_right_corner.y)//2)
        to_point = Point((to_cell.top_left_corner.x+to_cell.bottom_right_corner.x)//2, (to_cell.top_left_corner.y+to_cell.bottom_right_corner.y)//2)
        l = Line(from_point, to_point)
        l.draw(self.canvas, fill_color)

        


class Window:
    def __init__(self, width : int, height : int):
        self.width = width
        self.height = height
        self.root = Tk()
        self.root.title("Maze Solver")
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.canvas = Canvas() 
        self.canvas.configure(bg="white")
        self.canvas.pack()# pack canvas to be ready to be drawn
        self.is_running = False
    
    def redraw(self):
        self.root.update_idletasks()
        self.root.update()

    def wait_for_close(self):
        self.is_running = True
        while(self.is_running):
            self.redraw()

    def close(self):
        self.is_running = False

    def draw_line(self, line : Line, fill_color : str):
        line.draw(self.canvas, fill_color)

    def draw_cell(self, cell : Cell, fill_color : str):
        cell.draw(fill_color)



class Maze:
    '''
    2d grid of cells
    '''
    def __init__(self, x : int, y : int, rows : int, cols : int, cell_x_size : int, cell_y_size : int, win : Window = None, seed : int = None):
        self.rows = rows
        self.cols = cols
        self.cell_x_size = cell_x_size
        self.cell_y_size = cell_y_size
        self.win = win
        self._cells = [[None for j in range(cols)] for i in range(rows)]
        # anchor top left point of entire maze
        self._x = x
        self._y = y
        # randomness
        if seed != None:
            random.seed(seed)

        self._create_cells()
        self._break_entrance_and_exit()
        self._break_walls_r(0,0)

    def _create_cells(self):
        '''
        fill self._cells with (rows x cols) cells
        then, draw cells
        '''
        for i in range(self.rows):
            for j in range(self.cols):
                c = Cell(None, None, self.win)
                self._cells[i][j] = c
                self._draw_cells(i,j)

    def _draw_cells(self, i : int, j : int):
        top_left_x = self._x + self.cell_x_size * j
        top_left_y = self._y + self.cell_y_size * i
        top_left = Point(top_left_x, top_left_y)
        bot_right = Point(top_left_x + self.cell_x_size, top_left_y + self.cell_y_size)
        self._cells[i][j].top_left_corner = top_left
        self._cells[i][j].bottom_right_corner = bot_right
        if self.win != None:
            self.win.draw_cell(self._cells[i][j], "black")
            self._animate()
        else:
            print("NOTE: win is None")
        

    def _animate(self):
        # refresh canvas
        self.win.redraw()
        time.sleep(0.05)
        # time.sleep(0.5)


    def _break_entrance_and_exit(self):
        '''
        redraw top left cell's left wall to be white
        redraw bottom right cell's right wall to be white
        cells (n x m)
        '''
        entrance_cell = self._cells[0][0]
        n = len(self._cells)-1
        m = len(self._cells[0])-1
        exit_cell = self._cells[n][m]
        # left right top down
        entrance_cell.walls[2] = 0
        exit_cell.walls[3] = 0
        # call _draw_cells
        self._draw_cells(0,0)
        self._draw_cells(n,m)
    

    # TODO: this may not be doing everything that I claim it should be doing?
    def _is_valid_cell(self, i, j):
        '''
        helper function to determine if coordinates are valid in our maze
        returns True if valid
        else False
        '''
        # index bounds 
        i_max = self.rows
        j_max = self.cols

        if i > i_max or j > j_max:
            return False

        if i < 0 or j < 0:
            return False

        return True



    # FIXME: not working as intended, out of bounds indexing issues

    def _break_walls_r(self, i, j):
        # mark current cell as visited
        self._cells[i][j].visited = True
        
        # possible routes from here (left, right, top, down)
        # what happens when reaching the edges tho? don't want to access cells that don't exist, will get error
        # make sure are within bounds

        # top, down, left, right
        directions = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]
        # check bounds and keep only unvisited cells
        for tup in directions:
            if not self._is_valid_cell(tup[0], tup[1]):
                directions.remove(tup)
        
        for tup in directions:
            i_, j_ = tup[0], tup[1]
            if self._cells[i_][j_].visited == True:
                directions.remove(tup)
        
        print(f"{directions=}")
        
        while len(directions) > 0:
            # need to check if any nodes have already been visited, remove then from directions
            for tup in directions:
                i_, j_ = tup[0], tup[1]
                if self._cells[i_][j_].visited == True:
                    directions.remove(tup)

            # pick a random direction among the unvisited nodes
            x = random.randint(0, len(directions)-1)
            tup = directions[x]
            i_,j_ = tup[0], tup[1]
            print(f"chosen ({i_=},{j_=})")

            # don't need to mark new cell as visited, recursive call will mark it
            # self._cells[i_][j_].visited = True

            directions.remove(tup)
            # break down wall between current cell (i,j) and (i_,j_)
            # need to know if to the left, right, top, or bottom
            # walls order: (left, right, top, down)
            
            # left
            if j_ < j:
                # break right wall of other cell
                self._cells[i_][j_].walls[1] = 0
            # right
            elif j_ > j:
                # break left wall of other cell
                self._cells[i_][j_].walls[0] = 0
            # top
            elif i_ < i:
                # break bottom wall of other cell
                self._cells[i_][j_].walls[3] = 0
            # below
            else:
                # break top wall of other cell
                self._cells[i_][j_].walls[2] = 0

            self._draw_cells(i_, j_)
            # recursively go to cell
            self._break_walls_r(i_, j_)






def main():
    win = Window(800, 600)
    ## create some lines
    #win.draw_line(Line(Point(0,0), Point(20,20)), "black")
    #win.draw_line(Line(Point(20,20), Point(50,20)), "red")
    ## create some cells
    #c0 = Cell(Point(50, 50), Point(60, 60))
    #c1 = Cell(Point(70, 50), Point(80, 60))
    #c2 = Cell(Point(100, 100), Point(110, 110))
    #c2.walls[3] = 0
    #c3 = Cell(Point(70, 60), Point(80, 70))

    #win.draw_cell(c0, "black")
    #win.draw_cell(c1, "blue")
    #win.draw_cell(c2, "black")
    #win.draw_cell(c3, "black")

    ## draw some moves (lines from one cell to the other)
    #c0.draw_move(c1, win.canvas)
    #c1.draw_move(c3, win.canvas)

    # testing Maze
    # start_x, start_y, rows, cols, size_x, size_y
    maze = Maze(10,10,4,5,25,25,win, seed=0)
    win.wait_for_close()

if __name__ == "__main__":
    main()