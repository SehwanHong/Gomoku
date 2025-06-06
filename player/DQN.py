from action import Action
from .player import Player
from model import DQN
from board import boardState
from policy import randomPolicy

import numpy as np
import math
from treenode import DQNNode
import random
import time
import torch
from tqdm import tqdm
import os

class DQNPlayer(Player):
    save_format = '%y%m%d%H%M%S'

    def __init__(
            self,
            searchLimit=800,
            timeSearch=False,
            weightfile=None,
            store = False,
            device = 'mps',
            save_dir = "./data/",
            # rolloutPolicy=randomPolicy,
        ):

        self.searchLimit = searchLimit
        self.timeSearch = timeSearch

        self.episode = None
        self.explorationConstant = math.sqrt(2)
        
        self.store = store
        self.save_dir = save_dir
        self.device = device
        # self.rollout = __class__.randomPolicy
        
        if weightfile == None:
            self.DQNnet = DQN()
        else:
            # Load weight
            self.loadDQN(weightfile)
        
        self.DQNnet.to(device=self.device)

    def reset(self, gameState):
        self.prevStates = []
        self.list_action = []
        self.pred_Q_value = []
        self.root = DQNNode(gameState, None)

    def loadDQN(self, weightfile):
        self.DQNnet = DQN()
        self.DQNnet.load_state_dict(torch.load(weightfile, map_location=torch.device(self.device)))
    
    def search(self, state, train=True, print_state=True):
        t = time.time()
        i = 0
        if self.timeSearch:
            timeLimit = time.time() + self.searchLimit
            while time.time() < timeLimit:
                # print("\rsearch {} th".format(i+1), end='')
                self.executeRound(deterministic=not train)
                i += 1
        else:
            for i in tqdm(range(self.searchLimit)):
                self.executeRound(deterministic=not train)
        t2 = time.time()-t
        if print_state:
            print(f"took {t2} sec, iteration {i}")
            print(self.root)
        action = self.getBestChild(self.root, self.explorationConstant, deterministic=not train)
        self.playAction(action, preserve=False)

        # update game state and store
        # store gamestate and action
        if self.store:
            Q_value = np.zeros(state.board.size)
            for act, child in self.root.children.items():
                Q_value[7*act.x+act.y] += child.Q
            self.pred_Q_value.append(Q_value)
            self.prevStates.append(state)
            self.list_action.append(action)

        return action
    
    def playAction(self, action, preserve = True):
        # Reuse previous search results
        if preserve:
            self.root = self.root.children[action]
            
            parentNode = self.root.parent
            self.root.parent = None

            del parentNode
        else:
            self.root = self.createNode(self.root, action)
            self.root.parent = None
   
    def executeRound(self, deterministic = True):
        """
            execute a selection-expansion-simulation-backpropagation round
        """
        node, imidate_reward = self.selectNode(self.root, deterministic)
        late_reward = __class__.randomPolicy(node.state)
        late_reward = late_reward * node.state.currentStone
        # roll out using DQN funciton
        reward = imidate_reward + late_reward * 100
        __class__.backpropogate(node, reward)

    def selectNode(self, node, deterministic = True):
        # if not expended and not terminal find node that is best
        action = None
        while not node.N == 0 and not node.isTerminal:
            node = self.evaluateNode(node, self.explorationConstant, deterministic=deterministic)
            if not node.isFullyExpanded:
                break

        node, reward = self.expand(node)
        return node, reward

    def expand(self, node):
        actions = node.state.getPossibleActions()
        if len(actions) == 0:
            return node, node.state.winner * node.state.currentStone
        else:
            if len(node.children) == 0:
                gameState = self.generateGameState(node) #Generate Game State
                gameState = torch.from_numpy(gameState).to(device=self.device)
                prediction = self.DQNnet(gameState)
                Q_value = prediction[0]

                node.pQ = Q_value

            if len(node.children) <= len(actions):
                new_pQ = node.pQ.clone()
                while True:
                    arg_xy = torch.argmax(new_pQ)
                    action = Action(node.state.currentStone, arg_xy//node.state.row, arg_xy%node.state.col)
                    if action in actions and action not in node.children:
                        bestNode = __class__.createNode(node, action)
                        node.children[action] = bestNode
                        break
                    else:
                        new_pQ[arg_xy] = float("-inf")

            if len(node.children) == len(actions):
                node.isFullyExpanded = True

            if action != None:
                three_reward = node.state.isThree(action.x, action.y, node.state.currentStone) * 20
                four_reward = node.state.isFour(action.x, action.y, node.state.currentStone) * 50

                return bestNode, three_reward + four_reward
            else:
                return bestNode, 0


    @staticmethod
    # @ray.remote
    def createNode(node, action):
        return DQNNode(node.state.takeAction(action), node)

    def saveGamePlay(self):
        if self.store:
            self.gamePlayStartTime = time.gmtime()
            filename = time.strftime(DQNPlayer.save_format, self.gamePlayStartTime) + ".npz"
            filepath = os.path.join(self.save_dir, filename)
            np.savez(filepath, board=self.prevStates, value=self.pred_Q_value, action=self.list_action)

    def generateGameState(self, node):
        gameStates = []
        player = node.state.currentStone
        count = 0
        while count < 3:
            gameStates.append(node.state.board)
            count += 1
            if node.parent != None:
                node = node.parent
            else:
                break
        x = len(self.prevStates)
        for i in range(count,3):
            if x - i > 0:
                gameStates.append(self.prevStates[x - i].board)
        return self.listToGameState(gameStates, player)
    
    def listToGameState(self, gameStates, player):
        base = gameStates[0].shape
        gameState = np.zeros((7, base[0], base[1]), dtype=np.float32)
        i = 0
        for idx, gs in enumerate(gameStates):
            gameState[idx, :, :] = gs > 0
            gameState[idx+3, : , :] = gs < 0
        gameState[-1,:,:] = player
        return gameState.reshape((1, 7, base[0], base[1]))

    @staticmethod 
    def backpropogate(node, reward):
        r = reward
        while node is not None:
            node.N += 1
            node.W += r
            node.Q = node.W/node.N
            node = node.parent
            r *= -1
    
    @staticmethod
    def evaluateNode(node, explorationConstant, deterministic = True):
        # Select move with most visits if competitive or select move with categorical distribution
        # if len(node.children) > 0:
        if len(node.children) > len(node.state.getPossibleActions()):
            raise ValueError
        elif len(node.children) == len(node.state.getPossibleActions()):
            action = __class__.getBestChild(node, explorationConstant, deterministic)
            return node.children[action]
        else:
            return node
                    

    @staticmethod
    def calculateQValue(node, explorationConstant, parentpQ):
        return -1 * node.Q + explorationConstant * parentpQ /(1 + node.N)
    
    @staticmethod
    def getBestChild(node, explorationConstant, deterministic=True):
        if deterministic:
            bestValue = 0
            bestNodes = []
            for action, child in node.children.items():
                nodeValue = __class__.calculateQValue(child, explorationConstant, node.pQ[7*action.x + action.y])
                if child.N > bestValue:
                    bestValue = nodeValue
                    bestNodes = [action]
                elif child.N == bestValue:
                    bestNodes.append(action)

            return random.choice(bestNodes)
        else:
            epsilon = random.randrange(1, node.N)
            select = 0
            for action, child in node.children.items():
                select += child.N
                if select >= epsilon:
                    return action
    
    @staticmethod
    def randomPolicy(state):
        count = 0
        while not state.isTerminal():
            try:
                action = random.choice(state.getPossibleActions())
            except IndexError:
                raise Exception("Non-terminal state has no possible actions: " + str(state))
            state = state.takeAction(action)
            count += 1
        return state.getReward()
