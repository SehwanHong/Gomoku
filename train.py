from board_dataset import GomokuDataset
import torch
import torch.nn
import lightning
from lightning import Fabric
import argparse
import wandb
from glob import glob
import os
from utils import isCorrectTime, get_newest_model

def parse_args():
    parser = argparse.ArgumentParser(description="Train SVM argparser")
    parser.add_argument('--run_name', default="run")
    parser.add_argument('--data_dir', default='./data/', help="data directory")
    parser.add_argument('--model_dir', default='./model/', help="model directory")

    parser.add_argument('--batch_size', default=8, type=int, help="batch size")
    parser.add_argument('--lr', default=1e-3, type=float, help="initial learning rate")
    parser.add_argument('--warmup_epoch', default=2, type=int, help="warmup epoch")
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

    # fabric = Fabric(accelerator='cuda', devices=1, strategy="ddp",)
    # fabric.launch()
    # fabric.seed_everything(990104)

    start, end = get_newest_model(
        model_dir=config.model_dir,
    )

    dataset = GomokuDataset(
        save_dir=config.data_dir,
        start = start,
        end = end,
    )