#!/bin/bash -l

##SBATCH --nodelist=nv180

#SBATCH --time=10:00:00
#SBATCH -p 80g
#SBATCH --nodes=1            # This needs to match Trainer(num_nodes=...)
#SBATCH --ntasks-per-node=1  # This needs to match Trainer(devices=...)
#SBATCH --mem=32gb
#SBATCH --cpus-per-task=8
#SBATCH --gpus=1
#SBATCH -o ./logs/train_%A.txt

export RUN_NAME="run_$SLURM_JOB_ID"

# run script from above
srun --container-image /purestorage/project/shhong/enroot_images/torch2.sqsh \
    --container-mounts /purestorage:/purestorage,/purestorage/project/shhong/tmp:/home/$USER/.cache \
    --no-container-mount-home \
    --container-writable \
    --container-workdir /purestorage/project/shhong/Gomoku/ \
    bash -c "
    pip install lightning;
    pip install wandb;
    python train.py --run_name $RUN_NAME --batch_size 32 --lr 1e-3 --num_worker 8 --total_epoch 100 --model_update_count 1;
    "