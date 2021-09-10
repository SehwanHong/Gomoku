from numpy.testing._private.utils import print_assert_equal
from mcts import MCTS
from tdplayer import TDplayer, TDLambda
from tictactoe import *
from judger import *
from humanplayer import HumanPlayer, mnkHuman
from mnk import mnkState
from display import MNKDisplay
from DQN import *
from tkinter import *

def trainTD(epochs, print_every_n=500):
    player1 = TDplayer(epsilon=0.1)
    player2 = TDplayer(epsilon=0.05)
    judger = Judger(player1, player2)
    player1_win = 0.0
    player2_win = 0.0
    Tie = 0.0
    for i in range(1, epochs//3 + 1):
        winner = judger.play(print_state=False)
        if winner == 1:
            player1_win += 1
        elif winner == -1:
            player2_win += 1
        else :
            Tie += 1
        if i % print_every_n == 0:
            print('Epoch %d, P1: %f, P2: %f, Tie: %f' % (i, player1_win, player2_win, Tie))
            player1_win = 0.0
            player2_win = 0.0
            Tie = 0.0
        player1.backup()
        player2.backup()
        judger.reset()
    mctsplayer = MCTS(iterationLimit=400, epsilon=.2)
    judger = Judger(player1, mctsplayer, set_player=False)
    for i in range(1, epochs//30 + 1):
        winner = judger.play()
        if winner == 1:
            player1_win += 1
        elif winner == -1:
            player2_win += 1
        else :
            Tie += 1
        if ((epochs//3 + i) % print_every_n == 0):
            print('Epoch %d, P1: %f, P2: %f, Tie: %f' % (epochs//3 + i, player1_win, player2_win, Tie))
            player1_win = 0.0
            player2_win = 0.0
            Tie = 0.0
        player1.backup()
        judger.reset()
    judger = Judger(mctsplayer, player2, set_player=False)
    for i in range(1, epochs//30 + 1):
        winner = judger.play()
        if winner == 1:
            player1_win += 1
        elif winner == -1:
            player2_win += 1
        else :
            Tie += 1
        if ((2*epochs//3 + i) % print_every_n == 0):
            print('Epoch %d, P1: %f, P2: %f, Tie: %f' % (epochs//3 + epochs//30 + i, player1_win, player2_win, Tie))
            player1_win = 0.0
            player2_win = 0.0
            Tie = 0.0
        player2.backup()
        judger.reset()
    player1.save_policy()
    player2.save_policy()

def trainTDLambda(epochs, print_every_n=500):
    player1 = TDLambda()
    player2 = TDLambda()
    judger = Judger(player1, player2)
    player1_win = 0.0
    player2_win = 0.0
    Tie = 0.0
    for i in range(1, epochs + 1):
        winner = judger.play(print_state=False)
        if winner == 1:
            player1_win += 1
        elif winner == -1:
            player2_win += 1
        else :
            Tie += 1
        if i % print_every_n == 0:
            print('Epoch %d, P1: %f, P2: %f, Tie: %f' % (i, player1_win, player2_win, Tie))
            player1_win = 0.0
            player2_win = 0.0
            Tie = 0.0
        player1.backup()
        player2.backup()
        judger.reset()
    player1.save_policy()
    player2.save_policy()

def competeTD(turns):
    player1 = TDplayer(epsilon=0)
    player2 = TDplayer(epsilon=0)
    judger = Judger(player1, player2)
    player1.load_policy()
    player2.load_policy()
    player1_win = 0.0
    player2_win = 0.0
    draw = 0
    for _ in range(turns):
        winner = judger.play()
        if winner == 1:
            player1_win += 1
        elif winner == -1:
            player2_win += 1
        else:
            draw += 1
        judger.reset()
    print('%d turns, player 1 win %.02f, player 2 win %.02f, draw %.02f' % (turns, player1_win / turns, player2_win / turns, draw/ turns))

def competeTDLambda(turns):
    player1 = TDLambda(epsilon=0)
    player2 = TDLambda(epsilon=0)
    judger = Judger(player1, player2)
    player1.load_policy()
    player2.load_policy()
    player1_win = 0.0
    player2_win = 0.0
    draw = 0
    for _ in range(turns):
        winner = judger.play()
        if winner == 1:
            player1_win += 1
        elif winner == -1:
            player2_win += 1
        else:
            draw += 1
        judger.reset()
    print('%d turns, player 1 win %.02f, player 2 win %.02f, draw %.02f' % (turns, player1_win / turns, player2_win / turns, draw/ turns))

def mctsCompeteTD(turns):
    player1 = TDplayer(epsilon=0.0)
    player2 = TDplayer(epsilon=0.0)
    mctsplayer = MCTS(iterationLimit=400, epsilon=.2)
    judger = Judger(player1, mctsplayer)
    player1.load_policy()
    TD_win = 0.0
    MCTS_win = 0.0
    draw = 0
    for _ in range(int(turns/2)):
        winner = judger.play()
        if winner == 1:
            TD_win += 1
        elif winner == -1:
            MCTS_win += 1
        else:
            draw += 1
        judger.reset()
    judger = Judger(mctsplayer, player2)
    player2.load_policy()
    for _ in range(int(turns/2)):
        winner = judger.play()
        if winner == 1:
            MCTS_win += 1
        elif winner == -1:
            TD_win += 1
        else:
            draw += 1
        judger.reset()
    print('%d turns, TD win %.02f, MCTS win %.02f, draw %.02f' % (turns, TD_win / turns, MCTS_win / turns, draw/ turns))

def mctsCompeteTDLambda(turns):
    player1 = TDLambda(epsilon=0.0)
    player2 = TDLambda(epsilon=0.0)
    mctsplayer = MCTS(iterationLimit=400, epsilon=.2)
    judger = Judger(player1, mctsplayer)
    player1.load_policy()
    TD_win = 0.0
    MCTS_win = 0.0
    draw = 0
    for _ in range(int(turns/2)):
        winner = judger.play()
        if winner == 1:
            TD_win += 1
        elif winner == -1:
            MCTS_win += 1
        else:
            draw += 1
        judger.reset()
    judger = Judger(mctsplayer, player2)
    player2.load_policy()
    for _ in range(int(turns/2)):
        winner = judger.play()
        if winner == 1:
            MCTS_win += 1
        elif winner == -1:
            TD_win += 1
        else:
            draw += 1
        judger.reset()
    print('%d turns, TD Lambda win %.02f, MCTS win %.02f, draw %.02f' % (turns, TD_win / turns, MCTS_win / turns, draw/ turns))

def playTicTacToe():
    while True:
        key = 'r'
        player = 0
        while key not in {'m', 't', 'l', 'q'}:
            if key == 'r':
                print("'m' for monte-carlo tree search algorithm")
                print("'t' for td(0) player")
                print("'l' for td Lambda")
                print("'q' for quit the game")
                print("'r' for print option again")
            key = input("Which player you want to play against? \t")
        if key == 'q':
            break
        while player not in {1,2}:
            player = int(input("which player you want to play, select from 1 or 2 : "))
            
        human = HumanPlayer()
        td = None
        tdl = None
        mctsPlayer = None
        judger = None
        wincondition = 1

        if key == 'm':
            mctsPlayer = MCTS(iterationLimit=50)
            if player == 1:
                judger = Judger(human, mctsPlayer)
            else:
                wincondition = -1
                judger = Judger(mctsPlayer, human)
        elif key == 't':
            td = TDplayer(epsilon=0)
            if player == 1:
                judger = Judger(human, td)
            else:
                wincondition = -1
                judger = Judger(td, human)
            td.load_policy()
        elif key == 'l':
            tdl = TDLambda(epsilon=0)
            if player == 1:
                judger = Judger(human, tdl)
            else:
                wincondition = -1
                judger = Judger(tdl, human)
            tdl.load_policy()
        else:
            judger = Judger(human, human)
            
        winner = judger.play(print_state=True)
        if winner == wincondition:
            print("You win!")
        elif winner == 0:
            print("It is a tie!")
        else:
            print("You lose!")
        
        quit = input("'q' to quit, otherwise continue : ")
        if (quit == 'q'):
            break;

def playMNK():
    p1 = mnkHuman()
    p2 = MCTS(timeLimit=2000)
    judge = Judger(p1, p2)

    while True:
        winner = judge.play(game=mnkState, print_state=True)
        if winner == 1:
            print("p1 win!")
        elif winner == 0:
            print("It is a tie!")
        else:
            print("p2 win!")
        
        quit = input("'q' to quit, otherwise continue : ")
        if (quit == 'q'):
            break;

def playGraphicMNK():
    root = Tk()
    display = MNKDisplay(root, mnkState, 7, 7, 5)
    display.mainloop()
    root.mainloop()

def selfPlay(gameCount=0):
    dqnp1 = DQNPlayer(searchLimit=5, gameCount=gameCount)
    # dqnp2 = DQNPlayer(searchLimit=200)
    while dqnp1.gameCount < gameCount + 500:
        SP = SelfPlay(dqnp1)
        dqnp1.loadDQN("./weights/DQN_currentBest.h5")
        for i in range(50):
            winner = SP.play(game=mnkState)
            if winner == 1:
                print("p1 win!")
            elif winner == 0:
                print("It is a tie!")
            else:
                print("p2 win!")
            dqnp1.backup(winner)
    

if __name__ == "__main__":
    # trainTDLambda(int(1e5))
    # compete(int(1e3))
    # mctsCompete(int(100))
    # mctsCompeteTDLambda(100)
    # playTicTacToe()
    # playMNK()
    playGraphicMNK()
    # gpus = tf.config.list_physical_devices('GPU')
    # print(gpus)
    # if gpus:
    #     # Restrict TensorFlow to only allocate 1GB of memory on the first GPU
    #     try:
    #         tf.config.experimental.set_virtual_device_configuration(
    #                 gpus[0],
    #                 [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=1000)])
    #         logical_gpus = tf.config.experimental.list_logical_devices('GPU')
    #         print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
    #     except RuntimeError as e:
    #         # Virtual devices must be set before GPUs have been initialized
    #         print(e)
            
    # gameCount = int(input("gameCount:"))
    # for i in range(20):
    # selfPlay(0)
    #     gameCount += 16
