# ABI-CALIOP Collocation with Features for Model Training

*Update: Currently, there are three separate sessions to complete ABI-CALIIOP collocation, which means submitting three jobs separately. We will update a new version with only one session.*

## Data Downloading

1. **Download [CALIPSO data](https://search.earthdata.nasa.gov/search/granules?p=C1556717898-LARC_ASDC&pg[0][v]=f&pg[0][gsk]=-start_date&q=cal_lid_l2_01kmclay&tl=1707754578.127!3!!&lat=-0.0703125&long=-0.0703125)**
   1. Product name: CALIPSO Lidar Level 2 1 km Cloud Layer, V4-20
   2. Time span: I downloaded 2017-11-01 ~ 2017-11-30 data
   3. Save path: /umbc/rs/nasa-access/data/calipso_data/CAL_LID_L2_01kmCLay/2017-01-01
   4. Download by bash file: follow the instructions on the earthdata download page
2. **Download [ABI data](https://www.goes-r.gov/spacesegment/abi.html)**
   1. Product name
      1. OR_ABI-L1b-RadF: [https://docs.opendata.aws/noaa-goes16/cics-readme.html](https://docs.opendata.aws/noaa-goes16/cics-readme.html)
      2.  
   2. Time span: I downloaded 2017-305 ~ 2017-335 data (the same time range with CALIPSO data)
   3. Save path: /umbc/rs/nasa-access/users/xingyan/abi_data/2017/
   4. Download by aws cli: 

`aws s3 cp s3://noaa-goes16/ABI-L1b-RadF/2017/305 /umbc/rs/nasa-access/users/xingyan/abi_data/2017/ --recursive`

## Generating CALIOP Index of Collocation

Run python file *generate_collocation_index.py* to generated index for CALIPSO-ABI collocation. 

## Extracting collocated ABI Data with the Index

Run code to extract CALIPSO-ABI collocation data with the generated index. On [taki cluster](https://hpcf.umbc.edu/system-description-taki/), a SLURM file is required to submit jobs. We provide the SLURM file, which can be submitted in terminal by running:

`sbatch generate_index.slurm`

Please edit following variable values in the slurm file: ABI_PATH, ABI_L2_PATH, INDEX_PATH, SAVE_PATH

## Combining Features from Index Files and Extracted ABI Data

Run python file *combine.py* to combine the features from the previous two sessions.
