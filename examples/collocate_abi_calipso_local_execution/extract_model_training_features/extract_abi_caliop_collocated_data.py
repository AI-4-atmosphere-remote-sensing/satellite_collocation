import sys
sys.path.insert(1,'../../satellite_collocation/')
import os
import numpy as np
import general_collocation as gc
import instrument_reader as ir
import satellite_geo as sg

import glob
import datetime
from datetimerange import DateTimeRange
import h5py

from netCDF4 import Dataset

import warnings
warnings.filterwarnings("ignore")

import argparse
import string

abi_file_path = '/Volumes/MyPassport/abi_l1_201711/'
abi_file_l2_path = '/Volumes/MyPassport/abi_l2_201711/'
index_path = '/Volumes/MyPassport/2017_index/index_11_part/'
save_path = '/Users/xingyanli/Lab/ACCESS/satellite_collocation/examples/collocate_abi_calipso_local_execution/extracted_data/'

abi_files = sorted(glob.glob(abi_file_path+'/*/'+'/*/'+'OR_ABI-L1b-RadF-M?C01*.nc'))
abi_ranges = []
abi_stimeflags = []


# Functions for calculating solar and sensor angles
def Solar_Calculate(xlon, xlat, jday, tu):
    pi = 3.14159265
    dtor = pi / 180.0                         # change degree to radians
    
    tsm = tu + xlon/15.0                      # mean solar time
    xlo = xlon*dtor
    xla = xlat*dtor
    xj = jday
    
    a1 = (1.00554*xj - 6.28306)  * dtor
    a2 = (1.93946*xj + 23.35089) * dtor
    et = -7.67825*np.sin(a1) - 10.09176*np.sin(a2)             #time equation
    
    tsv = tsm + et/60.0 
    tsv = tsv - 12.0                                    # true solar time
    
    ah = tsv*15.0*dtor                                 # hour angle
    
    a3 = (0.9683*xj - 78.00878) * dtor
    delta = 23.4856*np.sin(a3)* dtor                    # solar declination (in radian)

    cos_delta = np.cos(delta)
    sin_delta = np.sin(delta)
    cos_ah = np.cos(ah)
    sin_xla = np.sin(xla)
    cos_xla = np.cos(xla)
    
    
    amuzero = sin_xla*sin_delta + cos_xla*cos_delta*cos_ah
    elev = np.arcsin(amuzero)
    cos_elev = np.cos(elev)
    az = cos_delta*np.sin(ah)/cos_elev
    caz = (-cos_xla*sin_delta + sin_xla*cos_delta*cos_ah) / cos_elev
       
    if (az >= 1.0):
        azim = np.arcsin(1.0)
    elif (az <= -1.0):
        azim = np.arcsin(-1.0)
    else:
        azim = np.arcsin(az)
 
    if (caz <= 0.0):
        azim = pi - azim
               
    if ((caz > 0.0) & (az <= 0.0)):
        azim = 2 * pi + azim
        
    azim = azim + pi
    pi2 = 2 * pi
    
    if (azim > pi2):
        azim = azim - pi2
   
    #conversion in degrees
    elev = elev / dtor
    asol = 90.0 - elev                                 # solar zenith angle in degrees
    
    print('SZA is:', asol)
    # print('------------------------------------------------')
    
    phis1 = azim / dtor - 180.0                         # solar azimuth angle in degrees
    phis2 = phis1 + 360
    
    # print('SAA is:', phis1)
    # print('SAA is:', phis2)
    # print('------------------------------------------------')
    phis = phis2 - 180
    print('SAA is (for libradtran SSA is from south):', phis)

    return asol, phis1, phis

def Sensor_Calculate(xlon, xlat):
    pi = 3.14159265
    dtor = pi / 180.0                         # change degree to radians
    
    satlon = -137.0
    satlat = 0.0
    
    lon = (xlon - satlon) * dtor   # in radians
#     print('Lon is:',lon)
    lat = (xlat - satlat) * dtor   # in radians
#     print('Lat is:',lat)

    beta = np.arccos(np.cos(lat) * np.cos(lon))
    sin_beta = np.sin(beta)

    # zenith angle    
    x = 42164.0* sin_beta/np.sqrt(1.808e09 - 5.3725e08*np.cos(beta))
    zenith = np.arcsin(x)
    zenith = zenith/dtor
    print('VZA is:',zenith)

    # azimuth angle
    azimuth = np.sin(lon) / sin_beta
    azimuth = np.arcsin(azimuth)
    azimuth = azimuth / dtor
    if (lat < 0.0):
        azimuth = 180.0 - azimuth
    if (azimuth < 0.0):
        azimuth = azimuth + 360.0
    print('VAA is:',azimuth)
    
    return zenith, azimuth


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
    print(abi_file)
n_abi_times = len(abi_ranges)

index_files = sorted(glob.glob(index_path+'Ind_CAL_*.h5'))

for index_file in index_files:
    print (index_file)
    #load index file

    index_name = os.path.basename(index_file)
    cal_timeflag = index_name[8:29]

    fid = h5py.File(index_file,'r')

    calipso_inds = fid['CALIPSO_Index'][:]
    # print(calipso_inds)
    calipso_utcs = np.squeeze(fid['CALIPSO_UTC'][:])
    # print(calipso_utcs)

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
    save_channel = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
    # save_channel = [1]
    n_channel = 16
    abi_data = np.full([n_profile,n_channel],fill_value=-9999.99)
    abi_cloud = np.full([n_profile],fill_value=-9999.99)

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
            current_abi_files = sorted(glob.glob(abi_file_path+'/*/'+'/*/'+'OR_ABI-L1b-RadF-M?C' + str(channel).zfill(2) + '*_s'+abi_stimeflag+'*.nc'))
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
        
        # Load ABI L2 file at this timeframe OR_ABI-L2-ACTPF-M3_G16_s20173050000407_e20173050011174_c20173050011455
        current_abi_l2_files = sorted(glob.glob(abi_file_l2_path+'/*/'+'/*/'+'OR_ABI-L2-ACTPF-M' + '*_s'+abi_stimeflag+'*.nc'))
        current_abi_l2_file = current_abi_l2_files[0]
        abi_ind_meridional_l2 = abi_ind_meridional_2km[index]
        abi_ind_zonal_l2 = abi_ind_zonal_2km[index]

        dataset = Dataset(current_abi_l2_file,'r')
        cloud_phase = properties = dataset['Phase'][:] 
        # fill_value = dataset.variables['Phase']._FillValue
        # cloud_phase[cloud_phase == fill_value] = np.nan
        abi_cloud[index] = cloud_phase[abi_ind_meridional_l2,abi_ind_zonal_l2]
        dataset.close()

    # Calculate ABI angles
    ABI_Lat_1km = fid['ABI_Lat_1km'][:]
    ABI_Lon_1km = fid['ABI_Lon_1km'][:]
    ABI_Timeflag = select_abi_stimeflag

    print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print(f'Starting with ABI Timeflag:{ABI_Timeflag}')

    SoZeAn = []
    SoAzAn = []
    SeZeAn = []
    SeAzAn = []
    minute = []

    for i in range(len(ABI_Timeflag)):
        timeflag = str(ABI_Timeflag[i])
        if timeflag=='0':
            SoZeAn.append(-9999.0)
            SoAzAn.append(-9999.0)
            SeZeAn.append(-9999.0)
            SeAzAn.append(-9999.0)
            minute.append(-9999.0)
            print('No ABI data available at the current pixel.')
        else:
            lon = ABI_Lon_1km[i]
            lat = ABI_Lat_1km[i]

            doy = int(timeflag[4:7])
            hr = int(timeflag[7:9])
            mi = int(timeflag[9:11])
            sec = int(timeflag[11:13])

            # print(doy_c,':',hr_c,':',mi_c)
            # print('{}CLEAN DAY{}'.format('\033[1m', '\033[0m'))

            minute.append(mi)

            print(f'abi time is: {doy}:{hr}:{mi}')

            tim = ((sec/60 + mi))/60 + hr
            jday = doy + tim/24
            # print('---------------')
            # print('Fractional Day: ', round(C_jday,4),'#############','Fractional Time: ', round(C_tim,4))
            # print('---------------------------------------------------------')

            Sol_Cal = Solar_Calculate(lon, lat, jday, tim) # SZA_Calc(lon, lat, jday, tu)
            SoZeAn.append(Sol_Cal[0])
            SoAzAn.append(Sol_Cal[2])
            
            Sen_Cal = Sensor_Calculate(lon, lat)
            SeZeAn.append(Sen_Cal[0])
            SeAzAn.append(Sen_Cal[1])
            print('---------------------------------------------------------')
    ABI_Solar_Zenith_Angle = np.array(SoZeAn)
    ABI_Solar_Azimuth_Angle = np.array(SoAzAn)
    ABI_Sensor_Zenith_Angle = np.array(SeZeAn)
    ABI_Sensor_Azimuth_Angle = np.array(SeAzAn)


    #save to files
    #check if there's valid data
    n_valid = np.where(select_abi_stimeflag>0)
    if ( len(n_valid[0]) <= 0 ):
        continue
    save_name = 'ABI_G16_Data_CAL_' + cal_timeflag + '.h5'
    sid = h5py.File(save_path+save_name,'w')
    sid.create_dataset('ABI_Obs',data=abi_data)
    sid.create_dataset('ABI_Timeflag',data=select_abi_stimeflag)
    sid.create_dataset('ABI_Cloud_Phase',data=abi_cloud)
    sid.create_dataset('ABI_Solar_Zenith_Angle', data=ABI_Solar_Zenith_Angle)
    sid.create_dataset('ABI_Solar_Azimuth_Angle', data=ABI_Solar_Azimuth_Angle)
    sid.create_dataset('ABI_Sensor_Zenith_Angle', data=ABI_Sensor_Zenith_Angle)
    sid.create_dataset('ABI_Sensor_Azimuth_Angle', data=ABI_Sensor_Azimuth_Angle)
    sid.close()
