#!/bin/bash
#SBATCH --partition=high_mem
#SBATCH --exclusive
#SBATCH --qos=medium+
#SBATCH --output=slurm-%x-%j-%u.out
#SBATCH --error=slurm-%x-%j-%u.out
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --account=pi_jianwu

# Example 1: Choose the time from 2008/01/01 to 2008/01/01 (Daily) with the region [-90,90,-180,180] with grid size [1,1] with sampling rate 1
#                        Calculate Minimum, Maximum, Mean, Pixel Counts, Standard Deviation, Histogram and Joint Histogram.
#                        Variables (5km resolution) in input_file_1km.csv & input_Jhist_1km.csv:
#              Cloud_Top_Pressure        
#              Cloud_Top_Temperature     
#              Cloud_Effective_Emissivity
#              cloud_fraction_CM         
#              Cloud_Top_Height          
python3 collocation_dask.py
