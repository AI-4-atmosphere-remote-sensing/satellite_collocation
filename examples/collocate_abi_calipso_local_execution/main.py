import sys
sys.path.insert(1,general_lib_path)
import os
import numpy as np
import general_collocation as gc
import instrument_reader as ir
import satellite_geo as sg

import glob
import datetime
from datetimerange import DateTimeRange
import h5py

import warnings
warnings.filterwarnings("ignore")

import argparse
import string

parser = argparse.ArgumentParser(description='This code is an example of collocating CALIPSO and ABI onboard GOESR_16')
parser.add_argument('-md','--maximum_distance', help='Define the maximum distance of collocated pixels in kilometer', required=True)
parser.add_argument('-gr','--geo_resolution', help='Define the pixel resolution of ABI in kilometer', required=True)
parser.add_argument('-tp','--track_instrument_path', help='Define the path of CALIPSO L2 files', required=True)
parser.add_argument('-sp','--save_path', help='Define the path of output files', required=True)
parser.add_argument('-ymd','--yearmonthday', help='Define the date flag of CALIPSO files, format YYYYMMDD', default=argparse.SUPPRESS)

args = vars(parser.parse_args())

maximum_distance = float(args['maximum_distance'])
geo_resolution = float(args['geo_resolution'])
cal_clayer_path = args['track_instrument_path'].strip()
save_path = args['save_path'].strip()

geo_static_file = './goesr_16_static_1km.h5'

if ("yearmonthday" in args):
    dateflag = args['yearmonthday'].strip()
    year = int(dateflag[0:4])
    month = int(dateflag[4:6])
    day = int(dateflag[6:8])
    cal_files = sorted(glob.glob(cal_clayer_path+
                       'CAL_LID_L2_01kmCLay-Standard-V4-10.'+
                       str(year).zfill(4)+'-'+str(month).zfill(2)+'-'+str(day).zfill(2)+'*.hdf'))
else:
    cal_files = sorted(glob.glob(cal_clayer_path+'*.hdf'))

#collocate caliop with abi

#assume that all abi files share the same Lat/Lon/Viewing angles
fid = h5py.File(geo_static_file,'r')
abi_lat_1km = fid['Latitude'][:]
abi_lon_1km = fid['Longitude'][:]
abi_spacemask_1km = fid['SpaceMask'][:]
valid_index_1km = np.where(abi_spacemask_1km==1)
fid.close()

for cal_file in cal_files:

    #print (clayer1km_file)
    cal_name = os.path.basename(cal_file)
    pos = cal_name.find('V4-10.')
    cal_timeflag = cal_name[pos+6:pos+27]
    #print (cal_timeflag)

    clayer1km_geo = ir.load_caliop_clayer1km_geoloc(cal_1km_file=cal_file)
    caliop_dts = clayer1km_geo['Profile_Datetime']
    caliop_timerange = DateTimeRange(caliop_dts[0],caliop_dts[-1])
   
    print ('Find collocation pixels for:')
    print ('CALIPSO File:', cal_name)
    
    caliop_lat = clayer1km_geo['Latitude']
    caliop_lon = clayer1km_geo['Longitude']
    caliop_dts = clayer1km_geo['Profile_Datetime']
    
    collocation_indexing = gc.track_disk_collocation_new(track_lat=caliop_lat, track_lon=caliop_lon, track_time=caliop_dts,
                           disk_lat=disk_lat_1km, disk_lon=disk_lon_1km,
                           disk_resolution=geo_resolution,maximum_distance=maximum_distance)

    disk_ind_x = collocation_indexing['disk_index_x']
    disk_ind_y = collocation_indexing['disk_index_y']
    calipso_ind = np.arange(len(caliop_lat))

    if ( len(np.where(disk_ind_x>=0)[0])<=1 ):
        print ( 'No collocate pixel found' )
        print ( '' )
        continue
    else:
        n_col =  len(np.where(disk_ind_x>=0)[0])
        print("Collocated pixels: %5d" % n_col)
        print ( '' )

        use_index = np.where(disk_ind_x>=0)
        abi_index1 = collocation_indexing['disk_index_x'][use_index]
        abi_index2 = collocation_indexing['disk_index_y'][use_index]
        distance = collocation_indexing['disk_track_distance'][use_index]
        #disk_track_tdiff = collocation_indexing['disk_track_time_difference'][use_index]
        clat = caliop_lat[use_index]
        clon = caliop_lon[use_index]
        alat = disk_lat_1km[abi_index1,abi_index2]
        alon = disk_lon_1km[abi_index1,abi_index2]

        save_name = 'Ind_CAL_' + cal_timeflag + '_ABI_G16_1km.h5'
        print (save_name)
        sid = h5py.File(save_path+save_name,'w')
        sid.create_dataset('CALIPSO_Lat',data=clat)
        sid.create_dataset('CALIPSO_Lon',data=clon)
        sid.create_dataset('ABI_Lat',data=alat)
        sid.create_dataset('ABI_Lon',data=alon)
        sid.create_dataset('CALIPSO_ABI_Distance',data=distance)
        #sid.create_dataset('CALIPSO_ABI_TimeDiff',data=disk_track_tdiff)
        sid.create_dataset('CALIPSO_Index',data=calipso_ind[use_index])
        sid.create_dataset('ABI_Index1',data=abi_index1)
        sid.create_dataset('ABI_Index2',data=abi_index2)
        sid.close()
