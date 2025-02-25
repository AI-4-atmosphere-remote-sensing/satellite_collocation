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

#### 1.2 Run the Example Code:

Check usage:
python main.py --help

Required Command Line Arguments:

'-md',  '--maximum_distance', define the maximum distance of collocated pixels in kilometer, default value is 5 km

'-mt',  '--maximum_timeinterval', define the maximum time interval of collocated pixels in minutes, default value is 15 minutes

'-sr',  '--swath_resolution', define the pixel resolution of swath instrument in kilometer, default value is 0.75 km

'-tp',  '--track_instrument_path', define the path of CALIPSO L2 files

'-sgp', '--swath_geo_path', define the path of VIIRS VNP03 files

'-sdp', '--swath_data_path', define the path of VIIRS VNP02 files

'-sp',  '--save_path', define the path of output files, default value './' current path

Example:

python main.py -md 15 -mt 50 -sr 1 -tp ../../resources/data/sample_input_data/CALIPSO_LID_L2_01kmCLay/ -sgp ../../resources/data/sample_input_data/VIIRS_Coordinates_VNP03MOD/ -sdp ../../resources/data/sample_input_data/VIIRS_Attributes_VNP02MOD/ -sp ../../resources/data/sample_output_data/


#### 1.3 Output:

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

### 3. Run CALIPSO-VIIRS Collocation in Parallel via Dask on AWS (collocate_viirs_calipso_dask_aws)
This example explains how to run the collocation code on AWS. More detailed steps can be found at [collocate_viirs_calipso_dask_aws](collocate_viirs_calipso_dask_aws) directory.

#### 3.1 Prerequisites:
1. The user has AWS account and credentials to run Lambda functions.
2. The user has access to an AWS EC2 instance where the collocation code can execute.

#### 3.2 Create the Lambda Function:
Step 1: Follow the steps in ___Step2- Lambda Function___ from [this link](https://github.com/AI-4-atmosphere-remote-sensing/satellite_collocation/tree/main/examples/collocate_viirs_calipso_dask_aws#step2--lambda-function:~:text=a%20lambda%20function!-,Step2%2D%20Lambda%20Function,-%2D%2DCreate%20a%20Lambda) to create a lamda function.

Step 2: Copy the [example code like this](https://github.com/AI-4-atmosphere-remote-sensing/satellite_collocation/blob/main/examples/collocate_viirs_calipso_dask_aws/service_1_trigger_lambda_to_execute.py) and paste in the **_Lambda Console_** and Save it.

#### 3.3 Create the API:
Step 1: Follow the steps in ___Step3- AWS API Gateway___ from [this link](https://github.com/AI-4-atmosphere-remote-sensing/satellite_collocation/tree/main/examples/collocate_viirs_calipso_dask_aws#:~:text=Step3%2D%20AWS%20API%20Gateway) to create an API.

Step 2: Click the _**API Endpoint link**_ to execute the model in the EC2

Note: To copy the results from EC2 to S3 bucket repeat the process _3.2_ to create Lambda Function using [this sample code](https://github.com/AI-4-atmosphere-remote-sensing/satellite_collocation/blob/main/examples/collocate_viirs_calipso_dask_aws/service_2_trigger_lambda_to_copy_files_to_S3.py) and _3.3_ to create an API.

### 4. Run CALIPSO-ABI Collocation in Parallel via Dask on AWS (collocate_abi_calipso_dask_aws)
This example explains how to run the collocation code on AWS by using the [RPAC toolkit](https://github.com/big-data-lab-umbc/Reproducible_and_portable_app_in_cloud).

#### 4.1 Prerequisites:
- The user has AWS account and credentials to run Lambda functions.
- The user has access to an AWS EC2 instance where the collocation code can execute.
- The user has the [RPAC toolkit](https://github.com/big-data-lab-umbc/Reproducible_and_portable_app_in_cloud) and its prerequisites in their local machine.

#### 4.2 Run the Example Code:
Step 1: Use the example configuration files and update the default configurations resource.ini, application.ini, personal.ini in ConfigTemplate folder.
```
>> cp -rf Reproducible_and_portable_app_in_cloud/examples/SatelliteCollocationViaDask/* Reproducible_and_portable_app_in_cloud/ConfigTemplate/
```
Step 2: Run python3 main.py to execute the big data analytics.
```
>> python3 main.py
```
Step 3: Check the application status from [link](https://us-west-2.console.aws.amazon.com/cloudformation/home?region=us-west-2). Please see other detailed information and debugging from [link](https://github.com/big-data-lab-umbc/Reproducible_and_portable_app_in_cloud/blob/main/README.md).
