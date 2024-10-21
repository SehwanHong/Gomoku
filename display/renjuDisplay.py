import tkinter as tk
from action import Action
from player import DQNPlayer
from player import MCTS
from .display import MNKDisplay
from board import Renju

class RenjuDisplay(tk.Frame):
    def __init__(self, master, width=720, height=720):
        super(RenjuDisplay, self).__init__(master)
        self.game = Renju
        self.gameState = self.game()
        self.H = height
        self.W = width
        self.bsize = min(self.H//self.gameState.row, self.W//self.gameState.col)
        self.canv = tk.Canvas(self, width=self.W, height=self.H, background='#9A7B4F')
        self.canv.pack()
        self.pack()
        self.canv.focus_set()
        self.canv.bind("<Button-1>", self.click)
        self.canv.bind("<r>", self.reset)
        self.canv.bind("<n>", self.action)
        self.winner = self.gameState.winner
        self.drawBoard()
        self.player = DQNPlayer(searchLimit=900, weightfile="./241021012616.pth")
        self.player.reset(gameState=self.gameState)

        self.ClickTrue = True

        print(True)
    
    
    def create_circle(self, x, y,  fill = "", outline = "black", width = 1):
        self.canv.create_oval(x - self.bsize//2, y - self.bsize//2, x + self.bsize//2, y + self.bsize//2, fill = fill, outline = outline, width = width)
    
    def drawBoard(self):
        self.possibleMove = self.gameState.getPossibleActions()
        for r in range(self.gameState.row):
            self.canv.create_line(0, self.bsize//2 + self.bsize * r, self.W, self.bsize//2 + self.bsize * r)
        for c in range(self.gameState.col):
            self.canv.create_line(self.bsize//2+self.bsize*c, 0, self.bsize//2+self.bsize*c, self.H)
        
        for r in range(self.gameState.row):
            for c in range(self.gameState.col):
                if self.gameState.board[r,c] == 1:
                    self.create_circle(
                        self.bsize//2+self.bsize*c,
                        self.bsize//2+self.bsize*r,
                        fill='black',
                    )
                elif self.gameState.board[r,c] == -1:
                    self.create_circle(
                        self.bsize//2+self.bsize*c,
                        self.bsize//2+self.bsize*r,
                        fill='white',
                    )
                elif Action(player=self.gameState.getCurrentPlayer(), x=r, y=c) in self.possibleMove:
                    if self.gameState.getCurrentPlayer() == 1:
                        self.create_circle(
                            self.bsize//2+self.bsize*c,
                            self.bsize//2+self.bsize*r,
                            fill='#444444',
                        )
                    elif self.gameState.getCurrentPlayer() == -1:
                        self.create_circle(
                            self.bsize//2+self.bsize*c,
                            self.bsize//2+self.bsize*r,
                            fill='#AAAAAA',
                        )

        if self.winner != None:
            msg = self.gameState.get_winner()
            self.canv.create_rectangle(
                self.bsize//2,
                self.bsize*(self.gameState.col//2-1),
                self.W - self.bsize//2,
                self.bsize*(self.gameState.col//2+1),
                fill='white',
            )
            self.canv.create_text(
                self.gameState.col//2*self.bsize,
                self.gameState.row//2*self.bsize,
                text="game is over\n" + msg + "\nDouble Click to reset the game",
            )

    def reset(self, event):
        print("event activated")
        if self.winner != None:
            self.gameState = self.game()
            self.player.reset(gameState=self.gameState)
            self.winner = self.gameState.winner
            self.ClickTrue = True
            self.canv.delete("all")
            self.drawBoard()

    def click(self, event):
        x = event.x
        y = event.y
        row = y //self.bsize
        col = x //self.bsize

        currentAction = Action(player=self.gameState.getCurrentPlayer(), x=row, y=col)
        print(currentAction)
        
        if currentAction in self.possibleMove and self.winner == None and self.ClickTrue:
            self.gameState = self.gameState.takeAction(currentAction)
            self.player.playAction(currentAction,preserve=False)
            self.winner = self.gameState.winner
            self.ClickTrue = False
            self.canv.delete("all")
            self.drawBoard()
            self.canv.update()
            # if self.winner == None:
            #     self.canv.event_generate("<<AIthink>>")
        
        elif self.winner != None:
            msg = self.gameState.get_winner()
            print(msg)
        
        self.canv.delete("all")
        self.drawBoard()
    
    def action(self, event):
        print("event activated")
        if not self.ClickTrue:
            action = self.player.search(self.gameState, print_state=True)
            print(action)
            self.gameState = self.gameState.takeAction(action)
            self.winner = self.gameState.winner
            self.ClickTrue = True
        if self.winner != None:
            msg = self.gameState.get_winner()
            print(msg)
        self.canv.delete("all")
        self.drawBoard()