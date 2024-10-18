from torch.utils.data import Dataset
import time
import os
from glob import glob
import numpy as np
from utils import isCorrectTime, getFiles, getGameStates
import torch

class GomokuDataset(Dataset):
    def __init__(
            self,
            save_dir = './data/',
            start = 'YYMMDDHHmmSS',
            end = 'YYMMDDHHmmSS',
        ):
        super().__init__()
        if start is not None and start != '000000000000':
            isCorrectTime(start)
        else:
            start = "000000000000"
        if end is not None and end != '000000000000':
            isCorrectTime(end)
        else:
            end = "991231235959"

        board_files = getFiles(save_dir, start, end)
        print(f"{start} {end} {len(board_files)}")
        assert len(board_files) > 0

        self.board_lists = getGameStates(board_files)
        self.N = len(self.board_lists)

    def __len__(self):
        return self.N

    def __getitem__(self, index):
        gameState, value = self.board_lists[index]
        
        return torch.from_numpy(gameState.astype(np.float32)), torch.from_numpy(value.astype(np.float32))


if __name__ == "__main__":
    dataset = GomokuDataset(
        start=None,
        end=None,
    )
    for idx, data in enumerate(dataset):
        if idx > len(dataset) - 3:
            print(data[0])