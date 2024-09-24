from DQN import DQN, DQNPlayer
import tensorflow as tf
import numpy as np
import random
import pandas as pd
from judger import Judger
from mnk import mnkState
import multiprocessing
import time

BATCHSIZE = 2048
EPOCH = 1000
DQNmodel = DQN()
DQNmodel.summary()

def train(lr=0.2):
    filenames = []
    c = 0
    for i in range(100000, -1, -1):
        try:
            filenames.extend(pd.read_csv("./csvfiles/traindata_{:05}.csv".format(i))['name'])
            c += 1
            if c >= 80:
                break
        except:
            continue
    if c < 80:
        for i in range(200, -1, -1):
            try:
                filenames.extend(pd.read_csv("./csvfiles/traindata_{:03}.csv".format(i))["name"])
                c += 1
                if c >= 80:
                    break
            except:
                continue
    
    # load weights for training
    try:
        DQNmodel.load_weights("./weights/DQN_currentBest.h5")
        print("load weight success")
    except OSError:
        print("load failed, using backup")
        DQNmodel.load_weights("./weights/DQN_backup.h5")
    finally:
        DQNmodel.compile(optimizer=tf.keras.optimizers.SGD(learning_rate=lr, momentum=0.9),
                        loss={"Value":'mse',"Policy":tf.keras.losses.CategoricalCrossentropy()})
        DQNmodel.fit(generator(filenames), verbose=1, epochs=1, steps_per_epoch=EPOCH)
        while True:
            try:
                DQNmodel.save_weights("./weights/DQN_currentBest.h5")
                DQNmodel.save_weights("./weights/DQN_backup.h5")
            except:
                pass
            else:
                print("save weights")
                break
        return 1

def generator(filenames, bsize=BATCHSIZE):
    count = 0
    counter = 0
    gameState = []
    policy = []
    value = []
    while True:
        for i in range(bsize):
            filename = random.choice(filenames)
            data = np.load(filename)
            gameState.append(data["GameState"][0])
            policy.append(data["Probability"])
            value.append(data["Reward"])
        counter += 1
        yield (np.array(gameState), {'Policy':np.array(policy), 'Value':np.array(value)})
        gameState = []
        policy = []
        value = []
        if counter == EPOCH:
            counter = 0

if __name__ == "__main__":
    gpus = tf.config.list_physical_devices('GPU')
    print(gpus)
    if gpus:
        # Restrict TensorFlow to only allocate 1GB of memory on the first GPU
        try:
            tf.config.experimental.set_virtual_device_configuration(
                    gpus[0],
                    [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=4000)])
            logical_gpus = tf.config.experimental.list_logical_devices('GPU')
            print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
        except RuntimeError as e:
            # Virtual devices must be set before GPUs have been initialized
            print(e)
    LR = 0.2
    i = 0
    while i < 10000000000:
        try:
            if i % 4000 == 3999:
                LR = LR * 0.99
            print("EPOCH {:010}".format(i))
            i += train(lr=LR)
        except KeyboardInterrupt:
            break
