#!/usr/bin/env python3

from tkinter import Canvas, Label, Button, Frame, \
                    N, E, W, S, PhotoImage, StringVar
import os

from random import choice, randint
from collections import Counter
from pygame import mixer

musics = os.listdir("./music")


class App(Frame):
    '''Base framed application class'''
    def __init__(self, master=None, Title="Application"):
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

    def __init__(self, master=None, *ap, foreground="black", rows, columns, cell, **an):
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
        for cell in figure.Cells:
            x, y = cell
            if x > self.columns - 1 or x < 0:
                continue
            if y > self.rows - 1 or y < 0:
                continue

            self.Matrix[x][y] = figure.Color

    def RemoveFigure(self, figure):
        for cell in figure.Cells:
            x, y = cell
            if x > self.columns - 1 or x < 0:
                continue
            if y > self.rows - 1 or y < 0:
                continue

            self.Matrix[x][y] = "gray"

    def Draw(self):
        for existing in self.Rects:
            self.delete(existing)

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


class Game(App):
    def CreateFigure(self):
        if self.NextFigure is not None:
            self.Control.CanvasNext.RemoveFigure(self.NextFigure.Shifted())
            self.CurrentFigure = self.NextFigure
        else:
            self.CurrentFigure = Figure()

        self.Control.Canvas.HoldFigure(self.CurrentFigure)

        # Draw next figure
        self.NextFigure = Figure()
        self.Control.CanvasNext.HoldFigure(self.NextFigure.Shifted())
        self.Control.CanvasNext.Draw()

    def Gravity(self):
        self.Control.Canvas.RemoveFigure(self.CurrentFigure)
        self.CurrentFigure.MoveDown()
        if self.IsLanded():
            self.CurrentFigure.MoveUp()
            self.Control.Canvas.HoldFigure(self.CurrentFigure)
            for cell in self.CurrentFigure.Cells:
                self.busy_cells.append(cell)

            self.CreateFigure()
            return

        self.Control.Canvas.HoldFigure(self.CurrentFigure)

    def MoveLeft(self, event):
        self.Control.Canvas.RemoveFigure(self.CurrentFigure)
        self.CurrentFigure.MoveLeft()
        self.Control.Canvas.HoldFigure(self.CurrentFigure)
        self.Control.Canvas.Draw()

    def MoveRight(self, event):
        self.Control.Canvas.RemoveFigure(self.CurrentFigure)
        self.CurrentFigure.MoveRight()
        self.Control.Canvas.HoldFigure(self.CurrentFigure)
        self.Control.Canvas.Draw()

    def Rotate(self, event):
        self.Control.Canvas.RemoveFigure(self.CurrentFigure)
        self.CurrentFigure.Rotate()
        self.Control.Canvas.HoldFigure(self.CurrentFigure)
        self.Control.Canvas.Draw()
    
    def IsLanded(self):
        intersected = False
        for cell in self.CurrentFigure.Cells:
            if cell in self.busy_cells or cell[1] > self.Control.Canvas.rows - 1:
                intersected = True
                break
            
        return intersected

    def FirstScreen(self):
        # Kostyl
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
                                     rows = 24, columns = 26, cell = 25)
        self.Control.Canvas.grid(row=1, column=0, rowspan=7)

        self.Control.CanvasNext = Canvas(self.Control, width=150,
                                         height=200, borderwidth=3,
                                         relief="solid", bg="white")
        self.Control.CanvasNext.grid(row=1, column=1, columnspan=2,
                                     sticky=N+E+S+W)
        # End of kostyl

        self.Control = Frame(borderwidth=3, relief="solid", bg="white")
        self.Control.grid(row=0, column=0, sticky=N+E+S+W)

        headerIm = PhotoImage(file="tetris.png")
        self.Control.Header = Label(self.Control, image=headerIm,
                                    borderwidth=3, relief="solid",
                                    width=615, bg="white")
        self.Control.Header.image = headerIm
        self.Control.Header.grid(row=0, columnspan=4, sticky=N+E+S+W)

        self.Control.Canvas = Tetris(self.Control, width=615, borderwidth=3,
                                     relief="solid", bg="white",
                                     rows = 24, columns = 26, cell = 25)
        self.Control.Score = Label(self.Control, text="Score", borderwidth=3,
                                   relief="solid",
                                   font=("Liberation Sans", 14), bg="white")
        self.Control.Score.grid(row=2, column=1, columnspan=2, sticky=N+E+S+W)

        self.Control.NewGame = Button(self.Control, text="New Game",
                                      command=self.SecondScreen, borderwidth=3,
                                      relief="solid",
                                      font=("Liberation Sans", 14), bg="white")
        self.Control.NewGame.grid(row=4, column=1, columnspan=2,
                                  sticky=N+E+S+W)

        self.Control.Best = Label(self.Control, text="Best", borderwidth=3,
                                  relief="solid", font=("Liberation Sans", 14),
                                  bg="white")
        self.Control.Best.grid(row=6, column=1, columnspan=2, sticky=N+E+S+W)

        self.Control.Quit = Button(self.Control, text="Quit",
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
        self.Control = Frame(borderwidth=3, relief="solid")
        self.Control.grid(row=0, column=0, sticky=N+E+S+W)

        headerIm = PhotoImage(file="tetris.png")
        self.Control.Header = Label(self.Control, image=headerIm,
                                    borderwidth=3, relief="solid",
                                    width=400, bg="white")
        self.Control.Header.image = headerIm
        self.Control.Header.grid(row=0, columnspan=3, sticky=N+E+S+W)

        self.Control.Canvas = Tetris(self.Control, width=400, height=600,
                                     borderwidth=3, relief="solid", bg="white",
                                     rows = 24, columns = 26, cell = 25)
        self.Control.Canvas.grid(row=1, column=0, rowspan=7)

        self.Control.CanvasNext = Tetris(self.Control, width=200, height=200,
                                         borderwidth=3, relief="solid",
                                         bg="white",
                                         rows = 8, columns = 8, cell = 25)
        self.Control.CanvasNext.grid(row=1, column=1, columnspan=2,
                                     sticky=N+E+S+W)

        self.Control.ChangeMusic = Button(self.Control, text="Change Music",
                                          command=changeMusic, borderwidth=3,
                                          relief="solid",
                                          font=("Liberation Sans", 14),
                                          bg="white")
        self.Control.ChangeMusic.grid(row=2, column=1, columnspan=2,
                                      sticky=N+E+S+W)

        self.Control.Lines = Label(self.Control, text="Lines", borderwidth=3,
                                   relief="solid",
                                   font=("Liberation Sans", 14), bg="white")
        self.Control.Lines.grid(row=3, column=1, columnspan=2, sticky=N+E+S+W)

        self.Control.Score = Label(self.Control, text="Score", borderwidth=3,
                                   relief="solid",
                                   font=("Liberation Sans", 14), bg="white")
        self.Control.Score.grid(row=4, column=1, columnspan=2, sticky=N+E+S+W)

        self.Control.Best = Label(self.Control, text="Best", borderwidth=3,
                                  relief="solid",
                                  font=("Liberation Sans", 14), bg="white")
        self.Control.Best.grid(row=5, column=1, columnspan=2, sticky=N+E+S+W)

        self.Control.Pause = Button(self.Control, text="Pause",
                                    command=self.pause, borderwidth=3,
                                    relief="solid",
                                    font=("Liberation Sans", 14), bg="white")
        self.Control.Pause.grid(row=6, column=1, sticky=N+E+S+W)

        self.Control.Quit = Button(self.Control, text="Quit",
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

        self.NextFigure = None
        self.CreateFigure()
        self._job = None
        self.busy_cells = []
        self.bind_all("<Left>", self.MoveLeft)
        self.bind_all("<Right>", self.MoveRight)
        self.bind_all("<space>", self.Rotate)
        self.Tick()

    def Tick(self):
        self.Gravity()
        self.Control.Canvas.Draw()
        self.Control.Lines.config(text = randint(1,100))
        self._job = self.after(500, self.Tick)

    def create(self):
        self.FirstScreen()

    def resume(self):
        self.Control.Pause.config(command=self.pause, text="Play")
        self._job = self.after(500, self.Tick)

    def pause(self):
        if self._job is not None:
            self.after_cancel(self._job)
            self._job = None

        self.Control.Pause.config(command=self.resume, text="Resume")

    def terminate(self):
        if self._job is not None:
            self.after_cancel(self._job)
            self._job = None
        self.FirstScreen()


mixer.init()
'''Функция смены фоновой музыки'''


def changeMusic():
    mixer.music.load('./music/'+choice(musics))
    mixer.music.play(-1)


class Figure():
    SHAPES = (
        ("yellow", (0, 0), (0, 1), (1, 0), (1, 1)),     # O
        ("lightblue", (0, 0), (0, 1), (0, 2), (0, 3)),  # I
        ("red", (0, 1), (1, 1), (1, 0), (2, 0)),        # Z
        ("green", (0, 0), (1, 0), (1, 1), (2, 1)),      # S
        ("orange", (0, 2), (0, 1), (0, 0), (1, 0)),     # L
        ("blue", (0, 0), (1, 0), (1, 1), (1, 2)),       # J
        ("purple", (0, 0), (1, 0), (2, 0), (1, 1)),     # T
    )

    def __init__(self, x=7, y=0, angle=0):
        figure = choice(self.SHAPES)
        self.Color = figure[0]
        self.Cells = [(x + cell[0], y + cell[1]) for cell in figure[1:]]

        times = int(angle / 90)
        for _ in range(times):
            self.Rotate()

    def Shifted(self):
        shifted = Figure()
        shifted.Color = self.Color
        shifted.Cells = [(cell[0]-4, cell[1]+3) for cell in self.Cells]
        return shifted
        
    def MoveUp(self):
        new_cells = [(cell[0], cell[1]-1) for cell in self.Cells]
        self.Cells = new_cells

    def MoveDown(self):
        new_cells = [(cell[0], cell[1]+1) for cell in self.Cells]
        self.Cells = new_cells

    def MoveLeft(self):
        new_cells = [(cell[0]-1, cell[1]) for cell in self.Cells]
        self.Cells = new_cells

    def MoveRight(self):
        new_cells = [(cell[0]+1, cell[1]) for cell in self.Cells]
        self.Cells = new_cells

    def Rotate(self):
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
            tmp_cell = (cell[1], -cell[0])
            if tmp_cell[0] < min_x:
                min_x = tmp_cell[0]
            if tmp_cell[1] < min_y:
                min_y = tmp_cell[1]
            new_cells.append(tmp_cell)
        new_cells_shifted = []
        for cell in new_cells:
            new_cells_shifted.append((cell[0]-min_x+shift_x,
                                      cell[1]-min_y+shift_y))

        # Implement me
        self.Cells = new_cells_shifted


if __name__ == "__main__":
    mixer.music.load('./music/'+choice(musics))
    mixer.music.play(-1)
    app = Game(Title="Tetris")
    app.mainloop()
