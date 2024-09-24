from board import mnkState
from Action import Action
from copy import deepcopy

class Renju(mnkState):
    def __init__(self, m=15, n=15, k=5):
        super().__init__(m=15, n=15, k=5)
        self.move_count = 0
    
    def getPossibleActions(self):
        possibleActions = []
        if self.move_count == 0:
            possibleActions.append(Action(player=self.currentPlayer, x=7, y=7))
        elif self.move_count == 1:
            for i in [6, 7, 8]:
                for j in [6, 7, 8]:
                    if self.isAvailable(i,j):
                        possibleActions.append(Action(player=self.currentPlayer, x=i, y=j))
        elif self.move_count == 2:
            for i in [5, 6, 7, 8, 9]:
                for j in [5, 6, 7, 8, 9]:
                    if self.isAvailable(i,j):
                        possibleActions.append(Action(player=self.currentPlayer, x=i, y=j))
        else:
            if self.winner != None:
                return possibleActions
            for i in range(self.row):
                for j in range(self.col):
                    if self.isAvailable(i,j):
                        possibleActions.append(Action(player=self.currentPlayer, x=i, y=j))
        return possibleActions

    def isAvailable(self, i, j):
        return super().isAvailable(i, j)
    
    def takeAction(self, action):
        newState = deepcopy(self)
        newState.board[action.x][action.y] = action.player
        newState.currentPlayer = self.currentPlayer * -1
        newState.move_count += 1
        newState.updateWinner()
        return newState