from tensorflow.keras import activations
from player import Player
import numpy as np
import tensorflow as tf
import math
from treenode import DQNNode
import random
import time

class DQNPlayer(Player):
    def __init__(self, searchLimit=800, weightfile=None, gameCount=0):
        # weight file with none create initialize or loade weight file
        self.episode = None
        # load weight
        self.DQNnet = DQN()
        # self.DQNnet.summary()
        self.searchLimit = searchLimit
        self.explorationConstant = math.sqrt(2)
        self.prevStates = []
        self.probPolicy = []
        self.gsfile = "./train_800/Game_{:010}/{:02}.npz"
        self.trainData = "./csvfiles/traindata_{:05}.csv"
        self.gameCount = gameCount
        self.time = False

    def reset(self):
        self.prevStates = []
        self.probPolicy = []
    
    def set_state(self, state):
        self.prevStates.append(state.board)
    
    def backup(self, winner):
        # Store gameState
        f = open(self.trainData.format(self.gameCount//1000), 'a')
        if( self.gameCount%1000 == 0):
            f.write("name\n")
        player = 1
        reward = [0.9**i * (-1)**i for i in range(len(self.probPolicy))]
        for i in range(len(self.probPolicy)):
            x = i - 3
            if i < 3:
                x = 0
            arr = self.listToGameState(self.prevStates[i:x:-1], player)
            filename = self.gsfile.format(self.gameCount, i)
            np.savez(filename, GameState=arr, Probability=self.probPolicy[i], Reward=reward[-i])
            f.write(filename+'\n')
            player *= -1
        self.gameCount += 1
        f.close()

    def loadDQN(self, filename, backup="./weights/DQN_backup.h5"):
        while True:
            try:
                self.DQNnet.load_weights(filename)
                print("loaded")
            except OSError:
                print("load failed, using backup")
                self.DQNnet.load_weights(backup)
                break
            else:
                break
    
    def search(self, state, train=True):
        self.root = DQNNode(state, None)
        t = time.time()
        i = 0
        if self.time:
            timeLimit = time.time() + 29.8
            while time.time() < timeLimit:
                print("\rsearch {} th".format(i+1), end='')
                self.executeRound()
                i += 1
        else:
            for i in range(self.searchLimit):
                print("\rsearch {} th".format(i+1), end='')
                self.executeRound()
        t2 = time.time()-t
        print("\t took {} sec".format(t2))
        
        action = self.getBestChild(self.root, deterministic=not train)
        #store gamestate and action
        probability = np.zeros(7*7)
        for act, child in self.root.children.items():
            probability[7*act.x+act.y] += child.N/self.root.N
        self.probPolicy.append(probability)
        return action
    
    def executeRound(self):
        """
            execute a selection-expansion-simulation-backpropagation round
        """
        node, reward = self.selectNode(self.root)
        # roll out using DQN funciton
        self.backpropogate(node, reward)

    def selectNode(self, node):
        while not node.N == 0 and not node.isTerminal:
            node = self.evaluateNode(node)
        return self.expand(node)

    def expand(self, node):
        actions = node.state.getPossibleActions()
        if len(actions) == 0:
            return node, node.state.winner * node.state.currentPlayer
        else:
            gameState = self.generateGameState(node) #Generate Game State
            prediction = self.DQNnet.predict(gameState)
            value = prediction[0][0][0]
            policy = prediction[1][0]
            policysum = sum(policy)
            # make expand with Q and U value
            for action in actions:
                if action not in node.children:
                    newNode = DQNNode(node.state.takeAction(action), node)
                    node.children[action] = newNode
                    newNode.P = policy[7*action.x + action.y]
            return node, value

    def backpropogate(self, node, reward):
        r = reward
        while node is not None:
            node.N += 1
            node.W += r
            node.Q = node.W/node.N
            node = node.parent
            r *= -1

    def evaluateNode(self, node):
        # Select move with most visits if competitive or select move with categorical distribution
        bestValue = float("-inf")
        bestNodes = []
        for child in node.children.values():
            # nodeValue = node.state.getCurrentPlayer() * child.Q + self.explorationConstant * child.P /(1 + child.N)
            nodeValue = -1 * child.Q + self.explorationConstant * child.P /(1 + child.N)
            if nodeValue > bestValue:
                bestValue = nodeValue
                bestNodes = [child]
            elif nodeValue == bestValue:
                bestNodes.append(child)
        return random.choice(bestNodes)
    
    def getBestChild(self, node, deterministic=True):
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

    def generateGameState(self, node):
        gameStates = []
        player = node.state.currentPlayer
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
        gameState = np.zeros((7,7,7))
        i = 0
        for gs in gameStates:
            gameState[:,:,i] = gs > 0
            gameState[:,:,i+3] = gs < 0
            i += 0
        gameState[:,:,-1] = player > 0
        return gameState.reshape((1,7,7,7))

def DQN(shape=(7,7,7)):
    inx = tf.keras.Input(shape)
    x = ConvHead(inx)
    for i in range(10):
        x = Residual(x)
    value = Value(x)
    policy = Policy(x)
    return tf.keras.Model(inputs=inx, outputs=[value, policy])
    

def ConvHead(input):
    x = tf.keras.layers.Conv2D(64, 3, padding='same')(input)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.ReLU()(x)
    return x

def Residual(input):
    x = ConvHead(input)
    x = tf.keras.layers.Conv2D(64, 3, padding='same')(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Add()([input, x])
    return x

def Value(input):
    x = tf.keras.layers.Conv2D(1, 1, padding='same')(input)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.ReLU()(x)
    x = tf.keras.layers.Flatten()(x)
    x = tf.keras.layers.Dense(64)(x)
    x = tf.keras.layers.ReLU()(x)
    x = tf.keras.layers.Dense(1)(x)
    x = tf.keras.layers.Activation('tanh', name='Value')(x)
    return x

def Policy(input):
    x = tf.keras.layers.Conv2D(2, 1, padding='same')(input)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.ReLU()(x)
    x = tf.keras.layers.Flatten()(x)
    x = tf.keras.layers.Dense(7*7, activation='softmax', name="Policy")(x)
    return x
