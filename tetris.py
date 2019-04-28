#!/usr/bin/env python3

from tkinter import Canvas, Label, Button, Frame, \
                    N, E, W, S, PhotoImage, StringVar
import os
import gettext

from random import choice, randint
from pygame import mixer
import datetime

musics = os.listdir("./music")
gettext.install('app', './')


class App(Frame):
    '''Base framed application class'''
    def __init__(self, master=None, Title="Application"):
        '''init App class'''
        Frame.__init__(self, master)
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.title(Title)
        self.grid(sticky=N+E+S+W)
        self.create()

    def create(self):
        '''Create all the widgets'''
        self.bQuit = Button(self, text='Quit', command=self.quit)
        self.bQuit.grid()


class Tetris(Canvas):
    '''Screen class'''
    def __init__(self, master=None, *ap, foreground="black", rows,
                 columns, cell, **an):
        '''Init screen function'''
        self.foreground = StringVar()
        self.foreground.set(foreground)
        Canvas.__init__(self, master, *ap, **an)

        self.rows = rows
        self.columns = columns
        self.cellwidth = cell
        self.cellheight = cell

        self.Matrix = []
        for _ in range(self.columns):
            column_arr = []
            for _ in range(self.rows):
                column_arr.append("gray")
            self.Matrix.append(column_arr)
        self.Rects = {}

    def HoldFigure(self, figure):
        '''Add figure to the matrix function'''
        for cell in figure.Cells:
            x, y = cell

            self.Matrix[x][y] = figure.Color

    def RemoveFigure(self, figure):
        '''Remove figure from  the matrix function'''
        for cell in figure.Cells:
            x, y = cell
            if x > self.columns - 1 or x < 0:
                continue
            if y > self.rows - 1 or y < 0:
                continue

            self.Matrix[x][y] = "gray"

    def Draw(self):
        '''Draw screen'''
        self.Rects = {}
        for column in range(self.columns):
            for row in range(self.rows):
                x1 = column*self.cellwidth
                y1 = row * self.cellheight
                x2 = x1 + self.cellwidth
                y2 = y1 + self.cellheight
                fill = self.Matrix[column][row]
                self.Rects[row, column] = self.create_rectangle(x1, y1,
                                                                x2, y2,
                                                                fill=fill,
                                                                tags="rect")

    def ReDraw(self):
        '''Redraw figure function'''
        for column in range(self.columns):
            for row in range(self.rows):
                self.itemconfig(self.Rects[row, column],
                                fill=self.Matrix[column][row])

    def isValidCoords(self, coords):
        '''Checking whether the cells are busy'''
        for c in coords:
            if c[0] > self.columns - 1 or c[0] < 0:
                return False
            if c[1] > self.rows - 1 or c[1] < 0:
                return False
            if self.Matrix[c[0]][c[1]] != "gray":
                return False
        return True

    def LineComplete(self, i):
        '''Checking whether line is full'''
        for j in range(self.columns):
            if self.Matrix[j][i] == "gray":
                return False
        return True

    def DeleteLine(self, idx):
        '''Delete line from screen function'''
        for j in range(self.columns):
            for i in range(idx, 0, -1):
                if i > -1:
                    self.Matrix[j][i] = self.Matrix[j][i-1]

    def FindCompleteLines(self, figure):
        '''Find completed by figure lines'''
        count = 0
        toDelete = []
        for cell in figure.Cells:
            if self.LineComplete(cell[1]):
                toDelete.append(cell[1])
                count += 1
        toDelete = set(sorted(toDelete))
        for line in toDelete:
            self.DeleteLine(cell[1])
        return count


class Game(App):
    '''Game class'''
    Best = 0
    Score = 0
    Lines = 0

    def CreateFigure(self):
        '''Create figure and next figure finction'''
        if self.NextFigure is not None:
            self.Control.CanvasNext.RemoveFigure(self.NextFigure.Shifted())
            self.CurrentFigure = self.NextFigure
        else:
            self.CurrentFigure = Figure()

        # Draw next figure
        self.NextFigure = Figure()
        self.Control.CanvasNext.HoldFigure(self.NextFigure.Shifted())
        self.Control.CanvasNext.ReDraw()

    def Gravity(self, event=None):
        '''Move the figure one cell down and draw function'''
        self.Control.Canvas.RemoveFigure(self.CurrentFigure)
        coords = self.CurrentFigure.MoveDown()
        if self.Control.Canvas.isValidCoords(coords):
            self.CurrentFigure.Cells = coords
        else:
            self.Control.Canvas.HoldFigure(self.CurrentFigure)
            lines = self.Control.Canvas.FindCompleteLines(self.CurrentFigure)
            self.Lines += lines
            self.Score += 4
            if self.Score > self.Best:
                self.Best = self.Score
            self.Control.ScoreString.set(_("Score: {}").format(self.Score))
            self.Control.BestString.set(_("Best: {}").format(self.Best))
            self.Control.LinesString.set(_("Lines: {}").format(self.Lines))
            self.CreateFigure()
            if self.Control.Canvas.isValidCoords(self.CurrentFigure.Cells):
                self.Control.Canvas.HoldFigure(self.CurrentFigure)
            else:
                self.GameOver()
                return 0
        self.Control.Canvas.HoldFigure(self.CurrentFigure)
        return 1

    def MoveLeft(self, event):
        '''Move the figure one cell left and draw function'''
        self.Control.Canvas.RemoveFigure(self.CurrentFigure)
        coords = self.CurrentFigure.MoveLeft()
        if self.Control.Canvas.isValidCoords(coords):
            self.CurrentFigure.Cells = coords
        self.Control.Canvas.HoldFigure(self.CurrentFigure)
        self.Control.Canvas.ReDraw()

    def MoveRight(self, event):
        '''Move the figure one cell right and draw function'''
        self.Control.Canvas.RemoveFigure(self.CurrentFigure)
        coords = self.CurrentFigure.MoveRight()
        if self.Control.Canvas.isValidCoords(coords):
            self.CurrentFigure.Cells = coords
        self.Control.Canvas.HoldFigure(self.CurrentFigure)
        self.Control.Canvas.ReDraw()

    def Rotate(self, event):
        '''Rotate the figure clockwise and draw function'''
        self.Control.Canvas.RemoveFigure(self.CurrentFigure)
        coords = self.CurrentFigure.Rotate()
        if self.Control.Canvas.isValidCoords(coords):
            self.CurrentFigure.Cells = coords
        self.Control.Canvas.HoldFigure(self.CurrentFigure)
        self.Control.Canvas.ReDraw()

    def FirstScreen(self):
        '''Start screen control'''
        self.Control = Frame(borderwidth=3, relief="solid", bg="white")
        self.Control.grid(row=0, column=0, sticky=N+E+S+W)

        headerIm = PhotoImage(file="tetris.png")
        self.Control.Header = Label(self.Control, image=headerIm,
                                    borderwidth=3, relief="solid",
                                    width=400, bg="white")
        self.Control.Header.image = headerIm
        self.Control.Header.grid(row=0, columnspan=3, sticky=N+E+S+W)

        self.Control.Canvas = Tetris(self.Control, width=400,
                                     height=600, borderwidth=3,
                                     relief="solid", bg="white",
                                     rows=24, columns=16, cell=25)
        self.Control.Canvas.grid(row=1, column=0, rowspan=7)

        self.Control.CanvasNext = Canvas(self.Control, width=150,
                                         height=200, borderwidth=3,
                                         relief="solid", bg="white")
        self.Control.CanvasNext.grid(row=1, column=1, columnspan=2,
                                     sticky=N+E+S+W)

        self.Control = Frame(borderwidth=3, relief="solid", bg="white")
        self.Control.grid(row=0, column=0, sticky=N+E+S+W)

        self.Control.BestString = StringVar()
        self.Control.BestString.set(_("Best: {}").format(self.Best))
        self.Control.ScoreString = StringVar()
        self.Control.ScoreString.set(_("Score: {}").format(self.Score))

        headerIm = PhotoImage(file="tetris.png")
        self.Control.Header = Label(self.Control, image=headerIm,
                                    borderwidth=3, relief="solid",
                                    width=615, bg="white")
        self.Control.Header.image = headerIm
        self.Control.Header.grid(row=0, columnspan=4, sticky=N+E+S+W)

        self.Control.Score = Label(self.Control,
                                   textvariable=self.Control.ScoreString,
                                   borderwidth=3, relief="solid",
                                   font=("Liberation Sans", 14), bg="white")
        self.Control.Score.grid(row=2, column=1, columnspan=2, sticky=N+E+S+W)

        self.Control.NewGame = Button(self.Control, text=_("New Game"),
                                      command=self.SecondScreen, borderwidth=3,
                                      relief="solid",
                                      font=("Liberation Sans", 14), bg="white")
        self.Control.NewGame.grid(row=4, column=1, columnspan=2,
                                  sticky=N+E+S+W)

        self.Control.Best = Label(self.Control,
                                  textvariable=self.Control.BestString,
                                  borderwidth=3,
                                  relief="solid", font=("Liberation Sans", 14),
                                  bg="white")
        self.Control.Best.grid(row=6, column=1, columnspan=2, sticky=N+E+S+W)

        self.Control.Quit = Button(self.Control, text=_("Quit"),
                                   command=self.quit, borderwidth=3,
                                   relief="solid",
                                   font=("Liberation Sans", 14), bg="white")
        self.Control.Quit.grid(row=8, column=1, columnspan=2, sticky=N+E+S+W)

        self.Control.grid_rowconfigure(1, minsize=100)
        self.Control.grid_rowconfigure(3, minsize=50)
        self.Control.grid_rowconfigure(5, minsize=50)
        self.Control.grid_rowconfigure(7, minsize=50)
        self.Control.grid_columnconfigure(0, minsize=35)

    def SecondScreen(self):
        '''Game screen control'''
        self.Score = 0
        self.Lines = 0
        self.Control = Frame(borderwidth=3, relief="solid")
        self.Control.grid(row=0, column=0, sticky=N+E+S+W)

        self.Control.BestString = StringVar()
        self.Control.BestString.set(_("Best: {}").format(self.Best))
        self.Control.ScoreString = StringVar()
        self.Control.ScoreString.set(_("Score: {}").format(self.Score))
        self.Control.LinesString = StringVar()
        self.Control.LinesString.set(_("Lines: {}").format(self.Lines))

        headerIm = PhotoImage(file="tetris.png")
        self.Control.Header = Label(self.Control, image=headerIm,
                                    borderwidth=3, relief="solid",
                                    width=400, bg="white")
        self.Control.Header.image = headerIm
        self.Control.Header.grid(row=0, columnspan=3, sticky=N+E+S+W)

        self.Control.Canvas = Tetris(self.Control, width=400, height=600,
                                     borderwidth=3, relief="solid", bg="white",
                                     rows=24, columns=16, cell=25)
        self.Control.Canvas.grid(row=1, column=0, rowspan=7)

        self.Control.CanvasNext = Tetris(self.Control, width=200, height=200,
                                         borderwidth=3, relief="solid",
                                         bg="white",
                                         rows=8, columns=8, cell=25)
        self.Control.CanvasNext.grid(row=1, column=1, columnspan=2,
                                     sticky=N+E+S+W)

        self.Control.ChangeMusic = Button(self.Control, text=_("Change Music"),
                                          command=changeMusic, borderwidth=3,
                                          relief="solid",
                                          font=("Liberation Sans", 14),
                                          bg="white")
        self.Control.ChangeMusic.grid(row=2, column=1, columnspan=2,
                                      sticky=N+E+S+W)

        self.Control.Lines = Label(self.Control,
                                   textvariable=self.Control.LinesString,
                                   borderwidth=3, relief="solid",
                                   font=("Liberation Sans", 14), bg="white")
        self.Control.Lines.grid(row=3, column=1, columnspan=2, sticky=N+E+S+W)

        self.Control.Score = Label(self.Control,
                                   textvariable=self.Control.ScoreString,
                                   borderwidth=3, relief="solid",
                                   font=("Liberation Sans", 14), bg="white")
        self.Control.Score.grid(row=4, column=1, columnspan=2, sticky=N+E+S+W)

        self.Control.Best = Label(self.Control,
                                  textvariable=self.Control.BestString,
                                  borderwidth=3, relief="solid",
                                  font=("Liberation Sans", 14), bg="white")
        self.Control.Best.grid(row=5, column=1, columnspan=2, sticky=N+E+S+W)

        self.Control.Pause = Button(self.Control, text=_("Pause"),
                                    command=self.pause, borderwidth=3,
                                    relief="solid",
                                    font=("Liberation Sans", 14), bg="white")
        self.Control.Pause.grid(row=6, column=1, sticky=N+E+S+W)

        self.Control.Quit = Button(self.Control, text=_("Quit"),
                                   command=self.terminate, borderwidth=3,
                                   relief="solid",
                                   font=("Liberation Sans", 14), bg="white")
        self.Control.Quit.grid(row=6, column=2, sticky=N+E+S+W)

        im = PhotoImage(file='umaru.png')
        self.Control.Image = Label(self.Control, image=im, borderwidth=3,
                                   relief="solid", width=150, height=200,
                                   bg="white")
        self.Control.Image.image = im
        self.Control.Image.grid(row=7, column=1, columnspan=2, sticky=N+E+S+W)

        self.Control.Canvas.Draw()
        self.Control.CanvasNext.Draw()
        self.NextFigure = None
        self.LastTime = datetime.datetime.now()
        self.CreateFigure()
        self._job = None
        self.bind_all("<Left>", self.MoveLeft)
        self.bind_all("<Right>", self.MoveRight)
        self.bind_all("<Up>", self.Rotate)
        self.bind_all("<Down>", self.Gravity)
        self.Tick()

    def Tick(self):
        '''Game timer'''
        now = datetime.datetime.now()
        flag = self.Gravity()
        if flag == 0:
            return
        self.Control.Canvas.ReDraw()
        self.Control.Lines.config(text=self.LastTime-now)
        self.LastTime = now
        self._job = self.after(250, self.Tick)

    def create(self):
        '''Create start screen function'''
        self.FirstScreen()

    def resume(self):
        '''Resume game function'''
        self.Control.Pause.config(command=self.pause, text=_("Pause"))
        self._job = self.after(250, self.Tick)

    def pause(self):
        '''Pause game function'''
        if self._job is not None:
            self.after_cancel(self._job)
            self._job = None

        self.Control.Pause.config(command=self.resume, text=_("Resume"))

    def GameOver(self):
        '''Stop the game'''
        if self._job is not None:
            self.after_cancel(self._job)
            self._job = None
        self.unbind_all("<Down>")

        self.Control.Pause.config(command=self.SecondScreen, text=_("Start"))

    def terminate(self):
        '''Quit to start screen'''
        if self._job is not None:
            self.after_cancel(self._job)
            self._job = None
        self.FirstScreen()


mixer.init()


def changeMusic():
    '''Функция смены фоновой музыки'''
    mixer.music.load('./music/'+choice(musics))
    mixer.music.play(-1)


class Figure():
    '''Tetris figure class'''
    SHAPES = (
        ("yellow", (0, 0), (0, 1), (1, 0), (1, 1)),     # O
        ("lightblue", (0, 0), (0, 1), (0, 2), (0, 3)),  # I
        ("red", (0, 1), (1, 1), (1, 0), (2, 0)),        # Z
        ("green", (0, 0), (1, 0), (1, 1), (2, 1)),      # S
        ("orange", (0, 2), (0, 1), (0, 0), (1, 0)),     # L
        ("blue", (0, 0), (1, 0), (1, 1), (1, 2)),       # J
        ("purple", (0, 0), (1, 0), (2, 0), (1, 1)),     # T
    )

    def __init__(self, x=7, y=0):
        '''Init figure'''
        figure = choice(self.SHAPES)
        self.Color = figure[0]
        self.Cells = [(x + cell[0], y + cell[1]) for cell in figure[1:]]
        coords = self.Cells
        times = randint(0, 2)
        for _ in range(times):
            coords = self.Rotate()
        self.Cells = coords

    def Shifted(self):
        '''Shift the figure at second screen'''
        shifted = Figure()
        shifted.Color = self.Color
        shifted.Cells = [(cell[0]-4, cell[1]+3) for cell in self.Cells]
        return shifted

    def MoveDown(self):
        '''Move the figure down'''
        new_cells = [(cell[0], cell[1]+1) for cell in self.Cells]
        return new_cells

    def MoveLeft(self):
        '''Move the figure left'''
        new_cells = [(cell[0]-1, cell[1]) for cell in self.Cells]
        return new_cells

    def MoveRight(self):
        '''Move the figure right'''
        new_cells = [(cell[0]+1, cell[1]) for cell in self.Cells]
        return new_cells

    def Rotate(self):
        '''Rotate the figure'''
        shift_x = 100000
        shift_y = 100000
        old_cells_shifted = []
        for cell in self.Cells:
            if cell[0] < shift_x:
                shift_x = cell[0]
            if cell[1] < shift_y:
                shift_y = cell[1]
        for cell in self.Cells:
            old_cells_shifted.append((cell[0]-shift_x, cell[1]-shift_y))
        new_cells = []
        min_x = 0
        min_y = 0
        for cell in old_cells_shifted:
            tmp_cell = (-cell[1], cell[0])
            if tmp_cell[0] < min_x:
                min_x = tmp_cell[0]
            if tmp_cell[1] < min_y:
                min_y = tmp_cell[1]
            new_cells.append(tmp_cell)
        new_cells_shifted = []
        for cell in new_cells:
            new_cells_shifted.append((cell[0]-min_x+shift_x,
                                      cell[1]-min_y+shift_y))
        return new_cells_shifted


if __name__ == "__main__":
    '''Start main function'''
    mixer.music.load('./music/'+choice(musics))
    mixer.music.play(-1)
    app = Game(Title="Tetris")
    app.mainloop()
