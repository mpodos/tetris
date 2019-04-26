import unittest
import tetris
import tkinter


class TestTetris(unittest.TestCase):

    def test_line_deletion(self):
        tmp = tkinter.Frame(borderwidth=3, relief="solid")
        ttrs = tetris.Tetris(tmp, width=400, height=600,
                             borderwidth=3, relief="solid", bg="white",
                             rows=24, columns=16, cell=25)
        # fill line
        for j in range(ttrs.columns):
            ttrs.Matrix[j][ttrs.rows-1] = "blue"

        figure = tetris.Figure()
        figure.Cells.append((1, ttrs.rows-1))

        count = ttrs.FindCompleteLines(figure)

        self.assertEqual(count, 1)
        for j in range(ttrs.columns):
            self.assertEqual(ttrs.Matrix[j][ttrs.rows-1], "gray")

    def test_hold_figure(self):
        tmp = tkinter.Frame(borderwidth=3, relief="solid")
        ttrs = tetris.Tetris(tmp, width=400, height=600,
                             borderwidth=3, relief="solid", bg="white",
                             rows=24, columns=16, cell=25)

        figure = tetris.Figure()
        ttrs.HoldFigure(figure)
        for cell in figure.Cells:
            self.assertEqual(ttrs.Matrix[cell[0]][cell[1]], figure.Color)

    def test_remove_figure(self):
        tmp = tkinter.Frame(borderwidth=3, relief="solid")
        ttrs = tetris.Tetris(tmp, width=400, height=600,
                             borderwidth=3, relief="solid", bg="white",
                             rows=24, columns=16, cell=25)

        figure = tetris.Figure()
        ttrs.HoldFigure(figure)
        ttrs.RemoveFigure(figure)
        for cell in figure.Cells:
            self.assertEqual(ttrs.Matrix[cell[0]][cell[1]], "gray")

    def test_figure_move_down(self):
        figure = tetris.Figure()

        cells = figure.MoveDown()
        for idx, cell in enumerate(figure.Cells):
            self.assertEqual(cells[idx][0], cell[0])
            self.assertEqual(cells[idx][1], cell[1]+1)

    def test_game_over(self):
        app = tetris.Game(Title="Tetris")
        app.SecondScreen()
        self.assertNotEquals(app._job, None)

        for i in range(app.Control.Canvas.rows):
            for j in range(app.Control.Canvas.columns):
                app.Control.Canvas.Matrix[j][i] = "red"
        app.Gravity()

        self.assertEquals(app._job, None)


if __name__ == '__main__':
    unittest.main()
