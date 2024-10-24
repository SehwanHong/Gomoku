import os
from glob import glob
import numpy as np

def isCorrectTime(time_str):
    assert len(time_str) == 12
    YY = time_str[:2]
    assert int(YY) >= 0 and int(YY) <= 99
    MM = time_str[2:4]
    assert int(MM) >= 1 and int(MM) <= 12
    DD = time_str[4:6]
    assert int(DD) >= 1 and int(DD) <= 31
    HH = time_str[6:8]
    assert int(HH) >= 0 and int(HH) <= 23
    mm = time_str[8:10]
    assert int(mm) >= 0 and int(mm) <= 59
    SS = time_str[10:12]
    assert int(SS) >= 0 and int(SS) <= 59

def get_newest_model(model_dir="./model/"):
    model_list = glob(model_dir + "**.pth", recursive=True)
    newest = '000000000000'
    second_newest = '000000000000'
    for model in model_list:
        filename = os.path.basename(model)
        time_created = filename[:-4]
        isCorrectTime(time_created)
        if int(time_created) >= int(newest):
            second_newest = newest
            newest = time_created
    return second_newest, newest

def getGameStates(board_files):
    board_lists = []
    for file_name in board_files:

        numpy_file = np.load(file_name, allow_pickle=True)
        boards = numpy_file['board']
        values = numpy_file['value']
        row = boards[0].row
        col = boards[0].col
        game_length = len(value)
        single_episode_list = []
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

            single_episode_list.append((gameState, value))
        

        for idx, batch in enumerate(single_episode_list):
            gameState, value = batch
            board_lists.append({
                "state" : gameState,
                "reward" : value,
                "next_state" : single_episode_list[idx + 1] if idx < game_length else None,
                "mask" : True if idx < game_length else False,
            })

    size = board_lists[0]['state'].shape
    for batch in board_lists:
        assert size == batch['state'].shape
    
    return board_lists

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
