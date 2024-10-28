from board import boardState
from player import DQNPlayer
from utils import get_newest_model

def get_model_path(model_dir='./model_save/'):
    start, end = get_newest_model(model_dir=model_dir)
    weightFile = None
    weightFile_old = None
    if start != '000000000000':
        weightFile_old = model_dir + end + '.pth'

    if end != '000000000000':
        weightFile = model_dir + end + '.pth'
    return weightFile, weightFile_old


class SelfPlay:
    def __init__(self, player=DQNPlayer):
        self.p = player
        self.current_player = None
    
    def alternate(self):
        while True:
            yield self.p
    
    def play(
            self, 
            game=boardState,
            train=False,
            print_state=False,
            update_model=False,
            model_dir="./model_save/"
        ):
        alternator = self.alternate()
        self.current_state = game()
        self.p.reset(self.current_state)

        while True:
            player = next(alternator)
        
            if update_model:
                weightFile, weightFile_old = get_model_path(model_dir=model_dir)
                if weightFile is not None:
                    player.loadDQN(weightFile)
        
            act = player.search(self.current_state, train=train, print_state=print_state)
            
            self.current_state = self.current_state.takeAction(act)

            if print_state:
                self.current_state.printState()
                print(act)

            if self.current_state.isTerminal():
                if print_state:
                    self.current_state.printState()
                msg, winner = self.current_state.get_winner(getValue=True)
                print(msg)
                return winner

class EvaluatePlay:
    def __init__(self, player_1:DQNPlayer = None, player_2:DQNPlayer = None):
        self.p1 = player_1
        self.p2 = player_2
        self.count = 0
    
    def alternate(self):
        while True:
            if self.count % 2 == 0:
                yield self.p1, self.p2
            else:
                yield self.p2, self.p1
    
    def play(self, game=boardState, print_state=False):
        self.count = 0
        alternator = self.alternate()
        self.current_state = game()
        self.p1.reset(self.current_state)
        self.p2.reset(self.current_state)

        while True:
            player, opponent = next(alternator)
            act = player.search(self.current_state, train=False, print_state=print_state)

            opponent.playAction(act, preserve=False)

            self.current_state = self.current_state.takeAction(act)

            if print_state:
                self.current_state.printState()
                print(act)

            if self.current_state.isTerminal():
                if print_state:
                    self.current_state.printState()
                msg, winner = self.current_state.get_winner(getValue=True)
                print(msg)
                return winner