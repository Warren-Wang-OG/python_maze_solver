from __future__ import annotations  # type hinting stuff

import random
import time
from tkinter import Canvas, StringVar, Tk, ttk


class Point:
    def __init__(self, x=0, y=0):
        # x=0, y=0 top left corner
        self.x = x
        self.y = y


class Line:
    def __init__(self, pt1: Point | None, pt2: Point | None):
        self.pt1 = pt1
        self.pt2 = pt2

    def draw(self, canvas: Canvas, fill_color: str):
        assert self.pt1 is not None
        assert self.pt2 is not None
        canvas.create_line(
            self.pt1.x, self.pt1.y, self.pt2.x, self.pt2.y, fill=fill_color, width=2
        )
        canvas.pack()


class Cell:
    def __init__(
        self,
        top_left_corner: Point,
        bottom_right_corner: Point,
        canvas: Canvas,
    ):
        # init all 4 walls to be on, order: (left, right, top, down)
        self.walls = [1, 1, 1, 1]
        # top left x/y, bottom right x/y
        self.top_left_corner = top_left_corner
        self.bottom_right_corner = bottom_right_corner
        # extras
        self.canvas = canvas
        # for traversal
        self.visited = False
        # for bfs
        self.bfs_parent: tuple[int, int] = (-1, -1)

    def draw(self, fill_color: str):
        # left
        if self.walls[0] == 1 and self.canvas != None:
            l = Line(
                self.top_left_corner,
                Point(self.top_left_corner.x, self.bottom_right_corner.y),
            )
            l.draw(self.canvas, fill_color)
        else:
            l = Line(
                self.top_left_corner,
                Point(self.top_left_corner.x, self.bottom_right_corner.y),
            )
            l.draw(self.canvas, "white")

        # right
        if self.walls[1] == 1 and self.canvas != None:
            l = Line(
                Point(self.bottom_right_corner.x, self.top_left_corner.y),
                self.bottom_right_corner,
            )
            l.draw(self.canvas, fill_color)
        else:
            l = Line(
                Point(self.bottom_right_corner.x, self.top_left_corner.y),
                self.bottom_right_corner,
            )
            l.draw(self.canvas, "white")

        # top
        if self.walls[2] == 1 and self.canvas != None:
            l = Line(
                self.top_left_corner,
                Point(self.bottom_right_corner.x, self.top_left_corner.y),
            )
            l.draw(self.canvas, fill_color)
        else:
            l = Line(
                self.top_left_corner,
                Point(self.bottom_right_corner.x, self.top_left_corner.y),
            )
            l.draw(self.canvas, "white")

        # bottom
        if self.walls[3] == 1 and self.canvas != None:
            l = Line(
                Point(self.top_left_corner.x, self.bottom_right_corner.y),
                self.bottom_right_corner,
            )
            l.draw(self.canvas, fill_color)
        else:
            l = Line(
                Point(self.top_left_corner.x, self.bottom_right_corner.y),
                self.bottom_right_corner,
            )
            l.draw(self.canvas, "white")

    def draw_move(self, to_cell: Cell, undo=False):
        """
        draw a line from the center of self to the center of to_cell
        """
        fill_color = "red"
        from_point = Point(
            (self.top_left_corner.x + self.bottom_right_corner.x) // 2,
            (self.top_left_corner.y + self.bottom_right_corner.y) // 2,
        )
        to_point = Point(
            (to_cell.top_left_corner.x + to_cell.bottom_right_corner.x) // 2,
            (to_cell.top_left_corner.y + to_cell.bottom_right_corner.y) // 2,
        )
        l = Line(from_point, to_point)
        if undo:
            l.draw(self.canvas, "gray")
        else:
            l.draw(self.canvas, fill_color)


class Maze:
    """
    2d grid of cells
    """

    def __init__(
        self,
        x: int,
        y: int,
        rows: int,
        cols: int,
        cell_x_size: int,
        cell_y_size: int,
        win: Window,
        seed: float,
    ):
        self.rows = rows
        self.cols = cols
        self.cell_x_size = cell_x_size
        self.cell_y_size = cell_y_size
        self.win = win
        self._temp_point = Point()
        self._cells: list[list[Cell]] = [
            [Cell(self._temp_point, self._temp_point, win.canvas) for _ in range(cols)]
            for _ in range(rows)
        ]
        # anchor top left point of entire maze
        self._x = x
        self._y = y
        random.seed(seed)
        self._animate_speed = 0.0

    def _create_cells(self):
        """
        fill self._cells with (rows x cols) cells
        then, draw cells
        """

        for i in range(self.rows):
            for j in range(self.cols):
                c = Cell(self._temp_point, self._temp_point, self.win.canvas)
                self._cells[i][j] = c
                self._draw_cells(i, j)

    def _draw_cells(self, i: int, j: int):
        top_left_x = self._x + self.cell_x_size * j
        top_left_y = self._y + self.cell_y_size * i
        top_left = Point(top_left_x, top_left_y)
        bot_right = Point(top_left_x + self.cell_x_size, top_left_y + self.cell_y_size)
        self._cells[i][j].top_left_corner = top_left
        self._cells[i][j].bottom_right_corner = bot_right
        self._cells[i][j].draw("black")
        self._animate()

    def _animate(self):
        self.win.redraw()  # refresh canvas
        if self._animate_speed != 0:
            time.sleep(
                self._animate_speed
            )  # slow down to allow for seeing the animation

    def _break_entrance_and_exit(self):
        """
        redraw top left cell's left wall to be white
        redraw bottom right cell's right wall to be white
        cells (n x m)
        """
        entrance_cell = self._cells[0][0]
        n = len(self._cells) - 1
        m = len(self._cells[0]) - 1
        exit_cell = self._cells[n][m]
        # left right top down
        entrance_cell.walls[2] = 0
        exit_cell.walls[3] = 0
        # call _draw_cells
        self._draw_cells(0, 0)
        self._draw_cells(n, m)

    def _is_valid_cell(self, i, j):
        """
        helper function to determine if coordinates are valid in our maze
        returns True if valid
        else False
        """
        # index bounds
        i_max = self.rows
        j_max = self.cols
        if i >= i_max or j >= j_max:
            return False
        if i < 0 or j < 0:
            return False
        return True

    def _break_walls_r(self, i, j):
        # mark current cell as visited
        self._cells[i][j].visited = True

        # possible routes from here: top, down, left, right
        directions = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]

        # check bounds and keep only unvisited cells
        tmp = []  # keep track of elements that might need removal
        for tup in directions:
            if not self._is_valid_cell(tup[0], tup[1]):
                tmp.append(tup)
        for e in tmp:
            directions.remove(e)
        tmp.clear()

        # remove already visited cells
        for tup in directions:
            i_, j_ = tup[0], tup[1]
            if self._cells[i_][j_].visited == True:
                tmp.append(tup)
        for e in tmp:
            directions.remove(e)
        tmp.clear()

        while True:
            # need to check if any nodes have already been visited, remove then from directions
            for tup in directions:
                i_, j_ = tup[0], tup[1]
                if self._cells[i_][j_].visited == True:
                    tmp.append(tup)

            for e in tmp:
                directions.remove(e)
            tmp.clear()

            # pick a random direction among the unvisited nodes
            if len(directions) > 1:
                x = random.randint(0, len(directions) - 1)
            elif len(directions) == 1:  # one elem
                x = 0
            else:
                # no more elems, no more cells to traverse to from here
                return
            tup = directions[x]
            i_, j_ = tup[0], tup[1]

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

            # draw other cell
            self._draw_cells(i_, j_)
            # recursively go to other cell
            self._break_walls_r(i_, j_)

    def _reset_cells_visited(self):
        # reset all cells visited property to false
        for i in range(self.rows):
            for j in range(self.cols):
                self._cells[i][j].visited = False

    def _has_wall_blocking(self, i, j, i_, j_):
        """
        return True if there is a wall in between
        the cell (i,j) and (i_,j_)
        else return False for no wall blocking
        walls order: (left, right, top, down)
        """
        if i_ < i and j_ == j:
            # other cell is above, check other cell down wall
            if self._cells[i_][j_].walls[3] == 1:
                return True
            return False
        elif i_ > i and j_ == j:
            # other cell is below, check other cell top wall
            if self._cells[i_][j_].walls[2] == 1:
                return True
            return False
        elif i_ == i and j_ < j:
            # other cell is to the left, check other cell right wall
            if self._cells[i_][j_].walls[1] == 1:
                return True
            return False
        elif i_ == i and j_ > j:
            # other cell is to the right, check other cell left wall
            if self._cells[i_][j_].walls[0] == 1:
                return True
            return False
        else:
            # invalid cell!!
            print(
                f"Invalid cell encountered in _has_wall_blocking({i=},{j=},{i_=},{j_=})"
            )
            return True

    def get_valid_neighbors(self, i: int, j: int) -> list[tuple[int, int]]:
        # not at end, continue working thru the maze
        # start with all directions
        # top, down, left, right
        directions = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]

        # ignore cells that:
        # 1. Have a wall between you and it
        # 2. Have already been visited
        # in other words, start with only considering cells that have no wall blocking and hasn't been visited yet
        tmp = []

        # keep only valid cells (cells inside the maze)
        for tup in directions:
            if not self._is_valid_cell(tup[0], tup[1]):
                tmp.append(tup)
        for e in tmp:
            directions.remove(e)
        tmp.clear()

        # check if open path (no wall)
        for tup in directions:
            i_, j_ = tup[0], tup[1]
            if self._has_wall_blocking(i, j, i_, j_):
                tmp.append(tup)
        for e in tmp:
            directions.remove(e)
        tmp.clear()

        # check visited, remove all cells that have already been visited
        for tup in directions:
            if self._cells[tup[0]][tup[1]].visited:
                tmp.append(tup)
        for e in tmp:
            directions.remove(e)

        return directions

    def dfs_solve(self):
        """
        return True if maze is solved, else False
        """
        if self._dfs_solve_r():
            print("Maze solved!")
        else:
            print("Could not solve Maze.")

    def _dfs_solve_r(self, i=0, j=0):
        """
        return True if maze is solved, else False
        goal cell is at (i,j) = (self.rows-1, self.cols-1)
        start is default (i,j) = (0,0)

        """
        # draw
        self._animate()

        # mark current cell as visited
        self._cells[i][j].visited = True

        # immediately end if at goal cell
        if i == self.rows - 1 and j == self.cols - 1:
            return True

        # get valid neighbors
        neighbors = self.get_valid_neighbors(i, j)

        # recursively travel to the valid cells
        for tup in neighbors:
            i_, j_ = tup[0], tup[1]
            # draw a move between curr cell and i_,j_
            self._cells[i][j].draw_move(self._cells[i_][j_])
            # recurse to other cell
            if self._dfs_solve_r(i_, j_):
                # finished!
                return True
            # not finished
            # draw undo move
            self._cells[i][j].draw_move(self._cells[i_][j_], undo=True)

        # all neighbors failed
        return False

    def wall_follower_solve(self):
        """
        Follows the right hand wall -- only works for simply connected mazes
        """
        # define direction facing (0 = right, 1 = left, up = 2, down = 3)
        curr_facing_direction = 3

        if self._wall_follower_r(i=0, j=0, curr_facing_direction=curr_facing_direction):
            print("Maze solved")
        else:
            print("Maze not solved.")

    def _wall_follower_r(self, i: int, j: int, curr_facing_direction: int):
        # draw
        self._animate()

        # mark current cell as visited
        self._cells[i][j].visited = True

        # immediately end if at goal cell
        if i == self.rows - 1 and j == self.cols - 1:
            return True

        # get valid neighbors
        neighbors = self.get_valid_neighbors(i, j)

        # establish priotity hierarchy, in this order:
        # 1. right, 2. left, 3. forward, 4. backward
        # relative to the curr_facing_direction

        # store ptr to valid direction, if existing, in order of established hierarchy
        inds: list[tuple[int, int] | None] = [None for _ in range(4)]
        for tup in neighbors:
            i_, j_ = tup[0], tup[1]
            if curr_facing_direction == 2:  # facing up
                # right
                if j_ > j:
                    inds[0] = tup
                # left
                elif j_ < j:
                    inds[1] = tup
                # forward (abs up)
                elif i_ < i:
                    inds[2] = tup
                # backward (abs down)
                elif i_ > i:
                    inds[3] = tup
                else:
                    raise Exception("unexpected state reached")

            elif curr_facing_direction == 0:  # facing right
                # right (abs down)
                if i_ > i:
                    inds[0] = tup
                # left (abs up)
                elif i_ < i:
                    inds[1] = tup
                # forward (abs right)
                elif j_ > j:
                    inds[2] = tup
                # backward (abs left)
                elif j_ < j:
                    inds[3] = tup
                else:
                    raise Exception("unexpected state reached")

            elif curr_facing_direction == 3:  # facing down
                # right (abs left)
                if j_ < j:
                    inds[0] = tup
                # left (abs right)
                elif j_ > j:
                    inds[1] = tup
                # forward (abs down)
                elif i_ > i:
                    inds[2] = tup
                # backward (abs up)
                elif i_ < i:
                    inds[3] = tup
                else:
                    raise Exception("unexpected state reached")

            elif curr_facing_direction == 1:  # facing left
                # right (abs up)
                if i_ < i:
                    inds[0] = tup
                # left (abs down)
                elif i_ > i:
                    inds[1] = tup
                # forward (abs left)
                elif j_ < j:
                    inds[2] = tup
                # backward (abs right)
                elif j_ > j:
                    inds[3] = tup
                else:
                    raise Exception("unexpected state reached")

            else:
                raise Exception("unexpected state reached")

        # go in order of hierarchy (right, left, forward, back)
        for foo, tup in enumerate(inds):
            if tup == None:
                continue

            i_, j_ = tup[0], tup[1]

            self._cells[i][j].draw_move(self._cells[i_][j_])

            # traverse to i_,j_ with the new current facing direction based on that cell's direction relative to
            # current cell direction
            # absolute directions mapping: (0 = right, 1 = left, up = 2, down = 3)

            if curr_facing_direction == 2:  # facing up (abs)
                if foo == 0:  # right (abs right)
                    new_direc = 0
                elif foo == 1:  # left (abs left)
                    new_direc = 1
                elif foo == 2:  # forward (abs up)
                    new_direc = 2
                elif foo == 3:  # backward (abs down)
                    new_direc = 3
                else:
                    raise Exception("unexpected state reached")

            elif curr_facing_direction == 0:  # facing right
                if foo == 0:  # right (abs down)
                    new_direc = 3
                elif foo == 1:  # left (abs up)
                    new_direc = 2
                elif foo == 2:  # forward (abs right)
                    new_direc = 0
                elif foo == 3:  # backward (abs left)
                    new_direc = 1
                else:
                    raise Exception("unexpected state reached")

            elif curr_facing_direction == 3:  # facing down
                if foo == 0:  # right (abs left)
                    new_direc = 1
                elif foo == 1:  # left (abs right)
                    new_direc = 0
                elif foo == 2:  # forward (abs down)
                    new_direc = 3
                elif foo == 3:  # backward (abs up)
                    new_direc = 2
                else:
                    raise Exception("unexpected state reached")

            elif curr_facing_direction == 1:  # facing left
                if foo == 0:  # right (abs up)
                    new_direc = 2
                elif foo == 1:  # left (abs down)
                    new_direc = 3
                elif foo == 2:  # forward (abs left)
                    new_direc = 1
                elif foo == 3:  # backward (abs right)
                    new_direc = 0
                else:
                    raise Exception("unexpected state reached")

            else:
                raise Exception("unexpected state reached")

            if self._wall_follower_r(i_, j_, curr_facing_direction=new_direc):
                return True

            # undo move
            self._cells[i][j].draw_move(self._cells[i_][j_], undo=True)

        return False  # maze not solved

    def bfs_solve(self):
        """
        run a bfs from start till find finish, should be "shortest path" if there exists more than one solution

        create a queue of cells, first in line will be cells closest to start cell, end in line will be furthest away from end cell

        at a cell, create distance array of cells that can be visited from this cell (valid cells), then enqueue all of these cells

        enqueue starting cell and its neighbors, making sure to save starting cell as the "bfs_parent" of the neighboring cells
        for cell in queue
            dequeue a cell and visit it
            check if at end cell, if so finish alg
            else
            create list of valid cells to visit from curr cell, update those cells bfs_parents
            enqueue those cells

        backtrack from goal cell to start cell to draw the shortest path from start to fin using bfs_parent
        """

        queue = []

        valid_cells = self.get_valid_neighbors(0, 0)  # starting position (0,0)
        for tup in valid_cells:
            queue.append(tup)
            self._cells[tup[0]][tup[1]].bfs_parent = (0, 0)

        while True:
            next_ = queue.pop(0)
            i_, j_ = next_[0], next_[1]
            self._cells[i_][j_].visited = True

            parent_i, parent_j = (
                self._cells[i_][j_].bfs_parent[0],
                self._cells[i_][j_].bfs_parent[1],
            )
            self._cells[i_][j_].draw_move(self._cells[parent_i][parent_j], undo=True)
            self._animate()

            # at goal cell
            if i_ == self.rows - 1 and j_ == self.cols - 1:
                break

            # enqueue new neighbors
            valid_cells = self.get_valid_neighbors(i_, j_)
            for tup in valid_cells:
                queue.append(tup)
                self._cells[tup[0]][tup[1]].bfs_parent = (i_, j_)

        # backtrack from the goal cell to the starting cell ?
        while (i_, j_) != (0, 0):
            parent_i, parent_j = (
                self._cells[i_][j_].bfs_parent[0],
                self._cells[i_][j_].bfs_parent[1],
            )
            self._cells[i_][j_].draw_move(self._cells[parent_i][parent_j])
            self._animate()
            i_, j_ = parent_i, parent_j

    def tremaux_solve(self):
        """
        Trémaux's algorithm
        """
        # for as long as you can, go forward, turning right, left or backing up
        # marked_entrances = []  # (i,j)
        # TODO:
        pass

    def pledge_solve(self):
        """
        Pledge algorithm
        """
        # TODO:
        pass


# TODO: implement clearing the maze w/o having to reconstruct everything (save time!) to allow running algs back to back on the same maze faster.


class Window:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.root = Tk()
        self.root.title("Maze Solver")
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        # main container frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        # left control panel
        self.control_frame = ttk.Frame(self.main_frame, padding="5")
        self.control_frame.pack(side="left", fill="y", padx=5, pady=5)

        # right canvas panel
        self.canvas_frame = ttk.Frame(self.main_frame)
        self.canvas_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        self.canvas = Canvas(
            self.canvas_frame, bg="white", width=self.width, height=self.height
        )
        self.canvas.pack(fill="both", expand=True)

        # default vals
        self.rows_var = StringVar(value="10")
        self.cols_var = StringVar(value="10")
        self.seed_var = StringVar(value="-1")
        self.gen_speed_var = StringVar(value="10")
        self.solve_speed_var = StringVar(value="5")
        self.algo_var = StringVar(value="bfs")

        self._create_controls()
        self.animation_running = False
        self.is_running = True

    def _create_controls(self):
        ttk.Label(self.control_frame, text="Rows:").grid(row=0, column=0, sticky="w")
        ttk.Entry(self.control_frame, textvariable=self.rows_var).grid(
            row=0, column=1, padx=5, pady=2
        )

        ttk.Label(self.control_frame, text="Columns:").grid(row=1, column=0, sticky="w")
        ttk.Entry(self.control_frame, textvariable=self.cols_var).grid(
            row=1, column=1, padx=5, pady=2
        )

        ttk.Label(self.control_frame, text="Random Seed:").grid(
            row=2, column=0, sticky="w"
        )
        ttk.Entry(self.control_frame, textvariable=self.seed_var).grid(
            row=2, column=1, padx=5, pady=2
        )

        ttk.Label(self.control_frame, text="Generation Speed [1-10]:").grid(
            row=3, column=0, sticky="w"
        )
        ttk.Entry(self.control_frame, textvariable=self.gen_speed_var).grid(
            row=3, column=1, padx=5, pady=2
        )

        ttk.Label(self.control_frame, text="Solve Speed [1-10]:").grid(
            row=4, column=0, sticky="w"
        )
        ttk.Entry(self.control_frame, textvariable=self.solve_speed_var).grid(
            row=4, column=1, padx=5, pady=2
        )

        ttk.Label(self.control_frame, text="Solving Algorithm:").grid(
            row=5, column=0, columnspan=2, sticky="w", pady=(10, 0)
        )
        ttk.Radiobutton(
            self.control_frame, text="DFS", variable=self.algo_var, value="dfs"
        ).grid(row=6, column=0, columnspan=2, sticky="w")
        ttk.Radiobutton(
            self.control_frame, text="BFS", variable=self.algo_var, value="bfs"
        ).grid(row=7, column=0, columnspan=2, sticky="w")
        ttk.Radiobutton(
            self.control_frame,
            text="Wall Follower",
            variable=self.algo_var,
            value="wall_follower",
        ).grid(row=8, column=0, columnspan=2, sticky="w")

        ttk.Button(
            self.control_frame, text="Create & Solve Maze", command=self.create_maze
        ).grid(row=9, column=0, columnspan=2, pady=(20, 5), sticky="ew")
        # ttk.Button(self.control_frame, text="Reset", command=self.reset).grid(
        #     row=10, column=0, columnspan=2, pady=5, sticky="ew"
        # )

    def create_maze(self):
        if self.animation_running:
            return

        try:
            min_rows = 2
            min_cols = 2
            max_rows = 50
            max_cols = 50
            rows = max(min_rows, min(max_rows, int(self.rows_var.get())))
            cols = max(min_cols, min(max_cols, int(self.cols_var.get())))

            seed = float(self.seed_var.get())
            if seed == -1:
                seed = random.random()
            generation_speed = max(1, min(10, int(self.gen_speed_var.get())))
            solve_speed = max(1, min(10, int(self.solve_speed_var.get())))
            solve_algo = self.algo_var.get()

            self.canvas.delete("all")

            maze = Maze(
                5,  # left margin
                5,  # top margin
                rows,
                cols,
                25,  # cell_x_size
                25,  # cell_y_size
                self,
                seed,
            )
            maze._animate_speed = 0.1 - (generation_speed * 0.01)
            self.animation_running = True
            maze._create_cells()
            maze._break_entrance_and_exit()
            maze._break_walls_r(0, 0)
            maze._reset_cells_visited()

            # set speed for solve animation
            maze._animate_speed = 0.1 - (solve_speed * 0.01)

            # animate solve
            if solve_algo == "dfs":
                maze.dfs_solve()
            elif solve_algo == "bfs":
                maze.bfs_solve()
            elif solve_algo == "wall_follower":
                maze.wall_follower_solve()
            else:
                raise ValueError("Unknown solve algorithm!")
        except Exception:
            pass
        finally:
            self.animation_running = False

    def redraw(self):
        self.root.update_idletasks()
        self.root.update()

    def wait_for_close(self):
        self.is_running = True
        while self.is_running:
            self.redraw()

    def close(self):
        self.animation_running = False
        self.root.destroy()
        self.is_running = False

    def main(self):
        while self.is_running:
            self.redraw()


if __name__ == "__main__":
    Window(800, 600).main()
