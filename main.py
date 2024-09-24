from display import MNKDisplay
from tkinter import *
from board import mnkState

def playGraphicMNK():
    root = Tk()
    display = MNKDisplay(root, mnkState, 15, 15, 5)
    display.mainloop()
    root.mainloop()

if __name__ == "__main__":
    playGraphicMNK()