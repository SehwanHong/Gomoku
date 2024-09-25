from .mnk import mnkState
from action import Action
from copy import deepcopy
from .constant import BLACK, WHITE

FIRST_PLAYER = 0
SECOND_PLAYER = 1

class Renju(mnkState):
    def __init__(self, m=15, n=15, k=5):
        super().__init__(m=15, n=15, k=5)
        self.move_count = 0

        self.currentPlayer = 0
        self.playerStone = [BLACK, WHITE]
    
    def getPossibleActions(self):
        possibleActions = []
        if self.winner != None:
            return possibleActions
        if self.move_count == 0:
            possibleActions.append(Action(player=self.currentStone, x=7, y=7))
            return possibleActions
        elif self.move_count == 1:
            for i in [6, 7, 8]:
                for j in [6, 7, 8]:
                    if self.isAvailable(i,j):
                        possibleActions.append(Action(player=self.currentStone, x=i, y=j))
            return possibleActions
        elif self.move_count == 2:
            for i in [5, 6, 7, 8, 9]:
                for j in [5, 6, 7, 8, 9]:
                    if self.isAvailable(i,j):
                        possibleActions.append(Action(player=self.currentStone, x=i, y=j))
            return possibleActions
        elif self.move_count == 3 and self.currentPlayer == SECOND_PLAYER:
            possibleActions.append(Action(player=self.currentStone, x=-1, y=-1))
        
        if self.currentStone == WHITE:
            for i in range(self.row):
                for j in range(self.col):
                    if self.isAvailable(i,j):
                        possibleActions.append(Action(player=self.currentStone, x=i, y=j))
        elif self.currentStone == BLACK:
            for i in range(self.row):
                for j in range(self.col):
                    if self.isAvailable(i,j): # and self.isLiveThree(i,j) and self.isLiveFour(i,j) and self.isNotOverline:
                        possibleActions.append(Action(player=self.currentStone, x=i, y=j))
        else:
            raise NotImplementedError
        return possibleActions

    def isAvailable(self, i, j):
        return super().isAvailable(i, j)
    
    def takeAction(self, action):
        newState = deepcopy(self)
        if self.move_count == 3 and action.x == -1 and action.y == -1:
            newState.currentPlayer = FIRST_PLAYER
            newState.playerStone = [WHITE, BLACK]
            newState.currentStone = newState.playerStone[newState.currentPlayer]
        else:
            assert action.x >= 0 and action.y >= 0 and action.x < self.row and action.y < self.col
            newState.board[action.x][action.y] = action.player
            newState.move_count += 1
            newState.currentPlayer = ( self.currentPlayer + 1 ) % 2
            newState.currentStone = newState.playerStone[newState.currentPlayer]
        newState.updateWinner()
        return newState

    
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
