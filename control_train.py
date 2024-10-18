import subprocess
import tempfile
import os
import time
from utils import get_newest_model, getFiles

def create_self_play(node_name, search_limit):
    filename = create_self_play_script(node_name, search_limit)
    job_id = submit_slurm_job(filename)
    if job_id is None:
        print('Error: sbatch job error')
    
    print(f'SelfPlay [{job_id}] made in {node_name}')
    os.unlink(filename)

def check_resource_available():
    cmd = "pestat -M 40000 -d | grep -e hpe -e nv -e aten | grep -v aten228"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    node_list = []

    result = result.stdout.strip().split('\n')
    for stat_info in result:
        info_list = stat_info.split()
        node_name = info_list[0]
        cpu_in_use = info_list[3]
        total_cpu = info_list[4]
        
        cpu_available = int(total_cpu) - int(cpu_in_use)
        
        for i in range(cpu_available // 5):
            if i > 3:
                break
            
            node_list.append(node_name)
    return node_list

def fill_available_node(search_limit):
    available_node_list = check_resource_available()

    for node_name in available_node_list:
        create_self_play(node_name, search_limit)

def create_self_play_script(node_name: str, search_limit):

    script_content = f"""#!/bin/bash -l

#SBATCH --nodelist={node_name}

#SBATCH --time=10:00:00
#SBATCH --nodes=1            # This needs to match Trainer(num_nodes=...)
#SBATCH --ntasks-per-node=1  # This needs to match Trainer(devices=...)
#SBATCH --mem=8gb
#SBATCH --cpus-per-task=4
#SBATCH -o ./logs/selfplay_%A.txt

# run script from above
srun --container-image /purestorage/project/shhong/enroot_images/torch2.sqsh \
    --container-mounts /purestorage:/purestorage,/purestorage/project/shhong/tmp:/home/$USER/.cache \
    --no-container-mount-home \
    --container-writable \
    --container-workdir /purestorage/project/shhong/Gomoku/ \
    bash -c "
    pip install lightning;
    python server_main.py --data_dir ./data/ --model_dir ./model_save/ --store_game_play --search_limit {search_limit} --time_search --iter 1 --self_play --train --update_model;
    "

"""
    # 임시 파일 생성
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False)

    temp_file.write(script_content)
    temp_filename = temp_file.name

    return temp_filename

def submit_slurm_job(script_path):
    cmd = f"sbatch {script_path}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error submitting job: {result.stderr}")
        return None
    
    # Job ID 추출
    job_id = result.stdout.strip().split()[-1]
    return job_id

def run_train():
    filename = "script/01_train_test.sh"
    job_id = submit_slurm_job(filename) 
    if job_id is None:
        print('Error: sbatch job error')
    
    print(f'train [{job_id}] created')
    os.unlink(filename)

def run_continuous():
    while True:
        model_dir = "./model_save/"
        _, newest_time = get_newest_model(model_dir=model_dir)

        board_files = getFiles(
            dir = model_dir, 
            start = newest_time,
            end = "991231235959",
        )

        search_limit = 1

        if len(board_files) > 200:
            while selfplay_not_running() != 0:
                time.sleep(3)
            run_train()
            search_limit += 1
        else:
            while train_not_running() != 0:
                time.sleep(3)
            fill_available_node(search_limit=search_limit)

def selfplay_not_running():
    cmd = "squeue | grep shhong | grep tmp | wc -l"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    running_jobs = int(result.stdout.strip())
    return running_jobs


def train_not_running():
    cmd = "squeue | grep shhong | grep 01_tr | wc -l"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    running_jobs = int(result.stdout.strip())
    return running_jobs


if __name__ == '__main__':
    run_continuous()
    # fill_available_node(search_limit=1)
