from DQN import DQN, DQNPlayer
from judger import Judger
from mnk import mnkState
import multiprocessing
import tensorflow as tf

def evaluateDQN(queue):
    currentBest = DQNPlayer(searchLimit=50)
    currentBest.loadDQN("./weights/DQN_currentBest.h5")
    competitor = DQNPlayer(searchLimit=50)
    competitor.loadDQN("./weights/DQN_newlyTrained.h5")

    # half and half and check win over 55%
    # update the DQN currentBest

    judger = Judger(currentBest, competitor)
    currentBestWin = 0.0
    competitorWin = 0.0
    draw = 0
    for _ in range(3):
        winner = judger.play(game=mnkState)
        if winner == 1:
            currentBestWin += 1
        elif winner == -1:
            competitorWin += 1
        else:
            draw += 1
        judger.reset()
        # print('%d turns, currentBestWin %.02f, competitorWin %.02f, draw %.02f' % (_, currentBestWin, competitorWin, draw))
    judger = Judger(competitor, currentBest)
    for _ in range(3):
        winner = judger.play(game=mnkState)
        if winner == 1:
            competitorWin += 1
        elif winner == -1:
            currentBestWin += 1
        else:
            draw += 1
        judger.reset()
        # print('%d turns, currentBestWin %.02f, competitorWin %.02f, draw %.02f' % (_, currentBestWin, competitorWin, draw))
    
    queue.put(currentBestWin, competitorWin, draw)
    
def MultiEvaluateDQN():
    q = multiprocessing.Queue()
    processes = [multiprocessing.Process(target=evaluateDQN, args=(q,)) for _ in range(5)]
    cB = 0
    comp = 0
    draw = 0

    for p in processes:
        p.start()
    
    for p in processes:
        p.join()
        x, y, z = q.get()
        cB += x
        comp += y
        draw += z
        
    print(cB, comp, draw)
    DQNmodel = DQN()
    if comp / (cB + comp + draw) > .55:
        DQNmodel = DQN()
        DQNmodel.load_weights("./weights/DQN_newlyTrained.h5")
        DQNmodel.save_weights("./weights/DQN_currentBest.h5")

if __name__ == "__main__":
    for i in range(20):
        MultiEvaluateDQN()