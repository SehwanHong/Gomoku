import os
from glob import glob

def isCorrectTime(time_str):
    assert len(time_str) == 12
    YY = time_str[:2]
    assert int(YY) >= 0 and int(YY) <= 99
    MM = time_str[2:4]
    assert int(MM) >= 1 and int(MM) <= 12
    DD = time_str[4:6]
    assert int(DD) >= 1 and int(DD) <= 31
    HH = time_str[6:8]
    assert int(HH) >= 0 and int(HH) <= 23
    mm = time_str[8:10]
    assert int(mm) >= 0 and int(mm) <= 59
    SS = time_str[10:12]
    assert int(SS) >= 0 and int(SS) <= 59

def get_newest_model(model_dir="./model/"):
    model_list = glob(model_dir + "**.pth", recursive=True)
    newest = '000000000000'
    second_newest = '000000000000'
    for model in model_list:
        filename = os.path.basename(model)
        time_created = filename[:-4]
        isCorrectTime(time_created)
        if int(time_created) >= int(newest):
            second_newest = newest
            newest = time_created
    return second_newest, newest