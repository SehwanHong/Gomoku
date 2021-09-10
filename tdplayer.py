import random
import pickle
from tictactoe import *
from player import Player

BOARD_ROW = 3
BOARD_COL = 3

class TDplayer(Player):
    def __init__(self, step_size = 0.1, epsilon = 0.1):
        self.estimations = dict()
        self.step_size = step_size
        self.epsilon = epsilon
        self.states = []
        self.greedy = []
        self.player = 0
    
    def reset(self):
        self.states = []
        self.greedy = []
    
    def set_state(self, state):
        self.states.append(state)
        self.greedy.append(True)
    
    def set_player(self, player):
        self.player = player
        self.make_table()
    
    def make_table(self):
        initialState = TicTacToeState();
        def get_all_states_impl(current_state, all_states):
            for i in range(BOARD_ROW):
                for j in range(BOARD_COL):
                    if current_state.isAvailable(i,j):
                        new_state = current_state.takeAction(Action(current_state.getCurrentPlayer(), i, j))
                        new_hash = hash(new_state)
                        if new_hash not in all_states:
                            is_end = new_state.isTerminal()
                            all_states[new_hash] = new_state
                            if not is_end:
                                get_all_states_impl(new_state, all_states)
        self.all_states = dict()
        self.all_states[hash(initialState)] = initialState
        get_all_states_impl(initialState, self.all_states)

        for hash_val in self.all_states:
            state = self.all_states[hash_val]
            if state.isTerminal():
                if state.winner == self.player:
                    self.estimations[hash_val] = 1.0
                elif state.winner == 0:
                    # we need to distinguish between a tie and a lose
                    self.estimations[hash_val] = 0.5
                else:
                    self.estimations[hash_val] = 0
            else:
                self.estimations[hash_val] = 0.5
    
    def backup(self):
        states = [hash(state) for state in self.states]

        for i in reversed(range(len(states) - 1)):
            state = states[i]
            next = self.estimations[states[i + 1]]
            current = self.estimations[state]
            td_error = self.greedy[i] * (next - current)
            current_board = self.all_states[state]
            next_board = self.all_states[states[i + 1]]
            new_estimate = current + self.step_size * td_error
            self.estimations[state] += self.step_size * td_error
    
    def search(self, state, train=True):
        action = None
        next_positions = state.getPossibleActions()
        r = random.random()
        if r < self.epsilon and train:
            action = random.choice(next_positions)
        else:
            values = []
            for act in next_positions:
                next_state = state.takeAction(act)
                values.append((self.estimations[hash(next_state)], act))
            
            random.shuffle(values)
            values.sort(key=lambda x: x[0], reverse=True)
            action = values[0][1]
        return action

    def save_policy(self):
        with open('TDpolicy_%s.bin' % ('first' if self.player == 1 else 'second'), 'wb') as f:
            pickle.dump(self.estimations, f)

    def load_policy(self):
        with open('TDpolicy_%s.bin' % ('first' if self.player == 1 else 'second'), 'rb') as f:
            self.estimations = pickle.load(f)


class TDLambda(TDplayer):
    def __init__(self, step_size=0.1, epsilon=0.1, lambdaValue=0.2):
        super().__init__(step_size=step_size, epsilon=epsilon)
        self.lambdaValue = lambdaValue
    
    def backup(self):
        states = [hash(state) for state in self.states]

        for i in reversed(range(len(states) - 1)):
            state = states[i]
            G = 0
            for k in range(i+1, len(states)):
                e = self.estimations[states[k]]
                l = (1-self.lambdaValue)*self.lambdaValue**(k-i-1)
                if k == len(states) - 1:
                    l += (self.lambdaValue)*self.lambdaValue**(k-i-1)
                v = l * e
                G += v
            current = self.estimations[state]
            td_error = self.greedy[i] * (G - current)
            new_estimate = current + self.step_size * td_error
            self.estimations[state] += self.step_size * td_error
    
    def save_policy(self):
        with open('TDLambdaPolicy_%s.bin' % ('first' if self.player == 1 else 'second'), 'wb') as f:
            pickle.dump(self.estimations, f)

    def load_policy(self):
        with open('TDLambdaPolicy_%s.bin' % ('first' if self.player == 1 else 'second'), 'rb') as f:
            self.estimations = pickle.load(f)