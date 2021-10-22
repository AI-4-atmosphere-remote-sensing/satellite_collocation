# Description
This folder shows examples on how to use our software.

## Run Examples

### 1. Run CALIPSO-VIIRS Collocation Locally without Parallelization (collocate_abi_calipso_local_execution)

#### 1.1 Prerequisite: Instructions on Downloading Input VIIRS and CALIPSO Data
This section guides users to download the required VIIRS and CALIPSO data for the following example runs.

##### 1.1.1 Download CALIPSO Data:
Step 1: Create an account or sign in on [NASA Earthdata](https://urs.earthdata.nasa.gov/)

Step 2: Use [Python3 Code](https://forum.earthdata.nasa.gov/viewtopic.php?f=7&t=2330&sid=cbc21236b1005808dbe9dbacf066c027) to download single file or whole folders

Step 3: To run the example code, you need CALIPSO Level-2 01km Cloud (Aerosol) Layer Product. The latest version (4.20) is available at [CALIPSO Data](https://asdc.larc.nasa.gov/data/CALIPSO/LID_L2_01kmCLay-Standard-V4-20/)

##### 1.1.2 Download VIIRS Data
Step 1: Create an account or sign in on [NASA Earthdata](https://urs.earthdata.nasa.gov/)

Step 2: To run the example code, you need [VIIRS/NPP Moderate Resolution Terrain-Corrected Geolocation L1 6-Min Swath 750 m](https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/5200/VNP03MOD/)

Step 3: Use [scripts](https://ladsweb.modaps.eosdis.nasa.gov/tools-and-services/data-download-scripts/#python) to download VIIRS Data

#### 1.2 Modify the Example Code:

Step 1: Select appropriate the time and distance thresholds for collocation code:

maximum_distance = 5.0  #kilometer

maximum_interval = 15.0 #minute

Step 2: Tell code the spatial resolution of VIIRS (or other passive instrument):

viirs_resolution = 0.75 #kilometer

Step 3: Specify locations of CALIPSO and VIIRS data and where you want to save the output files:

clayer1km_path = '$CALIPSO_CLAYER_1KM_Path'

vnp03_path = '$VIIRS_VNP03_MOD_Path'

save_path = '$SAVE_Path'

#### 1.3 Run the Example Code:

Simply type "python main.py"

#### 1.4 Output:

The collocation file will be named with "CAL_" + $CALIPSO_Timeflag + "_VNP_" + $VIIRS_Timeflag + "_Index.h5" and saved in HDF5 format in the $SAVE_Path folder.

There are five datasets in each saved file:

1) CALIPSO_Track_Index: 1-D integer array of collocated CALIPSO Profile ID. Valid Range[>= 0], no collocation if less than 0.


2) VIIRS_CrossTrack_Index and VIIRS_AlongTrack_Index: 2 1-D integer arrays of collocated VIIRS Across Track and Along Track IDs. Valid Range[>= 0], no collocation if less than 0.

3) CALIPSO_VIIRS_Distance: 1-D array of the spatial distances (in kilometer) between collocated CALIPSO and VIIRS pixels. Valid Range [0.0 ~ maximum_distance], no collocation if less than 0.

4) CALIPSO_VIIRS_Interval: 1-D array of the observation time differences (in minutes) between collocated CALIPSO and VIIRS pixels. Valid Range [-maximum_interval ~ maximum_interval].

### 2. Run CALIPSO-VIIRS Collocation in Parallel via Dask (collocate_viirs_calipso_dask_cluster)
To run this example, you need to get the first example running first to know how to get data and run code locally.

Because utilizing [Dask](https://dask.org/) requires additional Python packages, you need to copy the content of requirements_dask.txt file to the top folder and install the packages via Python setup.py
```
>> cp examples/collocate_viirs_calipso_dask_cluster/requirements_dask.txt ./requirements.txt
>> python setup.py install
```

collocation_dask_local.py shows how to utilize Dask to run in parallel via multiple threads. You can run it directly via Python
```
>> python3 collocation_dask_local.py
```

collocation_dask_slurm.py shows how to utilize Dask to run in parallel via separate SLURM jobs if you have a SLURM based distributed cluster. You can submit it as a job via the slurm file or run it directly via Python. collocation_dask_slurm.py first requests additional compute nodes via its SLURMCluster() and scale() functions, then calls collocate_viirs_calipso function in parallel on the nodes.
```
>> sbatch collocation_dask.slurm
```
