from .mnk import mnkState
from action import Action
from copy import deepcopy
from .constant import BLACK, WHITE, EMPTY
import numpy as np

FIRST_PLAYER = 0
SECOND_PLAYER = 1

class Renju(mnkState):
    def __init__(self, m=15, n=15, k=5):
        super().__init__(m=15, n=15, k=5)
        self.move_count = 0
        self.openningSequence = False

        self.currentPlayer = 0
        self.playerStone = [BLACK, WHITE]
    
    def getPossibleActions(self):
        # Get possible Actions for player
        possibleActions = []
        if self.winner != None:
            return possibleActions
        if self.openningSequence:
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
        
        # For renju rule, white have no violation
        # For renju rule, black have double three, double four, overline violation
        if self.currentStone == WHITE:
            for i in range(self.row):
                for j in range(self.col):
                    if self.isAvailable(i,j):
                        possibleActions.append(Action(player=self.currentStone, x=i, y=j))
        elif self.currentStone == BLACK:
            for i in range(self.row):
                for j in range(self.col):
                    if self.isPlausibleMove(i, j, self.currentStone) and self.isAvailable(i,j):
                        possibleActions.append(Action(player=self.currentStone, x=i, y=j))
        else:
            raise NotImplementedError
        return possibleActions

    def isValid(self, i, j):
        # Check if i,j is inside the board
        return i >= 0 and j >= 0 and i < self.row and j < self.col

    def isAvailable(self, i, j):
        # check if i,j is empty and able to place a stone
        return self.board[i, j] == EMPTY
    
    def deepcopy(self):
        return deepcopy(self)

    def takeAction(self, action):
        # For taking action, create a copy
        newState = deepcopy(self)
        if self.move_count == 3 and action.x == -1 and action.y == -1:
            newState.currentPlayer = FIRST_PLAYER
            newState.playerStone = [WHITE, BLACK]
            newState.currentStone = newState.playerStone[newState.currentPlayer]
        else:
            assert action.x >= 0 and action.y >= 0 and action.x < self.row and action.y < self.col
            assert action.player == self.currentStone
            newState.board[action.x][action.y] = action.player
            newState.move_count += 1
            newState.currentPlayer = ( self.currentPlayer + 1 ) % 2
            newState.currentStone = newState.playerStone[newState.currentPlayer]
            # newState._four()
            # newState._three()
            newState.updateWinner()
        return newState

    def countConsecutive(self, i, j, color):
        directions = [[1, 0], [0, 1], [1, 1], [1, -1]]

        counts = []

        for direction in directions:
            count = self.countBothDirection(i, j, direction, color)
            counts.append(count)
        
        return max(counts)
    
    def five(self, i, j):
        if self.isAvailable(i, j):
            return False
        return self.countConsecutive(i, j, self.board[i, j]) == 5
    
    def overline(self, i, j):
        if self.isAvailable(i, j):
            return False
        return self.countConsecutive(i,j, self.board[i, j]) > 5
    
    def isFive(self, i,j):
        return self.countConsecutive(i, j, self.currentStone) == 5

    def isOverline(self, i, j):
        return self.countConsecutive(i, j, self.currentStone) > 5

    def _four(self):
        # 하나를 뒀을 떄 5를 만들 수 있는 자리는 four 이다.
        four_board = np.zeros((self.row, self.col))

        for i in range(self.row):
            for j in range(self.col):
                if self.isAvailable(i, j):
                    four_board[i, j] += self.isFour(i,j, self.currentStone)
        if self.currentStone == BLACK:
            print("four_board")
            print(four_board)
        return four_board
    
    def _fourDefinition(self):
        # 하나를 뒀을 떄 5를 만들 수 있는 자리는 four 이다.
        four_board = np.zeros((self.row, self.col))

        for i in range(self.row):
            for j in range(self.col):
                if self.isAvailable(i, j):
                    four_board[i, j] += self.fourByDefinition(i,j, self.currentStone)
        return four_board
    
    def _openfour(self):
        # 하나를 뒀을 떄 5를 만들 수 있는 자리는 four 이다.
        four_board = np.zeros((self.row, self.col))

        for i in range(self.row):
            for j in range(self.col):
                if self.isAvailable(i, j):
                    four_board[i, j] += self.isOpenFour(i,j, self.currentStone)
        return four_board

    def _three(self):
        # 하나를 뒀을 떄 5를 만들 수 있는 자리는 four 이다.
        three_board = np.zeros((self.row, self.col))

        for i in range(self.row):
            for j in range(self.col):
                if self.isAvailable(i, j):
                    three_board[i, j] += self.isThree(i,j, self.currentStone)
        if self.currentStone == BLACK:
            print("three board")
            print(three_board)
        return three_board
    
    def countBothDirection(self, i, j, direction, color, skip=0):
        count = 1
        for pos_neg in range(-1, 2, 2):
            count += self.countSingleDirection(i, j, direction, color, pos_neg=pos_neg, skip=skip, include_me=False)
        return count

    def countSingleDirection(self, i, j, direction, color, pos_neg=1, skip=0, include_me=True):
        assert pos_neg in [-1, 1]
        if include_me:
            count = 1
        else:
            count = 0
        delta = 1
        check_skip = 0
        while True:
            delta_i = i + direction[0] * delta * pos_neg
            delta_j = j + direction[1] * delta * pos_neg
            if self.isValid(delta_i, delta_j) and self.board[delta_i, delta_j] == color:
                count += 1
            elif self.isValid(delta_i, delta_j) and self.board[delta_i, delta_j] == 0 and check_skip < skip:
                check_skip += 1
            else:
                break
            delta += 1
        return count

    def checkBlocked(self, i, j, direction, color, skip=0):
        return self.checkSingleBlocked(i,j,direction, color, pos_neg=1, skip=skip) and self.checkSingleBlocked(i,j,direction, color, pos_neg=-1, skip=skip)

    def checkSingleBlocked(self, i, j, direction, color, pos_neg=1, skip=0):
        assert pos_neg in [-1, 1]
        delta = 1
        check_skip = 0
        while True:
            delta_i = i + direction[0] * delta * pos_neg
            delta_j = j + direction[1] * delta * pos_neg
            if self.isValid(delta_i, delta_j) and self.board[delta_i, delta_j] == color:
                pass
            elif self.isValid(delta_i, delta_j) and self.board[delta_i, delta_j] == 0:
                if check_skip == skip:
                    return False
                elif check_skip < skip:
                    check_skip += 1
            else:
                return True
            delta += 1

    def isFour(self, i, j, color):
        """This Method is very slow, must use fourByDefinition"""
        cnt = 0
        directions = [[1, 0], [0, 1], [1, 1], [1, -1]]
        if self.isAvailable(i, j):
            for direction in directions:
                myfour = self.myfourDirection(i, j, direction, color)
                four_def, count_list, when_skipped, blocked = self.fourByDefinitionDirection(i, j, direction, color)
                assert myfour == four_def, f"\tmyfour : {myfour}\n\tfour_def : {four_def}\n\tcount_list : {count_list}\n\twhen_skipped: {when_skipped}\n\tblocked : {blocked}\n\tdirection : {direction}\n\tplace of stone : {i}, {j}\n{self.board}"
                cnt += myfour

        return cnt

    def fourByDefinition(self, i, j, color):
        cnt = 0
        directions = [[1, 0], [0, 1], [1, 1], [1, -1]]
        if self.isAvailable(i, j):
            for direction in directions:
                # myfour = self.myfourDirection(i, j, direction, color)
                four_def, count_list, when_skipped, blocked = self.fourByDefinitionDirection(i, j, direction, color)
                # assert myfour == four_def, f"myfour({myfour}), four_def({four_def}), {count_list}, {when_skipped}, {i}, {j}"
                cnt += four_def
        return cnt
    
    def myfourDirection(self, i, j, direction, color):
        cnt = 0
        # check for general cases
        count = self.countBothDirection(i, j, direction, color, skip=1)
        # cnt_list is for considering for each direction
        # because self countBoth Direction miss _00_?0_00_ where ? is a place of stone
        cnt_list = []
        for pos_neg_dir in range(-1, 2, 2):
            temp = self.countSingleDirection(i, j, direction, color, pos_neg=pos_neg_dir, skip=0, include_me=True) + self.countSingleDirection(i, j, direction, color, pos_neg=pos_neg_dir * -1, skip=1, include_me=False)
            cnt_list.append(temp)
        if count == 4:
            # checkBlocked is to check if both side is closed
            # thus not checkBlocked means at least one side is open
            if not self.checkBlocked(i, j, direction, color):
                # checking cnt_list[0] and cnt_list[1] to check for correct four
                # if _0_?0_0_ where ? is not 'four' because it cannot make '5' by putting one stone
                if cnt_list[0] == count or cnt_list[1] == count:
                    cnt += 1
        elif count > 4:
            # when the stone is place in one line must consider single skip for each direction
            for count in cnt_list:
                if count == 4:
                    cnt += 1
        return cnt
    
    @staticmethod
    def util_countDirection(board, i, j, direction, color):
        skip_count = []
        no_skip_count = []
        blocked = []
        row, col = board.shape
        isValid = lambda i,j :i >= 0 and j >= 0 and i < row and j < col 
        
        for pos_neg in range(-1, 2, 2):
            delta = 1
            count = 0
            count_empty = 0
            prev_stone = -100
            while True:
                delta_i = i + direction[0] * delta * pos_neg
                delta_j = j + direction[1] * delta * pos_neg
                if isValid(delta_i, delta_j) and board[delta_i, delta_j] == color:
                    count += 1
                    prev_stone = color
                elif isValid(delta_i, delta_j) and board[delta_i, delta_j] == 0 and count_empty == 0:
                    # count += 1
                    count_empty += 1
                    prev_stone = 0
                    no_skip_count.append(delta - 1)
                else:
                    if isValid(delta_i, delta_j) and board[delta_i, delta_j] == -color:
                        if count_empty == 1:
                            blocked.append(False)
                        else:
                            blocked.append(True)
                    elif not isValid(delta_i, delta_j):
                        if count_empty == 1:
                            blocked.append(False)
                        else:
                            blocked.append(True)
                    elif isValid(delta_i, delta_j) and board[delta_i, delta_j] == 0:
                        blocked.append(False)
                    else:
                        blocked.append(True)
                    if count_empty == 0:
                        no_skip_count.append(delta - 1)
                    skip_count.append(count)
                    break
                delta += 1
        
        return skip_count, no_skip_count, blocked

    @staticmethod
    def util_evalFour(skip_count, no_skip_count, blocked):
        cnt = 0
        newCount = skip_count[0] + skip_count[1] + 1
        if newCount == 4:
            if not blocked[0] or not blocked[1]:
                if no_skip_count[0] + skip_count[1] == 3 or skip_count[0] + no_skip_count[1] == 3:
                    cnt += 1
        elif newCount > 4:
            if no_skip_count[0] + skip_count[1] == 3:
                cnt += 1
            if skip_count[0] + no_skip_count[1] == 3:
                cnt += 1
        return cnt, skip_count, no_skip_count, blocked
    
    @staticmethod
    def util_evalOpenFour(skip_count, no_skip_count, blocked):
        cnt = 0
        newCount = no_skip_count[0] + no_skip_count[1] + 1
        if newCount == 4:
            if not blocked[0] and not blocked[1]:
                if no_skip_count[0] + skip_count[1] == 3 or skip_count[0] + no_skip_count[1] == 3:
                    cnt += 1
        return cnt, skip_count, no_skip_count, blocked

    def fourByDefinitionDirection(self, i, j, direction, color):
        skip_count, no_skip_count, blocked = self.util_countDirection(self.board, i, j, direction, color)
        return self.util_evalFour(skip_count=skip_count, no_skip_count=no_skip_count, blocked=blocked)

    def isOpenFour(self, i, j, color):
        directions = [[1, 0], [0, 1], [1, 1], [1, -1]]
        if self.isAvailable(i,j):
            for direction in directions:
                if self.checkOpenFourDirection(i, j, direction, color):
                    return True
        return False

    def checkOpenFourDirection(self, i, j, direction, color):
        if self.countConsecutive(i,j, color) == 5:
            return False
        skip_count, no_skip_count, blocked = self.util_countDirection(self.board, i, j, direction, color)
        newCount = skip_count[0] + skip_count[1] + 1
        if not blocked[0] and not blocked[1]:
            if newCount == 4 and sum(skip_count) == sum(no_skip_count):
                if no_skip_count[0] + skip_count[1] == 3 or skip_count[0] + no_skip_count[1] == 3:
                    return True
        return False

    
    def isThree(self, i, j, color):
        directions = [[1, 0], [0, 1], [1, 1], [1, -1]]
        cnt = 0
        if self.isAvailable(i,j):
            for direction in directions:
                if self.openThreeDirection(i, j, direction, color):
                    cnt += 1
        return cnt

    def openThreeDirection(self, i, j, direction, color):
        self.board[i,j] = color
        for pos_neg in range(-1, 2, 2):
            delta = 1
            while True:
                delta_i = i + direction[0] * delta * pos_neg
                delta_j = j + direction[1] * delta * pos_neg
                if self.isValid(delta_i, delta_j) and self.board[delta_i, delta_j] == color:
                    pass
                elif self.isValid(delta_i, delta_j) and self.board[delta_i, delta_j] == 0:
                    if self.checkOpenFourDirection(delta_i, delta_j, direction, self.currentStone):
                        if self.isPlausibleMove(delta_i, delta_j, self.currentStone):
                            self.board[i,j] = EMPTY
                            return True
                    break
                else:
                    break
                delta += 1
        self.board[i,j] = EMPTY
        return False


    def isPlausibleMove(self, i, j, color):
        if self.isFive(i, j):
            return True
        elif self.isOverline(i, j):
            if color == WHITE:
                return True
            else:
                return False
        elif self.isFour(i, j, color) > 1 or self.isThree(i, j, color) > 1:
            if color == WHITE:
                return True
            else:
                return False
        else:
            return True


    def isTerminal(self):
        self.updateWinner()
        return self.winner != None or len(self.getPossibleActions()) == 0

    def getReward(self):
        if self.winner == None:
            return False
        else:
            return self.winner
    
    def updateWinner(self):
        if len(self.getPossibleActions()) == 0:
            self.winner = 0
            return self.winner

        for i in range(self.row):
            for j in range(self.col):
                if self.board[i][j] == BLACK and self.five(i,j):
                    self.winner = BLACK
                    return self.winner
                elif self.board[i][j] == WHITE and (self.five(i,j) or self.overline(i,j)):
                    self.winner = WHITE
                    return self.winner
                elif self.board[i][j] not in[BLACK, WHITE, EMPTY]:
                    raise ValueError("self.board cannot have value that is BLACK, WHITE, EMPTY")
                else:
                    pass
        
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
