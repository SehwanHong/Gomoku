from board_dataset import GomokuDataset
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
    return parser.parse_args()

if __name__ == '__main__':
    config = parse_args()

    # wandb.login(key='local-73177de041f41c769eb8cbdccb982a9a5406fab7', host='http://wandb.artfacestudio.com')
    # wandb.init(
    #     project="gomoku",
    #     name=config.run_name,
    #     config=config,
    # )

    fabric = Fabric(accelerator='cuda', devices=1, strategy="ddp",)
    fabric.launch()
    fabric.seed_everything(990104)
    
    start, end = get_newest_model(
        model_dir=config.model_dir,
    )

    model = DQN()

    pytorch_total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    # wandb.config.update({"num_param": pytorch_total_params})

    print(f"pytorch total_params : {pytorch_total_params}")

    ''' Define Else '''
    # criterion = nn.CrossEntropyLoss()
    # criterion = nn.BCEWithLogitsLoss()
    # criterion = LabelSmoothSoftmaxCEV1(lb_smooth=0.1).cuda()
    criterion = nn.MSELoss()

    if end != '000000000000':
        model.load_state_dict(torch.load(config.model_dir + end + '.pth'))
    
    _, newest_time = get_newest_model(
        model_dir=config.model_dir,
    )

    first_lr = config.lr
    optimizer = optim.SGD(
        model.parameters(),
        lr=first_lr, momentum=0.9, weight_decay=5e-4, nesterov=False
    )

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
        
        for board, qvalue in dataloader:
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
    
    curr_time = time.time()
    save_format = '%y%m%d%H%M%S'
    filename = time.strftime(save_format, curr_time) + ".pth"
    filepath = os.path.join(config.model_dir, filename)
    
    torch.save(model.state_dict, filepath)