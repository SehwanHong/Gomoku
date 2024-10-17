#!/bin/bash -l

#SBATCH --nodelist=aten234 #aten228,aten230,aten232,aten234,aten236,aten238

#SBATCH --time=10:00:00
#SBATCH -p a10
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
    python server_main.py --data_dir ./data/ --model_dir ./model/ --store_game_play --search_limit 10 --time_search --iter 2 --self_play --train --update_model;
    " 
    
