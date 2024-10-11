from board import boardState
from player import DQNPlayer

class SelfPlay:
    def __init__(self, player=DQNPlayer):
        self.p = player
        self.current_player = None
    
    def alternate(self):
        while True:
            yield self.p
    
    def play(self, game=boardState, print_state=False):
        alternator = self.alternate()
        self.current_state = game()
        self.p.reset(self.current_state)

        while True:
            player = next(alternator)
            act = player.search(self.current_state, train=False, print_state=print_state)

            if print_state:
                self.current_state.printState()
                print(len(self.current_state.getPossibleActions()))
                print(act)
            
            self.current_state = self.current_state.takeAction(act)

            if self.current_state.isTerminal():
                if print_state:
                    self.current_state.printState()
                msg, winner = self.current_state.get_winner(getValue=True)
                return winner
