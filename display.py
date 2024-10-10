import tkinter as tk
from action import Action
# from DQN import DQNPlayer
from player import MCTS

class MNKDisplay(tk.Frame):
    def __init__(self, master, game, m, n, k, width=720, height=720):
        super(MNKDisplay, self).__init__(master)
        self.game = game
        self.m = m
        self.n = n
        self.k = k
        self.gameState = self.game(self.m, self.n, self.k)
        self.H = height
        self.W = width
        self.bsize = min(self.H//self.m, self.W//self.n)
        self.canv = tk.Canvas(self, width=self.W, height=self.H, background='#9A7B4F')
        self.canv.pack()
        self.pack()
        self.canv.bind("<Button-1>", self.click)
        self.canv.bind("<Button-2>", self.reset)
        self.canv.bind("<Button-3>", self.action)
        self.winner = self.gameState.winner
        self.drawBoard()
        self.mctsPlayer = MCTS(iterationLimit=300)
        self.ClickTrue = True


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
                    self.create_circle(self.bsize//2+self.bsize*c, self.bsize//2+self.bsize*r, fill='black')
                elif self.gameState.board[r,c] == -1:
                    self.create_circle(self.bsize//2+self.bsize*c, self.bsize//2+self.bsize*r, fill='white')
                elif Action(player=self.gameState.getCurrentPlayer(), x=r, y=c) in self.possibleMove:
                    if self.gameState.getCurrentPlayer() == 1:
                        self.create_circle(self.bsize//2+self.bsize*c, self.bsize//2+self.bsize*r, fill='#444444')
                    elif self.gameState.getCurrentPlayer() == -1:
                        self.create_circle(self.bsize//2+self.bsize*c, self.bsize//2+self.bsize*r, fill='#AAAAAA')

        if self.winner != None:
            msg = self.gameState.get_winner()
            self.canv.create_rectangle(self.bsize//2, self.bsize*(self.gameState.col//2-1),  self.W - self.bsize//2, self.bsize*(self.gameState.col//2+1), fill='white')
            self.canv.create_text(self.gameState.col//2*self.bsize, self.gameState.row//2*self.bsize, text="game is over\n" + msg + "\nDouble Click to reset the game")
    
    def reset(self, event):
        if self.winner != None:
            self.gameState = self.game(self.m, self.n, self.k)
            self.mctsPlayer.reset()
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
        
        if currentAction in self.possibleMove and self.winner == None and self.ClickTrue:
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
        if not self.ClickTrue:
            result = self.mctsPlayer.search(self.gameState, needDetails=True)
            action = result['action']
            reward = result['expectedReward']
            print(action, reward)
            self.gameState = self.gameState.takeAction(action)
            self.winner = self.gameState.winner
            self.ClickTrue = True
        if self.winner != None:
            msg = self.gameState.get_winner()
            print(msg)
        self.canv.delete("all")
        self.drawBoard()
        