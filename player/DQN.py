from .player import Player
from model import DQN
from board import boardState

import numpy as np
import math
from treenode import DQNNode
import random
import time
import torch
from tqdm import tqdm
import ray

class DQNPlayer(Player):
    save_format = '%y%m%d%H%M%S'

    def __init__(
            self,
            searchLimit=800,
            timeSearch=False,
            weightfile=None,
            store = False,
            device = 'mps'
        ):
        if weightfile == None:
            self.DQNnet = DQN()
        else:
            # Load weight
            self.loadDQN(weightfile)
        
        self.searchLimit = searchLimit
        self.timeSearch = timeSearch

        self.episode = None
        self.explorationConstant = math.sqrt(2)
        
        self.store = store
        self.device = device

        self.DQNnet.to(device=self.device)
        ray.init(num_cpus = 10)

    def reset(self, gameState):
        self.prevStates = []
        self.list_action = []
        self.pred_Q_value = []
        self.root = DQNNode(gameState, None)
        self.gamePlayStartTime = time.localtime()

    def loadDQN(self, weightfile):
        self.DQNnet = DQN()
        self.DQNnet.load_state_dict(torch.load(weightfile))
    
    def search(self, state, train=True, self_play=True):
        t = time.time()
        i = 0
        if self.timeSearch:
            timeLimit = time.time() + self.searchLimit
            while time.time() < timeLimit:
                print("\rsearch {} th".format(i+1), end='')
                self.executeRound()
                i += 1
        else:
            for i in tqdm(range(self.searchLimit)):
                # print("\rsearch {} th".format(i+1), end='')
                self.executeRound()
        t2 = time.time()-t
        print("\t took {} sec".format(t2))

        print(self.root)
        
        action = self.getBestChild(self.root, deterministic=not train)
        self.playAction(action)

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
    
    def playAction(self, action):
        # Reuse previous search results
        self.root = self.root.children[action]
        self.root.parent = None
    
    def executeRound(self):
        """
            execute a selection-expansion-simulation-backpropagation round
        """
        node, reward = self.selectNode(self.root)
        # roll out using DQN funciton
        self.backpropogate(node, reward)

    def selectNode(self, node):
        # if not expended and not terminal find node that is best
        while not node.N == 0 and not node.isTerminal:
            node = self.evaluateNode(node, self.explorationConstant)
        return self.expand(node)

    def expand(self, node):
        actions = node.state.getPossibleActions()
        if len(actions) == 0:
            return node, node.state.winner * node.state.currentStone
        else:
            start = time.time()
            gameState = self.generateGameState(node) #Generate Game State
            gameState = torch.from_numpy(gameState).to(device=self.device)
            prediction = self.DQNnet(gameState)
            Q_value = prediction[0]

            node.pQ = Q_value

            # make expand with Q and U value
            newNodes = ray.get([__class__.createNode.remote(node, action) for action in actions])
            
            for idx, action in tqdm(enumerate(actions), leave=False):
                if action not in node.children:
                    node.children[action] = newNodes[idx]
                    node.children[action].pQ = Q_value[7*action.x + action.y]

            return node, Q_value.sum()
    
    @staticmethod
    @ray.remote
    def createNode(node, action):
        return DQNNode(node.state.takeAction(action), node)

    def saveGamePlay(self):
        np.savez(time.strftime(DQNPlayer.save_format, self.gamePlayStartTime), board=self.prevStates, value=self.pred_Q_value)

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
                gameStates.append(self.prevStates[x - i])
        return self.listToGameState(gameStates, player)
    
    def listToGameState(self, gameStates, player):
        base = gameStates[0].shape
        gameState = np.zeros((7, base[0], base[1]), dtype=np.float32)
        i = 0
        for gs in gameStates:
            gameState[i, :, :] = gs > 0
            gameState[i+3, : , :] = gs < 0
            i += 0
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
    def evaluateNode(node, explorationConstant):
        # Select move with most visits if competitive or select move with categorical distribution
        bestValue = float("-inf")
        bestNodes = []
        for action, child in node.children.items():
            # nodeValue = node.state.getcurrentStone() * child.Q + self.explorationConstant * child.P /(1 + child.N)
            nodeValue = __class__.calculateQValue(child, explorationConstant, node.pQ[7*action.x + action.y])
            if nodeValue > bestValue:
                bestValue = nodeValue
                bestNodes = [child]
            elif nodeValue == bestValue:
                bestNodes.append(child)
        
        return random.choice(bestNodes)

    @staticmethod
    def calculateQValue(node, explorationConstant, parentpQ):
        return -1 * node.Q + explorationConstant * parentpQ /(1 + node.N)
    
    @staticmethod
    def getBestChild(node, deterministic=True):
        if deterministic:
            bestValue = 0
            bestNodes = []
            for action, child in node.children.items():
                nodeValue = child.N
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