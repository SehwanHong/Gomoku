from copy import deepcopy
import numpy as np
from board import BLACK, WHITE

class boardState():
    def __init__(self, m=7, n=7, k=5):
        self.board = np.zeros((m,n))
        self.row = m
        self.col = n
        self.k = k
        self.currentStone = BLACK
        self.winner = None

    def getCurrentPlayer(self):
        return self.currentStone

    def getPossibleActions(self):
        pass

    def isAvailable(self, i, j):
        pass

    def takeAction(self, action):
        newState = deepcopy(self)
        newState.board[action.x][action.y] = action.player
        newState.currentStone = self.currentStone * -1
        newState.updateWinner()
        return newState

    def isTerminal(self):
        pass

    def getReward(self):
        pass
    
    def printState(self):
        for i in range(self.row):
            print('-'+'----'*self.row)
            out = '| '
            for j in range(self.col):
                if self.board[i][j] == BLACK:
                    token = 'o'
                elif self.board[i][j] == WHITE:
                    token = 'x'
                else:
                    token = ' '
                out += token + ' | '
            print(out)
        print('-'+'----'*self.row)

    def updateWinner(self):
        pass
    
    def get_winner(self, getValue=False):
        pass
    
    def __hash__(self) -> int:
        return hash((tuple(j for i in self.board for j in i), self.currentStone))

