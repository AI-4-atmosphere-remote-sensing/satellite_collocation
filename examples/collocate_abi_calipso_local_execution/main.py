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

args = vars(parser.parse_args())

maximum_distance = float(args['maximum_distance'])
geo_resolution = float(args['geo_resolution'])
cal_clayer_path = args['track_instrument_path'].strip()
save_path = args['save_path'].strip()

# change the next two lines
goesr_16_path = '/tis/modaps/goesr/v10/GOES-16-ABI-L1B-FULLD/'
cal_clayer_path = '/data/shared_data/CALIPSO/CAL_LID_L2_01kmCLay/'

year = 2018
month = 3
day = 1
dateflag = str(year).zfill(4) + str(month).zfill(2) + str(day).zfill(2)
dt = datetime.datetime.strptime(dateflag,'%Y%m%d')
doy = dt.timetuple().tm_yday

#cal_files = sorted(glob.glob(cal_clayer_path+str(year).zfill(4)+'/'+
#                   'CAL_LID_L2_01kmCLay-Standard-V4-10.'+str(year).zfill(4)+'-'+str(month).zfill(2)+'-'+str(day).zfill(2)+'*.hdf'))
cal_files = sorted(glob.glob(cal_clayer_path+str(year).zfill(4)+'/'+
                   'CAL_LID_L2_01kmCLay-Standard-V4-10.2018-03-01T01-36-34*'))

goesr_files = sorted(glob.glob(goesr_16_path+str(year).zfill(4)+'/'+
                     str(doy).zfill(3)+'/*/OR_ABI-L1b-RadF-M3C01*.nc'))

abi_timeranges = ir.get_abi_timerange(goesr_files)

#collocate caliop with abi
maximum_distance = 5.0  #kilometer
maximum_interval = 6.0 #minute
abi_resolution = 1. #kilometer


#use this block if Lat/Lon of ABI instrument need to be calculated
#otherwise, load Lat/Lon directly from files
#calculate
abi_geos = ir.load_abi_geoloc(abi_file=goesr_files[0])
abi_lat = abi_geos['Latitude']
abi_lon = abi_geos['Longitude']
abi_spacemask = abi_geos['Space_Mask']
valid_index = np.where(abi_spacemask==1)
ny = abi_lat.shape[0]
nx = abi_lat.shape[1]
abi_vza = np.full([ny,nx],fill_value=np.nan,dtype=np.float32)
abi_vaa = np.full([ny,nx],fill_value=np.nan,dtype=np.float32)
abi_vangles = sg.calculate_geostationary_geometry(lon0=-75.0,lat=abi_lat[valid_index],lon=abi_lon[valid_index])
abi_vza[valid_index] = abi_vangles['VZA']
abi_vaa[valid_index] = abi_vangles['VAA']

#save lat/lon/mask/vza/vaa to a static file
fid = h5py.File('ABI_Static_1km.h5','w')
fid.create_dataset('Latitude',data=abi_lat)
fid.create_dataset('Longitude',data=abi_lon)
fid.create_dataset('Space_Mask',data=abi_spacemask)
fid.create_dataset('VZA',data=abi_vza)
fid.create_dataset('VAA',data=abi_vaa)
fid.close()
#

#load lat/lon from the static file
fid = h5py.File('ABI_Static_1km.h5','r')
abi_lat = fid['Latitude'][:]
abi_lon = fid['Longitude'][:]
abi_vza = fid['VZA'][:]
abi_vaa = fid['VAA'][:]
abi_spacemask = fid['Space_Mask'][:]
fid.close()
valid_index = np.where(abi_spacemask==1)


for cal_file in cal_files:

    #print (clayer1km_file)
    cal_name = os.path.basename(cal_file)
    pos = cal_name.find('V4-10.')
    cal_timeflag = cal_name[pos+6:pos+27]
    #print (cal_timeflag)

    clayer1km_geo = ir.load_caliop_clayer1km_geoloc(cal_1km_file=cal_file)
    caliop_dts = clayer1km_geo['Profile_Datetime']
    caliop_timerange = DateTimeRange(caliop_dts[0],caliop_dts[-1])
    overlap_flags = gc.find_overlap( caliop_timerange, abi_timeranges )
    indices = np.where(overlap_flags==1)[0]
    
    for index in indices:

        print ('Find collocation pixels for:')
        print ('File 1:', cal_name)
        print ('File 2:', os.path.basename(goesr_files[index]))

        abi_filename = os.path.basename(goesr_files[index])
        abi_startflag = abi_filename[abi_filename.find('_s')+2:abi_filename.find('_s')+15]
        abi_endflag = abi_filename[abi_filename.find('_e')+2:abi_filename.find('_e')+15]
        sdt = datetime.datetime.strptime(abi_startflag,'%Y%j%H%M%S')
        edt = datetime.datetime.strptime(abi_endflag,'%Y%j%H%M%S')
        dur_half = (edt-sdt)/2.0
        mdt = sdt + datetime.timedelta(seconds=dur_half.seconds)

        caliop_lat = clayer1km_geo['Latitude']
        caliop_lon = clayer1km_geo['Longitude']
        caliop_dts = clayer1km_geo['Profile_Datetime']
        disk_dt  = mdt

        collocation_indexing = gc.track_disk_collocation(track_lat=caliop_lat, track_lon=caliop_lon, track_time=caliop_dts,
                               disk_lat=disk_lat,disk_lon=disk_lon,disk_time=disk_dt,
                               disk_resolution=abi_resolution,maximum_distance=maximum_distance,maximum_interval=maximum_interval)


        caliop_ind = collocation_indexing['track_index_x']
        if ( len(np.where(caliop_ind>=0)[0])<=1 ):
            print ( 'No collocate pixel found' )
            print ( '' )
            continue
        else:
            n_col =  len(np.where(caliop_ind>=0)[0])
            print("Collocated pixels: %5d" % n_col)
            print ( '' )

            use_index = np.where(caliop_ind>=0)
            calipso_index = caliop_ind[use_index]
            abi_index1 = collocation_indexing['disk_index_x'][use_index]
            abi_index2 = collocation_indexing['disk_index_y'][use_index]
            distance = collocation_indexing['disk_track_distance'][use_index]
            disk_track_tdiff = collocation_indexing['disk_track_time_difference'][use_index]
            clat = caliop_lat[use_index]
            clon = caliop_lon[use_index]
            alat = disk_lat[abi_index1,abi_index2]
            alon = disk_lon[abi_index1,abi_index2]
          
            save_name = 'Ind_CAL_' + cal_timeflag + '_ABI_G16_s' + abi_startflag + '_e' + abi_endflag + '.h5'
            print (save_name)
            sid = h5py.File(save_name,'w')
            sid.create_dataset('CALIPSO_Lat',data=clat)
            sid.create_dataset('CALIPSO_Lon',data=clon)
            sid.create_dataset('ABI_Lat',data=alat)
            sid.create_dataset('ABI_Lon',data=alon)
            sid.create_dataset('CALIPSO_ABI_Distance',data=distance)
            sid.create_dataset('CALIPSO_ABI_TimeDiff',data=disk_track_tdiff)
            sid.create_dataset('CALIPSO_Index',data=calipso_index)
            sid.create_dataset('ABI_Index1',data=abi_index1)
            sid.create_dataset('ABI_Index2',data=abi_index2)
            sid.close()            
