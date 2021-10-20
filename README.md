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
