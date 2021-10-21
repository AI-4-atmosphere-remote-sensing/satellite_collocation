# Description
This folder shows examples on how to use our software.

## Run Examples

### 1. Run CALIPSO-VIIRS Collocation

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

