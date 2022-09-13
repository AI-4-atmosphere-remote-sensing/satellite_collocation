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

import warnings
warnings.filterwarnings("ignore")

import argparse
import string

parser = argparse.ArgumentParser(description='This code is an example of collocating CALIPSO and ABI onboard GOESR_16')
#parser.add_argument('-md','--maximum_distance', help='Define the maximum distance of collocated pixels in kilometer', required=True)
#parser.add_argument('-gr','--geo_resolution', help='Define the pixel resolution of ABI in kilometer', required=True)
parser.add_argument('-tp','--track_instrument_path', help='Define the path of CALIPSO L2 files', required=True)
parser.add_argument('-sp','--save_path', help='Define the path of output files', required=True)
parser.add_argument('-y','--year', help='Define the year of CALIPSO files, format YYYY', default=argparse.SUPPRESS)
parser.add_argument('-ym','--yearmonth', help='Define the month of CALIPSO files, format YYYYMM', default=argparse.SUPPRESS)
parser.add_argument('-ymd','--yearmonthday', help='Define the date flag of CALIPSO files, format YYYYMMDD', default=argparse.SUPPRESS)

args = vars(parser.parse_args())

#maximum_distance = float(args['maximum_distance'])
#geo_resolution = float(args['geo_resolution'])
cal_clayer_path = args['track_instrument_path'].strip()
save_path = args['save_path'].strip()

geo_static_files = ['./goesr_16_static_hkm.h5', './goesr_16_static_1km.h5', './goesr_16_static_2km.h5']

if ("year" in args):
    dateflag = args['year'].strip()
    year = int(dateflag[0:4])
    cal_files = sorted(glob.glob(cal_clayer_path+
                       'CAL_LID_L2_01kmCLay-Standard-V*.'+
                       str(year).zfill(4)+'-'+'*.hdf'))
elif ("yearmonth" in args):
    dateflag = args['yearmonth'].strip()
    year = int(dateflag[0:4])
    month = int(dateflag[4:6])
    cal_files = sorted(glob.glob(cal_clayer_path+
                       'CAL_LID_L2_01kmCLay-Standard-V*.'+
                       str(year).zfill(4)+'-'+str(month).zfill(2)+'-'+'*.hdf'))
elif ("yearmonthday" in args):
    dateflag = args['yearmonthday'].strip()
    year = int(dateflag[0:4])
    month = int(dateflag[4:6])
    day = int(dateflag[6:8])
    cal_files = sorted(glob.glob(cal_clayer_path+
                       'CAL_LID_L2_01kmCLay-Standard-V*.'+
                       str(year).zfill(4)+'-'+str(month).zfill(2)+'-'+str(day).zfill(2)+'*.hdf'))
else:
    cal_files = sorted(glob.glob(cal_clayer_path+'*.hdf'))
    
#collocate caliop with abi
    
#assume that all abi files share the same Lat/Lon/Viewing angles

disk_lons = []
disk_lats = []

for geo_static_file in geo_static_files:
    #the three files are for 0.5/1.0/2.0 km resolutions, respectively
    fid = h5py.File(geo_static_file,'r')
    abi_lat = fid['Latitude'][:]
    abi_lon = fid['Longitude'][:]
    abi_spacemask = fid['SpaceMask'][:]
    valid_index = np.where(abi_spacemask==1)
    fid.close()
    
    disk_lon = np.full([abi_lat.shape[0],abi_lat.shape[1]],fill_value=-9999.99)
    disk_lat = np.full([abi_lat.shape[0],abi_lat.shape[1]],fill_value=-9999.99)
    disk_lon[valid_index] = abi_lon[valid_index]
    disk_lat[valid_index] = abi_lat[valid_index]
    disk_lons.append(disk_lon)
    disk_lats.append(disk_lat)

for cal_file in cal_files:
    
    #print (clayer1km_file)
    cal_name = os.path.basename(cal_file)
    pos = cal_name.find('V4')
    cal_timeflag = cal_name[pos+6:pos+27]
    #print (cal_timeflag)

    save_name = 'Ind_CAL_' + cal_timeflag + '_ABI_G16.h5'
    if (os.path.exists(save_path+save_name)):
        continue
    
    clayer1km_geo = ir.load_caliop_clayer1km_geoloc(cal_1km_file=cal_file)

    print ('Find collocation pixels for:')
    print ('CALIPSO File:', cal_name)
    
    caliop_lat = clayer1km_geo['Latitude']
    caliop_lon = clayer1km_geo['Longitude']
    caliop_dts = clayer1km_geo['Profile_Datetime']
    caliop_utcs = clayer1km_geo['Profile_UTC']
    caliop_timerange = DateTimeRange(caliop_dts[0],caliop_dts[-1])

    collocation_indexing_hkm = gc.track_disk_collocation_test(track_lat=caliop_lat, track_lon=caliop_lon, track_time=caliop_dts,
                               disk_lat=disk_lats[0], disk_lon=disk_lons[0],
                               disk_resolution=0.5,maximum_distance=2.0)
    collocation_indexing_1km = gc.track_disk_collocation_test(track_lat=caliop_lat, track_lon=caliop_lon, track_time=caliop_dts,
                               disk_lat=disk_lats[1], disk_lon=disk_lons[1],
                               disk_resolution=1,maximum_distance=4.0)
    collocation_indexing_2km = gc.track_disk_collocation_test(track_lat=caliop_lat, track_lon=caliop_lon, track_time=caliop_dts,
                               disk_lat=disk_lats[2], disk_lon=disk_lons[2],
                               disk_resolution=2,maximum_distance=8.0)

    print (collocation_indexing_hkm)
    disk_ind_meridional_hkm = collocation_indexing_hkm['disk_index_meridional']
    disk_ind_zonal_hkm = collocation_indexing_hkm['disk_index_zonal']

    disk_ind_meridional_1km = collocation_indexing_1km['disk_index_meridional']
    disk_ind_zonal_1km = collocation_indexing_1km['disk_index_zonal']

    disk_ind_meridional_2km = collocation_indexing_2km['disk_index_meridional']
    disk_ind_zonal_2km = collocation_indexing_2km['disk_index_zonal']

    caliop_ind = np.arange(len(caliop_lat))

    valid_index = np.where( (disk_ind_meridional_hkm>=0) & (disk_ind_meridional_1km>=0) & (disk_ind_meridional_2km>=0) ) [0]

    #save index into a h5 file 

    if (len(valid_index) > 1) : 
        print ( 'Find ', len(valid_index), ' collocated pixels')
        #print (disk_ind_meridional_hkm[valid_index])
        #print (disk_ind_meridional_1km[valid_index])
        #print (disk_ind_meridional_2km[valid_index])

        clat = caliop_lat[valid_index]
        clon = caliop_lon[valid_index]
        cind = caliop_ind[valid_index]
        cutc = caliop_utcs[valid_index]

        #abi index and lat/lon at different resolutions
        abi_ind_meridional_hkm = disk_ind_meridional_hkm[valid_index]
        abi_ind_zonal_hkm = disk_ind_zonal_hkm[valid_index]
        abi_ind_meridional_1km = disk_ind_meridional_1km[valid_index]
        abi_ind_zonal_1km = disk_ind_zonal_1km[valid_index]
        abi_ind_meridional_2km = disk_ind_meridional_2km[valid_index]
        abi_ind_zonal_2km = disk_ind_zonal_2km[valid_index]

        abi_lat_hkm = disk_lats[0][abi_ind_meridional_hkm,abi_ind_zonal_hkm]
        abi_lon_hkm = disk_lons[0][abi_ind_meridional_hkm,abi_ind_zonal_hkm]
        abi_lat_1km = disk_lats[1][abi_ind_meridional_1km,abi_ind_zonal_1km]
        abi_lon_1km = disk_lons[1][abi_ind_meridional_1km,abi_ind_zonal_1km]
        abi_lat_2km = disk_lats[2][abi_ind_meridional_2km,abi_ind_zonal_2km]
        abi_lon_2km = disk_lons[2][abi_ind_meridional_2km,abi_ind_zonal_2km]

        #abi-calipso distances at different resolutions
        distance_hkm = collocation_indexing_hkm['disk_track_distance'][valid_index]
        distance_1km = collocation_indexing_1km['disk_track_distance'][valid_index]
        distance_2km = collocation_indexing_2km['disk_track_distance'][valid_index]

        sid = h5py.File(save_path+save_name,'w')
        sid.create_dataset('CALIPSO_Lat',data=clat)
        sid.create_dataset('CALIPSO_Lon',data=clon)
        sid.create_dataset('CALIPSO_Index',data=cind)
        sid.create_dataset('CALIPSO_UTC', data=cutc)

        sid.create_dataset('ABI_Lat_hkm',data=abi_lat_hkm)
        sid.create_dataset('ABI_Lon_hkm',data=abi_lon_hkm)
        sid.create_dataset('ABI_Lat_1km',data=abi_lat_1km)
        sid.create_dataset('ABI_Lon_1km',data=abi_lon_1km)
        sid.create_dataset('ABI_Lat_2km',data=abi_lat_2km)
        sid.create_dataset('ABI_Lon_2km',data=abi_lon_2km)
        sid.create_dataset('CALIPSO_ABI_Distance_hkm',data=distance_hkm)
        sid.create_dataset('CALIPSO_ABI_Distance_1km',data=distance_1km)
        sid.create_dataset('CALIPSO_ABI_Distance_2km',data=distance_2km)

        sid.create_dataset('ABI_Index_Meridional_hkm',data=abi_ind_meridional_hkm)
        sid.create_dataset('ABI_Index_Zonal_hkm',data=abi_ind_zonal_hkm)
        sid.create_dataset('ABI_Index_Meridional_1km',data=abi_ind_meridional_1km)
        sid.create_dataset('ABI_Index_Zonal_1km',data=abi_ind_zonal_1km)
        sid.create_dataset('ABI_Index_Meridional_2km',data=abi_ind_meridional_2km)
        sid.create_dataset('ABI_Index_Zonal_2km',data=abi_ind_zonal_2km)

        sid.close()

