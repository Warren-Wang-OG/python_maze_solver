# https://boot.dev/project/2b266bb4-2262-49c0-b6d1-75cd8c5e8be8/5b463508-3371-4df9-8a5c-228431af21b9
from __future__ import annotations # type hinting stuff
from tkinter import Tk, BOTH, Canvas

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
    def __init__(self, top_left_corner : Point, bottom_right_corner : Point):
        # init all 4 walls to be on, order: (left, right, top, down)
        self.walls = [1,1,1,1]
        # top left x/y, bottom right x/y
        self.top_left_corner = top_left_corner
        self.bottom_right_corner = bottom_right_corner
        # extras
        self.win = None
    
    def draw(self, canvas : Canvas, fill_color : str):
        for i,wall in enumerate(self.walls):
            if wall == 1:
                # draw the wall
                # left
                if i == 0:
                    l = Line(self.top_left_corner, Point(self.top_left_corner.x, self.bottom_right_corner.y))
                    l.draw(canvas, fill_color)
                # right
                elif i == 1:
                    l = Line(Point(self.bottom_right_corner.x, self.top_left_corner.y), self.bottom_right_corner)
                    l.draw(canvas, fill_color)
                # top
                elif i == 2:
                    l = Line(self.top_left_corner, Point(self.bottom_right_corner.x, self.top_left_corner.y))
                    l.draw(canvas, fill_color)
                # bottom
                else:
                    l = Line(Point(self.top_left_corner.x, self.bottom_right_corner.y), self.bottom_right_corner)
                    l.draw(canvas, fill_color)

    def draw_move(self, to_cell : Cell, canvas : Canvas, undo=False):
        '''
        draw a line from the center of self to the center of to_cell
        '''
        fill_color = "red"
        from_point = Point((self.top_left_corner.x+self.bottom_right_corner.x)//2, (self.top_left_corner.y+self.bottom_right_corner.y)//2)
        to_point = Point((to_cell.top_left_corner.x+to_cell.bottom_right_corner.x)//2, (to_cell.top_left_corner.y+to_cell.bottom_right_corner.y)//2)
        l = Line(from_point, to_point)
        l.draw(canvas, fill_color)

        


class Window:
    def __init__(self, width : int, height : int):
        self.width = width
        self.height = height
        self.root = Tk()
        self.root.title("Maze Solver")
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.canvas = Canvas() 
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
        cell.draw(self.canvas, fill_color)

class Maze:
    def __init__(self):
        pass

def main():
    win = Window(800, 600)
    # create some lines
    win.draw_line(Line(Point(0,0), Point(20,20)), "black")
    win.draw_line(Line(Point(20,20), Point(50,20)), "red")
    # create some cells
    c0 = Cell(Point(50, 50), Point(60, 60))
    c1 = Cell(Point(70, 50), Point(80, 60))
    c2 = Cell(Point(100, 100), Point(110, 110))
    c2.walls[3] = 0
    c3 = Cell(Point(70, 60), Point(80, 70))

    win.draw_cell(c0, "black")
    win.draw_cell(c1, "blue")
    win.draw_cell(c2, "black")
    win.draw_cell(c3, "black")

    # draw some moves (lines from one cell to the other)
    c0.draw_move(c1, win.canvas)
    c1.draw_move(c3, win.canvas)
    
    win.wait_for_close()

main()