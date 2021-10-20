# Description
This repository provide a toolkit that collocates data from two or more satellites.


### Installation
#### Conda environment setup
```
conda create -n satellite_collocation -c conda-forge python=3.7 libnetcdf netCDF4 h5py

>> git clone https://github.com/AI-4-atmosphere-remote-sensing/satellite_collocation.git
>> cd satellite_collocation
>> python setup.py install
```
### Run Examples
#### Run CALIPSO-VIIRS Collocation
##### Download CALIPSO Data
Step 1: Create an account or sign in on [NASA Earthdata](https://urs.earthdata.nasa.gov/)

Step 2: Use [Python3 Code](https://forum.earthdata.nasa.gov/viewtopic.php?f=7&t=2330&sid=cbc21236b1005808dbe9dbacf066c027) to download single file or whole folders

Step 3: To run the example code, you need CALIPSO Level-2 01km Cloud (Aerosol) Layer Product. The latest version (4.20) is available at [CALIPSO Data](https://asdc.larc.nasa.gov/data/CALIPSO/LID_L2_01kmCLay-Standard-V4-20/)
