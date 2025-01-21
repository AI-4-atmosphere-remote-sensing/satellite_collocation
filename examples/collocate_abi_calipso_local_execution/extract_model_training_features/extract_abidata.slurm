#!/bin/bash

#SBATCH --job-name=abi_calipso_collocate        # Job name
#SBATCH --output=slurm_1001_325.out             # Output file name
#SBATCH --error=slurm_1001_325.err              # Error file name
#SBATCH --partition=high_mem                    # Partition
#SBATCH --qos=long+                             # Queue
#SBATCH --time=3-00:00:00                       # Time limit 
#SBATCH --nodes=1                               # Number of nodes
#SBATCH --ntasks-per-node=1                     # MPI processes per node
#SBATCH --nodelist=bdnode008 

ABI_PATH="/umbc/rs/nasa-access/users/xingyan/abi_data/2017_l1/" 
ABI_L2_PATH="/umbc/rs/nasa-access/users/xingyan/abi_data/2017_l2/"
INDEX_PATH="/umbc/rs/nasa-access/users/xingyan/satellite_collocation/satellite_collocation_github/examples/collocate_abi_calipso_local_execution/generate_2017/collocated_index/"
SAVE_PATH="/umbc/rs/nasa-access/users/xingyan/satellite_collocation/satellite_collocation_github/examples/collocate_abi_calipso_local_execution/generate_2017/ABI_collocated_data/"

echo "Activating conda environment"
source /umbc/rs/nasa-access/users/xingyan/software/miniconda3/etc/profile.d/conda.sh
conda activate /umbc/rs/nasa-access/users/xingyan/software/miniconda3/envs/satellite_collocation
python extract_taki.py -ap $ABI_PATH -apl2 $ABI_L2_PATH -ip $INDEX_PATH -sp $SAVE_PATH