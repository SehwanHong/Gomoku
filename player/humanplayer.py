from .player import Player
from action import Action

# human interface
# input a number to put a chessman
# | q | w | e |
# | a | s | d |
# | z | x | c |

class HumanPlayer(Player):
    def __init__(self, **kwargs):
        self.player = None
        self.keys = ['q', 'w', 'e', 'a', 's', 'd', 'z', 'x', 'c']
        self.state = None
    
    def search(self, state, print_state=False):
        self.state = state
        if print_state:
            self.state.printState()
        row = self.state.row
        col = self.state.col
        x = None
        y = None
        action = None
        while action == None:
            print("write input as 'row col', eg. '10 7', 10th row, 7th coloumn")
            key = input("Input your position:")
            key = key.split()
            if len(key) != 2:
                continue
            x = int(key[0])
            y = int(key[1])
            if not (x >=0 and x < row and y >= 0 and y < col and self.state.isAvailable(x, y)):
                x = None
                y = None
                action = None
            else:
                action = Action(self.state.getCurrentPlayer(), x, y)
                return action
            