import sys
sys.path.insert(1,'/umbc/rs/nasa-access/users/xingyan/satellite_collocation/satellite_collocation_github/satellite_collocation/')
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

import os
import numpy as np
from pyhdf.SD import SD, SDC
from pyhdf.HDF import *
from pyhdf.V import VD
from pyhdf.VS import *
from netCDF4 import Dataset
from math import *
import datetime
import h5py
from datetimerange import DateTimeRange

cal_clayer_path = '/umbc/rs/nasa-access/users/xingyan/data/calipso_201711/1km_v20/'
save_path = '/umbc/rs/nasa-access/users/xingyan/satellite_collocation/satellite_collocation_github/examples/collocate_abi_calipso_local_execution/generate_2017/CALIPSO_Index/201711/'

geo_static_files = ['./static/goesr_16_static_hkm.h5', './static/goesr_16_static_1km.h5', './static/goesr_16_static_2km.h5']

cal_files = sorted(glob.glob(cal_clayer_path+'*.hdf'))

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
    print (cal_timeflag)

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

        #save other calipso variables
        cal_1km = SD(cal_file,SDC.READ)
        Layer_Top_Altitude = cal_1km.select('Layer_Top_Altitude').get()
        CALIPSO_Layer_Top_Altitude = Layer_Top_Altitude[valid_index,:]
        Layer_Top_Temperature = cal_1km.select('Layer_Top_Temperature').get()
        CALIPSO_Layer_Top_Temperature = Layer_Top_Temperature[valid_index,:]
        Layer_Base_Temperature = cal_1km.select('Layer_Base_Temperature').get()
        CALIPSO_Layer_Base_Temperature = Layer_Base_Temperature[valid_index,:]
        Integrated_Attenuated_Total_Color_Ratio = cal_1km.select('Integrated_Attenuated_Total_Color_Ratio').get()
        CALIPSO_Integrated_Attenuated_Total_Color_Ratio = Integrated_Attenuated_Total_Color_Ratio[valid_index,:]
        Integrated_Attenuated_Backscatter_532 = cal_1km.select('Integrated_Attenuated_Backscatter_532').get()
        CALIPSO_Integrated_Attenuated_Backscatter_532 = Integrated_Attenuated_Backscatter_532[valid_index,:]
        Integrated_Attenuated_Backscatter_1064 = cal_1km.select('Integrated_Attenuated_Backscatter_1064').get()
        CALIPSO_Integrated_Attenuated_Backscatter_1064 = Integrated_Attenuated_Backscatter_1064[valid_index,:]
        IGBP_Surface_Type = cal_1km.select('IGBP_Surface_Type').get()
        CALIPSO_IGBP_Surface_Type = IGBP_Surface_Type[valid_index,:]
        Snow_Ice_Surface_Type = cal_1km.select('Snow_Ice_Surface_Type').get()
        CALIPSO_Snow_Ice_Surface_Type = Snow_Ice_Surface_Type[valid_index,:]
        Number_Layers_Found = cal_1km.select('Number_Layers_Found').get()
        CALIPSO_Number_Layers_Found = Number_Layers_Found[valid_index]
        Feature_Classification_Flags = cal_1km.select('Feature_Classification_Flags').get()
        CALIPSO_Feature_Classification_Flags = Feature_Classification_Flags[valid_index,:]

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

        sid.create_dataset('CALIPSO_Layer_Top_Altitude',data=CALIPSO_Layer_Top_Altitude)
        sid.create_dataset('CALIPSO_Layer_Top_Temperature',data=CALIPSO_Layer_Top_Temperature)
        sid.create_dataset('CALIPSO_Layer_Base_Temperature',data=CALIPSO_Layer_Base_Temperature)
        sid.create_dataset('CALIPSO_Integrated_Attenuated_Total_Color_Ratio',data=CALIPSO_Integrated_Attenuated_Total_Color_Ratio)
        sid.create_dataset('CALIPSO_Integrated_Attenuated_Backscatter_532',data=CALIPSO_Integrated_Attenuated_Backscatter_532)
        sid.create_dataset('CALIPSO_Integrated_Attenuated_Backscatter_1064',data=CALIPSO_Integrated_Attenuated_Backscatter_1064)
        sid.create_dataset('IGBP_Surface_Type',data=IGBP_Surface_Type)
        sid.create_dataset('CALIPSO_IGBP_Surface_Type',data=CALIPSO_IGBP_Surface_Type)
        sid.create_dataset('CALIPSO_Snow_Ice_Surface_Type',data=CALIPSO_Snow_Ice_Surface_Type)
        sid.create_dataset('CALIPSO_Number_Layers_Found',data=CALIPSO_Number_Layers_Found)
        sid.create_dataset('CALIPSO_Feature_Classification_Flags',data=CALIPSO_Feature_Classification_Flags)

        sid.close()
