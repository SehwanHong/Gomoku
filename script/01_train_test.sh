#!/bin/bash -l

##SBATCH --nodelist=nv180

#SBATCH --time=10:00:00
#SBATCH -p 40g
#SBATCH --nodes=1            # This needs to match Trainer(num_nodes=...)
#SBATCH --ntasks-per-node=1  # This needs to match Trainer(devices=...)
#SBATCH --mem=16gb
#SBATCH --cpus-per-task=1
#SBATCH -o ./logs/%A.txt

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
    python train.py --run_name $RUN_NAME --data_dir ./data/ --model_dir ./model/;
    " 
    