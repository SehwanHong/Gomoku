from display import MNKDisplay
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

def DQN_selfplay(boardState = Renju):
    boardState = boardState
    player = DQNPlayer(
        searchLimit=100,
        store=True,
    )

    SP = SelfPlay(player)
    winner = SP.play(game=boardState)
    if winner == 1:
        print("p1 win!")
    elif winner == 0:
        print("It is a tie!")
    else:
        print("p2 win!")
    player.saveGamePlay(winner)

if __name__ == "__main__":
    # playGraphicMNK()
    DQN_selfplay()
