import sys
import os
import numpy as np
import satellite_collocation.general_collocation as gc
import satellite_collocation.instrument_reader as ir
import satellite_collocation.satellite_geo as sg

import glob
import datetime
from datetimerange import DateTimeRange
import h5py
import shutil

import warnings
warnings.filterwarnings("ignore")

import argparse
import s3fs

from dask.distributed import Client
from dask.distributed import as_completed



accessKeyId="AKIASHT77BI5XMAXXXXXX"
secretAccessKey="4iHrOCJguV1iUf9XlleB7e7AgCU0xYXXXXXX"
index_destination = "../../taki_data/index-finished/"

def refresh_s3():

    creds = store_aws_keys()
    s3 = s3fs.S3FileSystem(
        key=creds['AccessKeyId'],
        secret=creds['SecretAccessKey'],
        client_kwargs={'region_name':'us-west-2'},
    )
    return s3

def store_aws_keys():    

    creds ={}
    creds['AccessKeyId'] = accessKeyId
    creds['SecretAccessKey'] = secretAccessKey
    
    return creds

def collocation_abi(index_file,save_path,n_abi_times):

    print(index_file)

    print("Working for index file: ",index_file)
    if index_file == "":
        return "Unvaild index file.\n\n"

    index_name = os.path.basename(index_file)
    cal_timeflag = index_name[8:29]

    fid = h5py.File(index_file,'r')

    calipso_inds = fid['CALIPSO_Index'][:]
    calipso_utcs = np.squeeze(fid['CALIPSO_UTC'][:])

    abi_ind_meridional_hkm = fid['ABI_Index_Meridional_hkm'][:]
    abi_ind_meridional_1km = fid['ABI_Index_Meridional_1km'][:]
    abi_ind_meridional_2km = fid['ABI_Index_Meridional_2km'][:]

    abi_ind_zonal_hkm = fid['ABI_Index_Zonal_hkm'][:]
    abi_ind_zonal_1km = fid['ABI_Index_Zonal_1km'][:]
    abi_ind_zonal_2km = fid['ABI_Index_Zonal_2km'][:]

    distance_hkm = fid['CALIPSO_ABI_Distance_hkm'][:]
    distance_1km = fid['CALIPSO_ABI_Distance_1km'][:]
    distance_2km = fid['CALIPSO_ABI_Distance_2km'][:]
    fid.close()

    #check calipso utc times 
    n_profile = len(calipso_utcs) 
    #to date
    calipso_dates = np.squeeze(np.asarray(calipso_utcs+20000000.,dtype=np.int32))
    #to time
    calipso_times = np.squeeze((calipso_utcs - calipso_dates + 20000000.) * 24. * 3600.)

    profile_dts = []
    for i_profile in range(n_profile):
        profile_dts.append(datetime.datetime.strptime(str(calipso_dates[i_profile]), '%Y%m%d') + datetime.timedelta(seconds=calipso_times[i_profile]))

    #define save variables
    select_abi_stimeflag = np.zeros(n_profile, dtype=np.int64)
    #save data from the following channels
    #save_channel = [1,2,3,11,12,13,14,15,16]
    save_channel = [1]
    n_channel = 16
    abi_data = np.full([n_profile,n_channel],fill_value=-9999.99)

    for i_abi_time in range(n_abi_times):
        abi_range = abi_ranges[i_abi_time]    
        abi_stimeflag = abi_stimeflags[i_abi_time]
        #print (abi_range, profile_dts[0])
        y = np.asarray([(x in abi_range) for x in profile_dts])
        index = np.where(y)[0]
        if (len(index)>0):
            select_abi_stimeflag[index] = int(abi_stimeflag)
        else:
            continue

        #load ABI data 
        print ("Load ABI Data for timeflag ", abi_stimeflag)
        
        #ABI files at this timeframe
        for channel in save_channel:
            current_abi_files = sorted(glob.glob(abi_file_path+'OR_ABI-L1b-RadF-M?C' + str(channel).zfill(2) + '*_s'+abi_stimeflag+'*.nc'))
            if (len(current_abi_files)!=1):
                continue
            current_abi_file = current_abi_files[0]
            abi_name = os.path.basename(current_abi_file)
            resolution = ir.get_abi_l1b_resolution(channel_number=channel)
            print ("Load Channel:", channel, ' (' + str(resolution) + 'km)')

            if ( resolution == 0.5 ):
                abi_ind_meridional = abi_ind_meridional_hkm[index]
                abi_ind_zonal = abi_ind_zonal_hkm[index]
            elif ( resolution == 1 ):
                abi_ind_meridional = abi_ind_meridional_1km[index]
                abi_ind_zonal = abi_ind_zonal_1km[index]
            elif ( resolution == 2 ):
                abi_ind_meridional = abi_ind_meridional_2km[index]
                abi_ind_zonal = abi_ind_zonal_2km[index]
            else:
                continue

            temp_data = ir.load_abi_l1b(abi_file=current_abi_file,
                                    index_meridional=abi_ind_meridional,
                                    index_zonal=abi_ind_zonal,channel_number=channel)

            abi_data[index,channel-1] = temp_data

    #save to files
    #check if there's valid data
    n_valid = np.where(select_abi_stimeflag>0)
    if ( len(n_valid[0]) <= 0 ):
        return "No file in this time flag.\n\n"
    save_name = 'ABI_G16_Data_CAL_' + cal_timeflag + '.h5'
    sid = h5py.File(save_path+save_name,'w')
    sid.create_dataset('ABI_Obs',data=abi_data)
    sid.create_dataset('ABI_Timeflag',data=select_abi_stimeflag)
    sid.close()

    print("Save ABI output file: ",save_path+save_name)

    shutil.move(index_file, index_destination+index_name)

    return "Done extract.\n\n"



if __name__ =='__main__':

    parser = argparse.ArgumentParser(description='This code is an example of extracting ABI data based on existing index files')
    parser.add_argument('-ap','--abi_path', help='Define the path of ABI files', required=True)
    parser.add_argument('-ip','--index_path', help='Define the path of Index files', required=True)
    parser.add_argument('-sp','--save_path', help='Define the path of output files', required=True)
    parser.add_argument('-nw','--num_workers', help='Define the number of workers for Dask parallel computing', default="1")
    parser.add_argument('-ds','--dask_scheduler', help='Define the address of the Dask scheduler', required=True)

    args = vars(parser.parse_args())
    abi_file_path = args['abi_path'].strip()
    index_path = args['index_path'].strip()
    save_path = args['save_path'].strip()
    num_workers = args['num_workers'].strip()
    scheduler_address = args['dask_scheduler'].strip()

    #check abi files
    abi_files = sorted(glob.glob(abi_file_path+'OR_ABI-L1b-RadF-M?C*.nc'))
    abi_ranges = []
    abi_stimeflags = []

    for abi_file in abi_files:
        abi_name = os.path.basename(abi_file)
        abi_start_pos = abi_name.find("_s")
        abi_end_pos = abi_name.find("_e")
        abi_starttimeflag = abi_name[abi_start_pos+2:abi_start_pos+15]
        abi_endtimeflag = abi_name[abi_end_pos+2:abi_end_pos+15]
        abi_sdt = datetime.datetime.strptime(abi_starttimeflag, "%Y%j%H%M%S")
        abi_edt = datetime.datetime.strptime(abi_endtimeflag, "%Y%j%H%M%S")
        #abi_mdt = abi_sdt + (abi_edt-abi_sdt)/2.
        #abi_mdts.append(abi_mdt)
        abi_range = DateTimeRange(abi_sdt,abi_edt)
        abi_ranges.append(abi_range)
        abi_stimeflags.append(abi_starttimeflag)
    n_abi_times = len(abi_ranges)

    index_files = sorted(glob.glob(index_path+'Ind_CAL_*.h5'))

    kwargv = {"save_path": save_path, "n_abi_times": n_abi_times}
    #collocation_abi(cal_files,index_save_path,disk_lats,disk_lons,save_path)

    #create a client at the same node
    #client = Client(threads_per_worker=2, n_workers=int(num_workers)) #4,6,8

    client = Client(scheduler_address)

    #collocate_viirs_calipso() will be executed in parallel via multiple threads
    tt = client.map(collocation_abi, index_files, **kwargv)

    # aggregate the result
    for future, result in as_completed(tt, with_results= True):
        print(result)
    
    client.close()