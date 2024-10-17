from board import mnkState
from board import Renju
from player import DQNPlayer
from self_play import SelfPlay, EvaluatePlay
from utils import get_newest_model
import argparse

def DQN_selfplay(
        boardState = Renju,
        player=None,
        print_state=False,
        iter=10,
        update_model=False,
        model_dir = None,
        train = True
    ):
    boardState = boardState
    assert player is not None

    SP = SelfPlay(player)
    for i in range(iter):
        winner = SP.play(
            game=boardState,
            train = train,
            print_state=print_state,
        )
        if winner == 1:
            print("p1 win!")
        elif winner == 0:
            print("It is a tie!")
        else:
            print("p2 win!")
        player.saveGamePlay()
        if update_model:
            weightFile, weightFile_old = get_model_path(model_dir=model_dir)
            if weightFile is not None:
                player.loadDQN(weightFile)

def DQN_evaluateplay(boardState = Renju, player_1=None, player_2=None, print_state=False, iter=10):
    boardState = boardState
    assert player_1 is not None
    assert player_2 is not None
    assert iter % 2 == 0

    p1_win_count = 0
    tie_count = 0
    p2_win_count = 0

    EP = EvaluatePlay(player_1, player_2)
    for i in range(iter // 2):
        winner = EP.play(game=boardState, print_state=print_state)
        if winner == 1:
            p1_win_count += 1
            print("p1 win!")
        elif winner == 0:
            tie_count += 1
            print("It is a tie!")
        else:
            p2_win_count += 1
            print("p2 win!")
        player_1.saveGamePlay()
        player_2.saveGamePlay()

    EP = EvaluatePlay(player_2, player_1)
    for i in range(iter // 2):
        winner = EP.play(game=boardState, print_state=print_state)
        if winner == 1:
            p2_win_count += 1
            print("p2 win!")
        elif winner == 0:
            tie_count += 1
            print("It is a tie!")
        else:
            p1_win_count += 1
            print("p1 win!")
        player_1.saveGamePlay()
        player_2.saveGamePlay()
    
    print(f"p1 win count : {p1_win_count:05d}")
    print(f"p2 win count : {p2_win_count:05d}")
    print(f"tie count    : {tie_count:05d}")
    print(f"p1 win rate  : {p1_win_count / iter : 5f}")
    print(f"p2 win rate  : {p2_win_count / iter : 5f}")

    if p1_win_count > p2_win_count:
        return False
    else:
        return True

def parse_args():
    parser = argparse.ArgumentParser(description="Train SVM argparser")
    parser.add_argument('--data_dir', default='./data/', help="data directory")
    parser.add_argument('--model_dir', default='./model_save/', help="model directory")

    parser.add_argument('--store_game_play', action="store_true", help="option for storing gameplay")
    parser.add_argument('--print_state', action="store_true", help="option for printing board")

    parser.add_argument('--search_limit', default=90, type=int, help="limiting of search")
    parser.add_argument('--time_search', action='store_true', help="change search from iteration to time")

    parser.add_argument('--iter', default=10, type=int, help='iteration number')
    parser.add_argument('--self_play', action="store_true" , help='option for selfplay')
    parser.add_argument('--train', action="store_true" , help='option for selfplay')
    parser.add_argument('--update_model', action="store_true" , help='option for selfplay')
    parser.add_argument('--evaluate_model', action="store_true" , help='option for evaluating two model')
    return parser.parse_args()

def get_model_path(model_dir='./model_save/'):
    start, end = get_newest_model(model_dir=model_dir)
    weightFile = None

    if start != '000000000000':
        weightFile_old = model_dir + end + '.pth'

    if end != '000000000000':
        weightFile = model_dir + end + '.pth'
    return weightFile, weightFile_old

if __name__ == "__main__":
    config = parse_args()

    start, end = get_newest_model(model_dir=config.model_dir)
    weightFile = None

    if start != '000000000000':
        weightFile_old = config.model_dir + end + '.pth'

    if end != '000000000000':
        weightFile = config.model_dir + end + '.pth'

    if config.self_play:
        player = DQNPlayer(
            weightfile=weightFile,
            searchLimit=config.search_limit,
            store=config.store_game_play,
            timeSearch=config.time_search,
            device='cpu',
            save_dir=config.data_dir,
        )

        DQN_selfplay(
            player=player,
            print_state=config.print_state,
            iter=config.iter,
            update_model=config.update_model,
            model_dir=config.model_dir,
            train=config.train,
        )

    if config.evaluate_model:
        player_1 = DQNPlayer(
            weightfile=weightFile,
            searchLimit=config.search_limit,
            store=config.store_game_play,
            timeSearch=config.time_search,
            device='cpu',
            save_dir=config.data_dir,
        )

        player_2 = DQNPlayer(
            weightfile=weightFile_old,
            searchLimit=config.search_limit,
            store=config.store_game_play,
            timeSearch=config.time_search,
            device='cpu',
            save_dir=config.data_dir,
        )

        DQN_evaluateplay(
            player_1=player_1,
            player_2=player_2,
            print_state=config.print_state,
            iter=config.iter,
        )