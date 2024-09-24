from tictactoe import TicTacToeState

class Judger:
    def __init__(self, player1, player2, set_player=True):
        self.p1 = player1
        self.p2 = player2
        self.current_player = None
        self.p1_player = 1
        self.p2_player = -1
        if set_player:
            self.p1.set_player(self.p1_player)
            self.p2.set_player(self.p2_player)
    
    def reset(self):
        self.p1.reset()
        self.p2.reset()
    
    def alternate(self):
        while True:
            yield self.p1
            yield self.p2
    
    def play(self, game=TicTacToeState, print_state=False):
        alternator = self.alternate()
        self.reset()
        self.current_state = game()
        self.p1.set_state(self.current_state)
        self.p2.set_state(self.current_state)
        
        while True:
            if print_state:
                self.current_state.printState()
            player = next(alternator)
            act = player.search(self.current_state)
            self.current_state = self.current_state.takeAction(act)
            self.p1.set_state(self.current_state)
            self.p2.set_state(self.current_state)
            if self.current_state.isTerminal():
                if print_state:
                    self.current_state.printState()
                msg, winner = self.current_state.get_winner(getValue=True)
                return winner


class SelfPlay:
    def __init__(self, player):
        self.p = player
        self.current_player = None
    
    def reset(self):
        self.p.reset()
    
    def alternate(self):
        while True:
            yield self.p
    
    def play(self, game=TicTacToeState, print_state=False):
        alternator = self.alternate()
        self.reset()
        self.current_state = game()
        self.p.set_state(self.current_state)
        
        while True:
            if print_state:
                self.current_state.printState()
            player = next(alternator)
            act = player.search(self.current_state)
            print(act)
            self.current_state = self.current_state.takeAction(act)
            self.p.set_state(self.current_state)
            if self.current_state.isTerminal():
                if print_state:
                    self.current_state.printState()
                msg, winner = self.current_state.get_winner(getValue=True)
                return winner
