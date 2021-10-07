# Description
This folder shows examples on how to use our software.

# Prerequisite: Instructions on Downloading Input VIIRS and CALIPSO Data
This section guides users to download the required VIIRS and CALIPSO data for the following example runs.

## Requirement of Input Data
Our collocation example requires the input 
          1. VIIRS/NPP Moderate Resolution Terrain-Corrected Geolocation 6-Min L1 Swath at 750m resolution. 
              (https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/VNP03MOD)
          2. CALIOP/CALIPSO Level-2 1km Cloud Layer Product.
              (https://asdc.larc.nasa.gov/data/CALIPSO/LID_L2_01kmCLay-Standard-V4-20/)

### Step 1: Create an account or sign in on [NASA Earthdata](https://urs.earthdata.nasa.gov/)

### Step 2: Request a token for using the wget command-line utility in your preferred terminal
In order to properly authenticate your transfer and download, please obtain an [app key](https://ladsweb.modaps.eosdis.nasa.gov/tools-and-services/data-download-scripts/#requesting) according to [these instructions](https://ladsweb.modaps.eosdis.nasa.gov/tools-and-services/data-download-scripts/#appkeys).

### Step 3: Modify the token in the wget command-line of the download_viirs.sh
