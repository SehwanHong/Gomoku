from board_dataset import GomokuDataset, GomokuDatasetEpisode
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch import optim
import lightning
from lightning import Fabric
import argparse
import wandb
from glob import glob
import os
from utils import isCorrectTime, get_newest_model
from model import DQN
import time
from utils import getFiles

def parse_args():
    parser = argparse.ArgumentParser(description="Train SVM argparser")
    parser.add_argument('--run_name', default="run")
    parser.add_argument('--data_dir', default='./data/', help="data directory")
    parser.add_argument('--model_dir', default='./model_save/', help="model directory")

    parser.add_argument('--batch_size', default=8, type=int, help="batch size")
    parser.add_argument('--lr', default=1e-3, type=float, help="initial learning rate")
    parser.add_argument('--total_epoch', default=200, type=int, help="total_epoch")
    parser.add_argument('--num_worker', default=8, type=int, help="number of worker")
    parser.add_argument('--dropout_rate', default=0.4, type=float, help="number of worker")

    parser.add_argument('--model_update_count', default=10, type=int, help="how much time for updating model")
    parser.add_argument('--hard_update', action='store_true', help="train model with hard update")
    parser.add_argument('--soft_update', action='store_true', help="train model with soft update")
    parser.add_argument('--tau', default=5e-3, type=float, help="option for soft update")
    parser.add_argument('--episodes', default=100, type=int, help="option for soft update")
    parser.add_argument('--gamma', default=0.99, type=float, help="option for soft update")
    return parser.parse_args()

def train_hard(config):    
    start, end = get_newest_model(
        model_dir=config.model_dir,
    )

    model = DQN()

    pytorch_total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    # wandb.config.update({"num_param": pytorch_total_params})

    print(f"pytorch total_params : {pytorch_total_params}")

    model = fabric.setup(model)

    ''' Define Else '''
    # criterion = nn.CrossEntropyLoss()
    # criterion = nn.BCEWithLogitsLoss()
    # criterion = LabelSmoothSoftmaxCEV1(lb_smooth=0.1).cuda()
    criterion = nn.MSELoss()

    if end != '000000000000':
        model.load_state_dict(torch.load(config.model_dir + end + '.pth'))
    
    first_lr = config.lr
    optimizer = optim.SGD(
        model.parameters(),
        lr=first_lr, momentum=0.9, weight_decay=5e-4, nesterov=False
    )

    _, newest_time = get_newest_model(
        model_dir=config.model_dir,
    )

    curr_time = time.gmtime()

    for epoch in range(config.total_epoch):
        dataset = GomokuDataset(
            save_dir=config.data_dir,
            start = newest_time,
            end = None,
        )
        
        dataloader = DataLoader(
            dataset,
            batch_size=config.batch_size,
            shuffle=True,
            num_workers=config.num_worker,
            pin_memory=True,
            drop_last=True,
        )

        cur_iter = 0
        total_loss = 0

        dataloader = fabric.setup_dataloaders(dataloader)

        for batch in dataloader:
            board = batch['state']
            qvalue = batch['reward']
            optimizer.zero_grad()
            outputs = model(board)

            loss = criterion(outputs, qvalue)

            total_loss += loss.item()
            if cur_iter % 250 == 0:
                # wandb.log({
                #     'iter': cur_iter,
                #     'loss' : loss,
                # })
                print(f"iter : {cur_iter :08d} \t loss : {loss:08f}")

            cur_iter += 1

            loss.backward()
            optimizer.step()

        print(f"current epoch {epoch}")
        print(f'total_loss: {round(total_loss, 4)} ({round(total_loss/cur_iter, 4)})')
        # wandb.log({
        #     'epoch': epoch,
        #     'total_loss' : total_loss,
        #     'avg_loss' : total_loss/cur_iter,
        # })
    
    save_format = '%y%m%d%H%M%S'
    filename = time.strftime(save_format, curr_time) + ".pth"
    filepath = os.path.join(config.model_dir, filename)
    
    print(f"saved to {filepath}")
    torch.save(model.state_dict(), filepath)

def train_soft(config):
    start, end = get_newest_model(
        model_dir=config.model_dir,
    )

    policy_net = DQN()
    target_net = DQN()


    pytorch_total_params = sum(p.numel() for p in policy_net.parameters() if p.requires_grad)
    # wandb.config.update({"num_param": pytorch_total_params})

    print(f"pytorch total_params : {pytorch_total_params}")

    policy_net = fabric.setup(policy_net)
    target_net = fabric.setup(target_net)

    ''' Define Else '''
    # criterion = nn.CrossEntropyLoss()
    # criterion = nn.BCEWithLogitsLoss()
    # criterion = LabelSmoothSoftmaxCEV1(lb_smooth=0.1).cuda()
    # criterion = nn.MSELoss()
    criterion = nn.SmoothL1Loss()

    if end != '000000000000':
        policy_net.load_state_dict(torch.load(config.model_dir + end + '.pth'))
        target_net.load_state_dict(torch.load(config.model_dir + end + '.pth'))
    else:
        target_net.load_state_dict(policy_net.state_dict())
    
    first_lr = config.lr
    optimizer = optim.SGD(
        policy_net.parameters(),
        lr=first_lr, momentum=0.9, weight_decay=5e-4, nesterov=False
    )

    _, newest_time = get_newest_model(
        model_dir=config.model_dir,
    )

    curr_time = time.gmtime()

    for epoch in range(config.total_epoch):
        dataset = GomokuDatasetEpisode(
            save_dir=config.data_dir,
            episodes=config.episodes,
        )
        
        dataloader = DataLoader(
            dataset,
            batch_size=config.batch_size,
            shuffle=True,
            num_workers=config.num_worker,
            pin_memory=True,
            drop_last=True,
        )

        cur_iter = 0
        total_loss = 0

        dataloader = fabric.setup_dataloaders(dataloader)

        for batch in dataloader:
            state = batch['state']
            reward = batch['reward']
            action = batch['action'].unsqueeze(0)
            next_state = batch['next_state']
            non_final_mask = batch['mask']

            outputs = policy_net(state).gather(1, action)


            non_final_next_states = next_state[non_final_mask]

            next_state_values = fabric.to_device(torch.zeros(config.batch_size))
            with torch.no_grad():
                next_state_values[non_final_mask] = target_net(non_final_next_states).max(1).values

            expected_reward = reward.gather(1, action) - config.gamma * next_state_values

            loss = criterion(outputs, expected_reward)

            total_loss += loss.item()
            if cur_iter % 50 == 0:
                print(f"iter : {cur_iter :08d} \t loss : {loss:08f}")

            cur_iter += 1

            optimizer.zero_grad()
            loss.backward()

            torch.nn.utils.clip_grad_value_(policy_net.parameters(), 100)
            optimizer.step()

        print(f"current epoch {epoch}")
        print(f'total_loss: {round(total_loss, 4)} ({round(total_loss/cur_iter, 4)})')
    
    save_format = '%y%m%d%H%M%S'
    filename = time.strftime(save_format, curr_time) + ".pth"
    filepath = os.path.join(config.model_dir, filename)
    
    print(f"saved to {filepath}")
    target_net_state_dict = target_net.state_dict()
    policy_net_state_dict = policy_net.state_dict()
    for key in policy_net_state_dict:
        target_net_state_dict[key] = policy_net_state_dict[key]*config.tau + target_net_state_dict[key]*(1-config.tau)
    target_net.load_state_dict(target_net_state_dict)
    torch.save(target_net.state_dict(), filepath)

def start_train(prev_len):
    while True:
        board_files = getFiles(
            dir = './data/', 
            start = "000000000000",
            end = "991231235959",
        )
        if len(board_files) > prev_len + 20:
            print(f"train started")
            return len(board_files)

if __name__ == '__main__':
    config = parse_args()

    fabric = Fabric(accelerator='cuda', devices=1, strategy="ddp",)
    fabric.launch()
    fabric.seed_everything(990104)
    prev_len = config.episodes
    for count in range(config.model_update_count):
        print(f"current model count {count}")

        prev_len = start_train(prev_len)
        if config.hard_update:
            train_hard(config)
        elif config.soft_update:
            train_soft(config)
