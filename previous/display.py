import tkinter as tk
from Action import Action
from DQN import DQNPlayer

class MNKDisplay(tk.Frame):
    def __init__(self, master, game, m, n, k):
        super(MNKDisplay, self).__init__(master)
        self.bsize = 50
        self.game = game
        self.m = m
        self.n = n
        self.k = k
        self.gameState = self.game(self.m, self.n, self.k)
        self.H = self.bsize*self.gameState.row
        self.W = self.bsize*self.gameState.col
        self.canv = tk.Canvas(self, width=self.W, height=self.H, background='#9A7B4F')
        self.canv.pack()
        self.pack()
        self.canv.bind("<Button-1>", self.click)
        self.canv.bind("<Button-2>", self.reset)
        self.canv.bind("<Button-3>", self.action)
        self.winner = self.gameState.winner
        self.drawBoard()
        self.mctsPlayer = DQNPlayer(searchLimit=200)
        self.mctsPlayer.loadDQN("./DQN_currentBest.h5")
        self.ClickTrue = True


    def create_circle(self, x, y,  fill = "", outline = "black", width = 1):
        self.canv.create_oval(x - self.bsize//2, y - self.bsize//2, x + self.bsize//2, y + self.bsize//2, fill = fill, outline = outline, width = width)
    
    def drawBoard(self):
        for r in range(self.gameState.row):
            self.canv.create_line(0, self.bsize//2 + self.bsize * r, self.W, self.bsize//2 + self.bsize * r)
        for c in range(self.gameState.col):
            self.canv.create_line(self.bsize//2+self.bsize*c, 0, self.bsize//2+self.bsize*c, self.H)
        
        for r in range(self.gameState.row):
            for c in range(self.gameState.col):
                if self.gameState.board[r,c] == 1:
                    self.create_circle(self.bsize//2+self.bsize*c, self.bsize//2+self.bsize*r, fill='black')
                elif self.gameState.board[r,c] == -1:
                    self.create_circle(self.bsize//2+self.bsize*c, self.bsize//2+self.bsize*r, fill='white')
        
        if self.winner != None:
            msg = self.gameState.get_winner()
            self.canv.create_rectangle(self.bsize//2, self.bsize*(self.gameState.col//2-1),  self.W - self.bsize//2, self.bsize*(self.gameState.col//2+1), fill='white')
            self.canv.create_text(self.gameState.col//2*self.bsize, self.gameState.row//2*self.bsize, text="game is over\n" + msg + "\nDouble Click to reset the game")
    
    def reset(self, event):
        if self.winner != None:
            self.gameState = self.game(self.m, self.n, self.k)
            self.mctsPlayer.reset()
            self.mctsPlayer.loadDQN("./DQN_currentBest.h5")
            self.winner = self.gameState.winner
            self.ClickTrue = True
            self.canv.delete("all")
            self.drawBoard()

    def click(self, event):
        x = event.x
        y = event.y
        row = y //self.bsize
        col = x //self.bsize
        print(x,y)
        
        if self.gameState.isAvailable(row, col) and self.winner == None and self.ClickTrue:
            self.gameState = self.gameState.takeAction(Action(self.gameState.getCurrentPlayer(), row, col))
            self.winner = self.gameState.winner
            # self.ClickTrue = False
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
        # print("event called")
        # if not self.ClickTrue:
        if self.ClickTrue:
            action = self.mctsPlayer.search(self.gameState, train=False)
            self.gameState = self.gameState.takeAction(action)
            self.winner = self.gameState.winner
            self.ClickTrue = True
        if self.winner != None:
            msg = self.gameState.get_winner()
            print(msg)
        self.canv.delete("all")
        self.drawBoard()
        