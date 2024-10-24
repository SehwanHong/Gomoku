from torch.utils.data import Dataset
import time
import os
from glob import glob
import numpy as np
from utils import isCorrectTime, getFiles, getGameStates
import torch
from random import random

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
        batch_dict = self.board_lists[index]
        gameState = batch_dict['state']
        value = batch_dict['reward']
        value = np.reshape(value, (15,15))

        random_value = random()
        if random_value < 0.25:
            # Horizontal flip
            gameState = gameState[::-1, :]
            value = value[::-1, :]
        elif random_value < 0.5:
            # Vertical flip
            gameState = gameState[:, ::-1]
            value = value[:, ::-1]
        elif random_value < 0.75:
            # Horizontal and Vertical Flip
            gameState = gameState[::-1, ::-1]
            value = value[::-1, ::-1]
        else:
            pass

        value = value.flatten()

        gameState = torch.from_numpy(gameState.astype(np.float32))
        value = torch.from_numpy(value.astype(np.float32))
        return gameState, value


class GomokuDatasetEpisode(Dataset):
    def __init__(
            self,
            save_dir = './data/',
            episodes = 100,
        ):
        super().__init__()
        start = "000000000000"
        end = "991231235959"

        board_files = getFiles(save_dir, start, end)
        print(f"{start} {end} {len(board_files)}")
        assert len(board_files) > episodes

        board_files = board_files[-episodes:]

        self.board_lists = getGameStates(board_files)
        self.N = len(self.board_lists)

    def __len__(self):
        return self.N

    def __getitem__(self, index):
        batch_dict = self.board_lists[index]
        gameState = batch_dict['state']
        value = batch_dict['reward']
        nextState = batch_dict['next_state']
        mask = batch_dict['mask']
        value = np.reshape(value, (15,15))

        random_value = random()
        if random_value < 0.25:
            # Horizontal flip
            gameState = gameState[::-1, :]
            nextState = nextState[::-1, :]
            value = value[::-1, :]
        elif random_value < 0.5:
            # Vertical flip
            gameState = gameState[:, ::-1]
            nextState = nextState[:, ::-1]
            value = value[:, ::-1]
        elif random_value < 0.75:
            # Horizontal and Vertical Flip
            gameState = gameState[::-1, ::-1]
            nextState = nextState[::-1, ::-1]
            value = value[::-1, ::-1]
        else:
            pass

        value = value.flatten()

        gameState = torch.from_numpy(gameState.astype(np.float32))
        nextState = torch.from_numpy(nextState.astype(np.float32))
        value = torch.from_numpy(value.astype(np.float32))
        return {
            "state" : gameState,
            "reward" : value,
            "next_state" : nextState,
            "mask" : mask,
        }



if __name__ == "__main__":
    dataset = GomokuDataset(
        start=None,
        end=None,
    )
    for idx, data in enumerate(dataset):
        if idx > len(dataset) - 3:
            print(data[0])