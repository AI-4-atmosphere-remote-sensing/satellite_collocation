#!/bin/bash
#SBATCH --partition=high_mem
#SBATCH --exclusive
#SBATCH --qos=medium+
#SBATCH --output=slurm-%x-%j-%u.out
#SBATCH --error=slurm-%x-%j-%u.out
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --account=pi_jianwu

#switch to satellite_collocation environment via conda
source ~/.bashrc
source ~/.bash_profile
conda activate satellite_collocation

#run the code
python3 collocation_dask_slurm.py
