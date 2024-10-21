from display import MNKDisplay, RenjuDisplay
from tkinter import *
from board import mnkState
from board import Renju
from player import DQNPlayer
from self_play import SelfPlay

def playGraphicMNK():
    root = Tk()
    display = MNKDisplay(root, Renju, 15, 15, 5)
    display.mainloop()
    root.mainloop()

def playGraphicRenju():
    root = Tk()
    display = RenjuDisplay(root)
    display.mainloop()
    root.mainloop()

def DQN_selfplay(boardState = Renju, player=None):
    boardState = boardState
    assert player is not None

    SP = SelfPlay(player)
    winner = SP.play(game=boardState, print_state=True)
    if winner == 1:
        print("p1 win!")
    elif winner == 0:
        print("It is a tie!")
    else:
        print("p2 win!")
    player.saveGamePlay()

if __name__ == "__main__":
    # playGraphicMNK()
    playGraphicRenju()
    # player = DQNPlayer(
    #     searchLimit=90,
    #     store=True,
    #     timeSearch=True,
    #     device='cpu'
    # )
    # DQN_selfplay(player=player)
