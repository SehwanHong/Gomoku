from board import boardState
from action import Action

class mnkState(boardState):
    def __init__(self, m=7, n=7, k=5):
        super().__init__(m, n, k)

    def getPossibleActions(self):
        possibleActions = []
        if self.winner != None:
            return possibleActions
        for i in range(self.row):
            for j in range(self.col):
                if self.isAvailable(i,j):
                    possibleActions.append(Action(player=self.currentStone, x=i, y=j))
        return possibleActions
    
    def isAvailable(self, i, j):
        return self.board[i, j] == 0

    def isTerminal(self):
        self.updateWinner()
        return self.winner != None or len(self.getPossibleActions()) == 0

    def getReward(self):
        if self.winner == None:
            return False
        else:
            return self.winner
    
    def updateWinner(self):
        for r in range(self.row-self.k+1):
            for c in range(self.col):
                if (abs(sum(self.board[r:r+self.k,c])) == self.k 
                        and not (r > 0 and abs(sum(self.board[r-1:r+self.k,c])) == self.k + 1)
                        and not (r + self.k < self.row and abs(sum(self.board[r:r+self.k+1,c])) == self.k + 1)):
                    self.winner = sum(self.board[r:r+self.k,c])//self.k
                    return self.winner

        for r in range(self.row):
            for c in range(self.col-self.k+1):
                if (abs(sum(self.board[r,c:c+self.k])) == self.k 
                        and not (c > 0 and abs(sum(self.board[r,c-1:c+self.k])) == self.k + 1)
                        and not (c + self.k < self.col and abs(sum(self.board[r,c:c+self.k+1])) == self.k + 1)):
                    self.winner = sum(self.board[r,c:c+self.k])//self.k
                    return self.winner
        
        for r in range(self.row-self.k+1):
            for c in range(self.col-self.k+1):
                if (abs(sum(self.board[r+i,c+i] for i in range(self.k))) == self.k
                        and not (r > 0 and c > 0 and abs(sum(self.board[r+i-1,c+i-1] for i in range(self.k+1))) == self.k+1)
                        and not (r + self.k < self.row and c + self.k < self.col and abs(sum(self.board[r+i,c+i] for i in range(self.k+1))) == self.k+1)):
                    self.winner = sum(self.board[r+i,c+i] for i in range(self.k))//self.k
                    return self.winner
        
        for r in range(self.row-self.k+1):
            for c in range(self.col-1, self.k - 2, -1):
                if (abs(sum(self.board[r+i,c-i] for i in range(self.k))) == self.k
                        and not (r > 0 and c + 1 < self.col and abs(sum(self.board[r+i-1,c-i+1] for i in range(self.k+1))) == self.k+1)
                        and not (r + self.k < self.row and c + 1 > self.k and abs(sum(self.board[r+i,c-i] for i in range(self.k+1))) == self.k+1)
                        ):
                    self.winner = sum(self.board[r+i,c-i] for i in range(self.k))//self.k
                    return self.winner
        
        if len(self.getPossibleActions()) == 0:
            self.winner = 0
            return self.winner
        self.winner = None
        return self.winner
    
    def get_winner(self, getValue=False):
        if getValue:
            if self.winner == None:
                return "Game is currently playing", self.winner
            elif self.winner > 0:
                return "Player 1 have won the game", self.winner
            elif self.winner < 0:
                return "Player 2 have won the game", self.winner
            else:
                return "Draw", self.winner
        else:
            if self.winner == None:
                return "Game is currently playing"
            elif self.winner > 0:
                return "Player 1 have won the game"
            elif self.winner < 0:
                return "Player 2 have won the game"
            else:
                return "Draw"
