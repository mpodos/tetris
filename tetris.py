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

class Game(App):

    def create(self):
        self.Control = Frame(borderwidth=3, relief="solid")
        self.Control.grid(row=0, column=0, sticky=N+E+S+W)

        headerIm = PhotoImage(file="tetris.png")
        self.Control.Header = Label(self.Control, image=headerIm, borderwidth=3, relief="solid", width=400, bg="white")
        self.Control.Header.image = headerIm
        self.Control.Header.grid(row=0, columnspan=3, sticky=N+E+S+W)

        self.Control.Canvas = Canvas(self.Control, width=400, height=600, borderwidth=3, relief="solid", bg="white")
        self.Control.Canvas.grid(row=1, column=0, rowspan=7)
        # grid properties
        self.rows = 24
        self.columns = 16
        self.cellwidth = 25
        self.cellheight = 25
        # pick colors for grid
        colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
        self.Colors = []
        for column in range(self.columns):
            column_arr = []
            for row in range(self.rows):
                column_arr.append(choice(colors))
            self.Colors.append(column_arr)
        # draw coloreful grid
        self.rect = {}
        for column in range(self.columns):
            for row in range(self.rows):
                x1 = column*self.cellwidth
                y1 = row * self.cellheight
                x2 = x1 + self.cellwidth
                y2 = y1 + self.cellheight
                self.rect[row,column] = self.Control.Canvas.create_rectangle(x1,y1,x2,y2, fill=self.Colors[column][row], tags="rect")

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

        self.Control.Pause = Button(self.Control, text="Pause", command=self.quit, borderwidth=3, relief="solid", font=("Liberation Sans", 14), bg="white")
        self.Control.Pause.grid(row=6, column=1,sticky=N+E+S+W)

        self.Control.Quit = Button(self.Control, text="Quit", command=self.quit, borderwidth=3, relief="solid", font=("Liberation Sans", 14), bg="white")
        self.Control.Quit.grid(row=6, column=2, sticky=N+E+S+W)

        im = PhotoImage(file='umaru.png')
        self.Control.Image = Label(self.Control, image=im, borderwidth=3, relief="solid", width=150, height=200, bg="white")
        self.Control.Image.image=im
        self.Control.Image.grid(row=7, column=1, columnspan=2, sticky=N+E+S+W)

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

if __name__ == "__main__":
    mixer.music.load(choice(musics))
    mixer.music.play(-1)
    app = Game(Title="Tetris")
    app.mainloop()
