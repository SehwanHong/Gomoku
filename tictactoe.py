from copy import deepcopy
from functools import reduce
import operator
from Action import Action

class TicTacToeState():
    def __init__(self):
        self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.row = 3
        self.col = 3
        self.currentPlayer = 1
        self.winner = None

    def getCurrentPlayer(self):
        return self.currentPlayer

    def getPossibleActions(self):
        possibleActions = []
        for i in range(self.row):
            for j in range(self.col):
                if self.isAvailable(i,j):
                    possibleActions.append(Action(player=self.currentPlayer, x=i, y=j))
        return possibleActions
    
    def isAvailable(self, i, j):
        return self.board[i][j] == 0

    def takeAction(self, action):
        newState = deepcopy(self)
        newState.board[action.x][action.y] = action.player
        newState.currentPlayer = self.currentPlayer * -1
        newState.updateWinner()
        return newState

    def isTerminal(self):
        for row in self.board:
            if abs(sum(row)) == 3:
                return True
        for column in list(map(list, zip(*self.board))):
            if abs(sum(column)) == 3:
                return True
        for diagonal in [[self.board[i][i] for i in range(len(self.board))],
                         [self.board[i][len(self.board) - i - 1] for i in range(len(self.board))]]:
            if abs(sum(diagonal)) == 3:
                return True
        return reduce(operator.mul, sum(self.board, []), 1)

    def getReward(self):
        for row in self.board:
            if abs(sum(row)) == 3:
                return sum(row) / 3
        for column in list(map(list, zip(*self.board))):
            if abs(sum(column)) == 3:
                return sum(column) / 3
        for diagonal in [[self.board[i][i] for i in range(len(self.board))],
                         [self.board[i][len(self.board) - i - 1] for i in range(len(self.board))]]:
            if abs(sum(diagonal)) == 3:
                return sum(diagonal) / 3
        return False
    
    def printState(self):
        for i in range(self.row):
            print('-------------')
            out = '| '
            for j in range(self.col):
                if self.board[i][j] == 1:
                    token = 'o'
                elif self.board[i][j] == -1:
                    token = 'x'
                else:
                    token = ' '
                out += token + ' | '
            print(out)
        print('-------------')
    
    def updateWinner(self):
        if self.isTerminal() == True:
            for row in self.board:
                if abs(sum(row)) == self.row:
                    self.winner = sum(row) / self.row
                    return self.winner
            for column in list(map(list, zip(*self.board))):
                if abs(sum(column)) == self.col:
                    self.winner = sum(column) / self.col
                    return self.winner
            for diagonal in [[self.board[i][i] for i in range(len(self.board))],
                            [self.board[i][len(self.board) - i - 1] for i in range(len(self.board))]]:
                if abs(sum(diagonal)) == 3:
                    self.winner = sum(diagonal) / 3
                    return self.winner
            self.winner = 0
            return self.winner
        self.winner = None
        return self.winner
    
    def get_winner(self, getValue=False):
        self.winner = None
        self.updateWinner()
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
    
    def __hash__(self) -> int:
        return hash((tuple(j for i in self.board for j in i), self.currentPlayer))

