from torch.utils.data import Dataset
import time
import os
from glob import glob
import numpy as np
from utils import isCorrectTime

class GomokuDataset(Dataset):
    def __init__(
            self,
            save_dir = './data/',
            start = 'YYMMDDHHmmSS',
            end = 'YYMMDDHHmmSS',
        ):
        super().__init__()
        if start is not None and start is not '000000000000':
            isCorrectTime(start)
        else:
            start = "000000000000"
        if end is not None and end is not '000000000000':
            isCorrectTime(end)
        else:
            end = "991231235959"

        board_files = GomokuDataset.getFiles(save_dir, start, end)
        print(board_files)

        self.board_lists = GomokuDataset.getGameStates(board_files)
        self.N = len(self.board_lists)

    @staticmethod
    def getGameStates(board_files):
        board_lists = []
        for file_name in board_files:
            numpy_file = np.load(file_name, allow_pickle=True)
            boards = numpy_file['board']
            values = numpy_file['value']
            row = boards[0].row
            col = boards[0].col
            for idx, value in enumerate(values):
                if idx < 3:
                    gameBoard = []
                    for i in range(3):
                        gameBoard.append(boards[idx])
                        idx -= 1
                        if idx < 0:
                            idx = 0
                else:
                    gameBoard = boards[idx:idx-3:-1]
                assert len(gameBoard) == 3, f"{idx} {len(gameBoard)}"
                gameState = np.zeros((7, row, col))
                for idx, gs in enumerate(gameBoard):
                    gameState[idx, :, :] = gs.board > 0
                    gameState[idx+3, : , :] = gs.board < 0
                gameState[-1, :, :] = boards[idx].currentStone
                board_lists.append((gameState, value))

        size = board_lists[0][0].shape
        for gameBoard, value in board_lists:
            assert size == gameBoard.shape
        
        return board_lists

    def __len__(self):
        return self.N

    def __getitem__(self, index):
        gameState, value = self.board_lists[index]
        return gameState, value

    @staticmethod
    def getFiles(dir, start, end):
        """
        This function retrieves all image files within a folder using glob.
        Args:
            folder_path: Path to the folder to search.
            extensions: Tuple of image file extensions (defaults to common formats).
        Returns:
            A list containing the full paths of all image files.
        """
        board_files = []
        for file_path in glob(os.path.join(dir, f"**/*.npz"), recursive=True):
            filename = os.path.basename(file_path)
            time_created = filename[:-4]
            isCorrectTime(time_created)
            if int(time_created) >= int(start) and int(time_created) <= int(end):
                board_files.append(file_path)
        return board_files
    

if __name__ == "__main__":
    dataset = GomokuDataset(
        start=None,
        end=None,
    )
    for idx, data in enumerate(dataset):
        if idx > len(dataset) - 3:
            print(data[0])