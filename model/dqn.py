import torch
import torch.nn as nn
import lightning

class BasicBlock(nn.Module):
    def __init__(self, in_c, out_c, stride=1):
        super(BasicBlock, self).__init__()
        self.bn1 = nn.BatchNorm2d(in_c)
        self.conv1 = nn.Conv2d(in_c, out_c, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_c)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(out_c, out_c, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn_last = nn.BatchNorm2d(out_c)
        self.bn_last.final = True
        
        if stride > 1 or in_c != out_c:
            self.downsample = nn.Sequential(
                nn.Conv2d(in_c, out_c, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_c)
            )
        else:
            self.downsample = nn.Identity()
        
    def forward(self, x):
        identity = x
        
        x = self.bn1(x)
        x = self.conv1(x)
        x = self.bn2(x)
        x = self.relu(x)

        x = self.conv2(x)
        x = self.bn_last(x)

        identity = self.downsample(identity)
        x += identity
        
        return x

class BottleNeckBlock(nn.Module):
    def __init__(self, in_c, out_c, stride=1, b=1, attention=False, g=8):
        super(BottleNeckBlock, self).__init__()

        bottle_c = out_c // b
        cardinality = bottle_c // g if bottle_c // g != 0 else 1
        if g == -1:
            cardinality = 1
        self.relu = nn.ReLU(inplace=True)

        # self.bn0 = nn.BatchNorm2d(in_c)
        self.conv1 = nn.Conv2d(in_c, bottle_c, kernel_size=1, stride=1, bias=False)
        self.bn1 = nn.BatchNorm2d(bottle_c)
        # self.relu1 = Swish()
        self.conv2 = nn.Conv2d(bottle_c, bottle_c, kernel_size=3, stride=stride, padding=1, bias=False, groups=cardinality)
        self.bn2 = nn.BatchNorm2d(bottle_c)
        # self.relu2 = Swish()
        self.conv3 = nn.Conv2d(bottle_c, out_c, kernel_size=1, stride=1, bias=False)
        self.bn_last = nn.BatchNorm2d(out_c)
        self.bn_last.final = True

        if stride > 1:
            self.downsample = nn.Sequential(
                nn.AvgPool2d(2, stride, ceil_mode=True),
                nn.Conv2d(in_c, out_c, kernel_size=1, stride=1, bias=False),
                nn.BatchNorm2d(out_c)
            )
        elif in_c != out_c:
            self.downsample = nn.Sequential(
                nn.Conv2d(in_c, out_c, kernel_size=1, stride=1, bias=False),
                nn.BatchNorm2d(out_c)
            )
        else:
            self.downsample = nn.Identity()

    def forward(self, x):
        identity = x

        # x = self.bn0(x)
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.conv2(x)
        x = self.bn2(x)
        x = self.relu(x)

        x = self.conv3(x) 
        x = self.bn_last(x)

        identity = self.downsample(identity)
        x += identity

        x = self.relu(x)

        return x

class Value(nn.Module):
    def __init__(self, in_c, out_c, stride=1, downsample=None, attention=False, g=8):
        super(Value, self).__init__()
        self.bn1 = nn.BatchNorm2d(in_c)
        self.conv1 = nn.Conv2d(in_c, 1, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(1)
        self.relu1 = nn.ReLU(inplace=True)
        self.flatten = nn.Flatten()
        self.linear1 = nn.Linear(out_c, out_c*2)
        self.relu2 = nn.ReLU()
        self.linear2 = nn.Linear(out_c*2, out_c)
        
    def forward(self, x):
        # use loss of mse
        x = self.bn1(x)
        x = self.conv1(x)
        x = self.bn2(x)
        x = self.relu1(x)

        x = self.flatten(x)
        x = self.linear1(x)
        x = self.relu2(x)
        x = self.linear2(x)

        return x

class DQN(nn.Module):
    def __init__(self, board_size = 15*15) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(7, 16, kernel_size=3, stride=1,  padding=1)
        self.bb1 = BasicBlock(16, 32)
        self.bb2 = BasicBlock(32, 64)
        self.bb3 = BasicBlock(64, 64)
        self.value = Value(64, board_size)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bb1(x)
        x = self.bb2(x)
        x = self.bb3(x)
        x = self.value(x)
        return x

