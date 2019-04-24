#!/usr/bin/env python3

from tkinter import *
from tkinter import Canvas, Label, Tk, StringVar, messagebox
from tkinter import colorchooser, filedialog
import time

from random import choice
from collections import Counter
from pygame import mixer
from threading import Thread

musics = ["Chop Suey.wav", "Game Of Thrones Theme.wav", "Hypnotize.wav", "In The End.wav", "Numb.wav", "Stairway to Heaven.wav", "Star Wars.wav", "We Are The Champions.wav"]

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
    '''Canvas with simple drawing'''
    def mousedown(self, event):
        '''Store mousedown coords'''
        self.x0, self.y0 = event.x, event.y
        self.cursor = None

    def mousemove(self, event):
        '''Do sometheing when drag a mouse'''
        if self.cursor:
            self.delete(self.cursor)
        self.cursor = self.create_line((self.x0, self.y0, event.x, event.y), fill=self.foreground.get())

    def mouseup(self, event):
        '''Dragging is done'''
        self.cursor = None

    def __init__(self, master=None, *ap, foreground="black", **an):
        self.foreground = StringVar()
        self.foreground.set(foreground)
        Canvas.__init__(self, master, *ap, **an)
        self.bind("<Button-1>", self.mousedown)
        self.bind("<B1-Motion>", self.mousemove)
        self.bind("<ButtonRelease-1>", self.mouseup)

        self.rows = 24
        self.columns = 16
        self.cellwidth = 25
        self.cellheight = 25
        
        self.Matrix = []
        for _ in range(self.columns):
            column_arr = []
            for _ in range(self.rows):
                column_arr.append("gray")
            self.Matrix.append(column_arr)
        
        self.Rectangles = {}
    
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
        for existing in self.Rectangles:
            self.delete(existing)

        self.Rectangles = {}
        for column in range(self.columns):
            for row in range(self.rows):
                x1 = column*self.cellwidth
                y1 = row * self.cellheight
                x2 = x1 + self.cellwidth
                y2 = y1 + self.cellheight
                self.Rectangles[row,column] = self.create_rectangle(x1,y1,x2,y2, fill=self.Matrix[column][row], tags="rect")

class Game(App):
    def CreateFigure(self):
        self.CurrentFigure = Figure()
        self.Control.Canvas.HoldFigure(self.CurrentFigure)

    def Gravity(self):
        self.Control.Canvas.RemoveFigure(self.CurrentFigure)
        self.CurrentFigure.MoveDown()
        self.Control.Canvas.HoldFigure(self.CurrentFigure)

    def FirstScreen(self):
        # Kostyl
        self.Control = Frame(borderwidth=3, relief="solid")
        self.Control.grid(row=0, column=0, sticky=N+E+S+W)

        headerIm = PhotoImage(file="tetris.png")
        self.Control.Header = Label(self.Control, image=headerIm, borderwidth=3, relief="solid", width=400, bg="white")
        self.Control.Header.image = headerIm
        self.Control.Header.grid(row=0, columnspan=3, sticky=N+E+S+W)

        self.Control.Canvas = Tetris(self.Control, width=400, height=600, borderwidth=3, relief="solid", bg="white")
        self.Control.Canvas.grid(row=1, column=0, rowspan=7)

        self.Control.CanvasNext = Canvas(self.Control, width=150, height=200, borderwidth=3, relief="solid", bg="white")
        self.Control.CanvasNext.grid(row=1, column=1, columnspan=2, sticky=N+E+S+W)
        # End of kostyl

        self.Control = Frame(borderwidth=3, relief="solid")
        self.Control.grid(row=0, column=0, sticky=N+E+S+W)

        headerIm = PhotoImage(file="tetris.png")
        self.Control.Header = Label(self.Control, image=headerIm, borderwidth=3, relief="solid", width=565, bg="white")
        self.Control.Header.image = headerIm
        self.Control.Header.grid(row=0, columnspan=4, sticky=N+E+S+W)

        self.Control.Canvas = Tetris(self.Control, width=565, borderwidth=3, relief="solid", bg="white")

        self.Control.NewGame = Button(self.Control, text="Score", command=self.quit, borderwidth=3, relief="solid", font=("Liberation Sans", 14), bg="white")
        self.Control.NewGame.grid(row=2, column=1, columnspan=2, sticky=N+E+S+W)

        self.Control.NewGame = Button(self.Control, text="New Game", command=self.SecondScreen, borderwidth=3, relief="solid", font=("Liberation Sans", 14), bg="white")
        self.Control.NewGame.grid(row=4, column=1, columnspan=2, sticky=N+E+S+W)

        self.Control.NewGame = Button(self.Control, text="Best", command=self.quit, borderwidth=3, relief="solid", font=("Liberation Sans", 14), bg="white")
        self.Control.NewGame.grid(row=6, column=1, columnspan=2, sticky=N+E+S+W)

        self.Control.NewGame = Button(self.Control, text="Quit", command=self.quit, borderwidth=3, relief="solid", font=("Liberation Sans", 14), bg="white")
        self.Control.NewGame.grid(row=8, column=1, columnspan=2, sticky=N+E+S+W)

        self.Control.grid_rowconfigure(1, minsize=100)
        self.Control.grid_rowconfigure(3, minsize=50)
        self.Control.grid_rowconfigure(5, minsize=50)
        self.Control.grid_rowconfigure(7, minsize=50)
        self.Control.grid_columnconfigure(0, minsize=35)

    def SecondScreen(self):
        self.Control = Frame(borderwidth=3, relief="solid")
        self.Control.grid(row=0, column=0, sticky=N+E+S+W)

        headerIm = PhotoImage(file="tetris.png")
        self.Control.Header = Label(self.Control, image=headerIm, borderwidth=3, relief="solid", width=400, bg="white")
        self.Control.Header.image = headerIm
        self.Control.Header.grid(row=0, columnspan=3, sticky=N+E+S+W)

        self.Control.Canvas = Tetris(self.Control, width=400, height=600, borderwidth=3, relief="solid", bg="white")
        self.Control.Canvas.grid(row=1, column=0, rowspan=7)

        self.Control.CanvasNext = Canvas(self.Control, width=150, height=200, borderwidth=3, relief="solid", bg="white")
        self.Control.CanvasNext.grid(row=1, column=1, columnspan=2, sticky=N+E+S+W)

        self.Control.ChangeMusic = Button(self.Control, text="Change Music", command=changeMusic, borderwidth=3, relief="solid", font=("Liberation Sans", 14), bg="white")
        self.Control.ChangeMusic.grid(row=2, column=1, columnspan=2, sticky=N+E+S+W)

        self.Control.Lines = Label(self.Control, text="Lines", borderwidth=3, relief="solid", font=("Liberation Sans", 14), bg="white")
        self.Control.Lines.grid(row=3, column=1, columnspan=2, sticky=N+E+S+W)

        self.Control.Score = Label(self.Control, text="Score", borderwidth=3, relief="solid", font=("Liberation Sans", 14), bg="white")
        self.Control.Score.grid(row=4, column=1, columnspan=2, sticky=N+E+S+W)

        self.Control.Best = Label(self.Control, text="Best", borderwidth=3, relief="solid", font=("Liberation Sans", 14), bg="white")
        self.Control.Best.grid(row=5, column=1, columnspan=2, sticky=N+E+S+W)

        self.Control.Pause = Button(self.Control, text="Pause", command=self.pause, borderwidth=3, relief="solid", font=("Liberation Sans", 14), bg="white")
        self.Control.Pause.grid(row=6, column=1,sticky=N+E+S+W)

        self.Control.Quit = Button(self.Control, text="Quit", command=self.terminate, borderwidth=3, relief="solid", font=("Liberation Sans", 14), bg="white")
        self.Control.Quit.grid(row=6, column=2, sticky=N+E+S+W)

        im = PhotoImage(file='umaru.png')
        self.Control.Image = Label(self.Control, image=im, borderwidth=3, relief="solid", width=150, height=200, bg="white")
        self.Control.Image.image=im
        self.Control.Image.grid(row=7, column=1, columnspan=2, sticky=N+E+S+W)

        self.CreateFigure()
        self._job = None
        self.Tick()
    
    def Tick(self):
        self.Gravity()
        self.Control.Canvas.Draw()
        self._job = self.after(1000, self.Tick)

    def create(self):
        self.FirstScreen()

    def resume(self):
        self.Control.Pause.config(command = self.pause, text = "Play")
        self._job = self.after(1000, self.Tick)

    def pause(self):
        if self._job is not None:
            self.after_cancel(self._job)
            self._job = None

        self.Control.Pause.config(command = self.resume, text = "Resume")
    
    def terminate(self):
        if self._job is not None:
            self.after_cancel(self._job)
            self._job = None
        
        self.FirstScreen()


mixer.init()
def changeMusic():
    mixer.music.load(choice(musics))
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

    def __init__(self, x = 8, y = 12, angle = 0):
        figure = choice(self.SHAPES)
        self.Color = figure[0]
        self.Cells = [(x + cell[0], y + cell[1]) for cell in figure[1:]]

        times = int(angle / 90)
        for _ in range(times):
            self.RotateRight()

    def MoveDown(self):
        new_cells = [(cell[0], cell[1]+1) for cell in self.Cells]
        self.Cells = new_cells
    
    def RotateRight(self):
        new_cells = []
        # Implement me
        self.Cells = new_cells

if __name__ == "__main__":
    mixer.music.load(choice(musics))
    mixer.music.play(-1)
    app = Game(Title="Tetris")
    app.mainloop()
