from board import mnkState
from action import Action
from copy import deepcopy
from board import BLACK, WHITE

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
        if self.move_count == 0:
            possibleActions.append(Action(player=self.currentStone, x=7, y=7))
        elif self.move_count == 1:
            for i in [6, 7, 8]:
                for j in [6, 7, 8]:
                    if self.isAvailable(i,j):
                        possibleActions.append(Action(player=self.currentStone, x=i, y=j))
        elif self.move_count == 2:
            for i in [5, 6, 7, 8, 9]:
                for j in [5, 6, 7, 8, 9]:
                    if self.isAvailable(i,j):
                        possibleActions.append(Action(player=self.currentStone, x=i, y=j))
        elif self.move_count == 3:
            if self.currentPlayer == SECOND_PLAYER:
                possibleActions.append(Action(player=self.currentStone, x=-1, y=-1))
        elif self.move_count == 4:
            pass
        else:
            if self.winner != None:
                return possibleActions
            for i in range(self.row):
                for j in range(self.col):
                    if self.isAvailable(i,j):
                        possibleActions.append(Action(player=self.currentStone, x=i, y=j))
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
            assert action.x >= 0 and action.y >= 0 and action.x < self.m and action.y < self.n
            newState.board[action.x][action.y] = action.player
            newState.move_count += 1
            newState.currentPlayer = newState.move_count % 2
            newState.currentStone = newState.playerStone[newState.currentPlayer]
        newState.updateWinner()
        return newState