import unittest
from main import Maze


'''
I've always hated writing unittests...
'''

class Tests(unittest.TestCase):
    def test_maze_create_cells(self):
        num_cols = 12
        num_rows = 10
        m1 = Maze(0,0,num_rows,num_cols,10,10)
        # ensure dimensions are correct
        self.assertEqual(len(m1._cells), num_cols)
        self.assertEqual(len(m1._cells[0]), num_rows)
        # ensure entrance and exit are set
        self.assertEqual(m1._cells[0][0].walls[2], 0)
        self.assertEqual(m1._cells[len(m1._cells)-1][len(m1._cells[0])-1].walls[3], 0)


if __name__ == "__main__":
    unittest.main()