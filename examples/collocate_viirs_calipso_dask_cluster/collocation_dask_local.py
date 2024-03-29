# this is a demo to show how to collocate CALIPSO 1km Cloud Layer L2 product with VIIRS Data

from satellite_collocation import *

import sys
import dask
from dask.distributed import as_completed
from dask.distributed import Client, LocalCluster
from dask.distributed import wait

import satellite_collocation.instrument_reader as ir
import satellite_collocation.general_collocation as gc
import numpy as np
import glob
import os
import h5py
from datetimerange import DateTimeRange
import argparse

def collocate_viirs_calipso(clayer1km_file, maximum_distance, maximum_interval, viirs_resolution, vnp03_files, save_path):

    print ('clayer1km_file:', clayer1km_file)
    print ('vnp03_files:', vnp03_files)
    vnp_timeranges = ir.get_modis_viirs_timerange(vnp03_files)

    cal_name = os.path.basename(clayer1km_file)
    pos = cal_name.find('V4-10.')
    cal_timeflag = cal_name[pos+6:pos+27]
    print (cal_timeflag)

    clayer1km_geo = ir.load_caliop_clayer1km_geoloc(cal_1km_file=clayer1km_file)
    caliop_dts = clayer1km_geo['Profile_Datetime']
    caliop_timerange = DateTimeRange(caliop_dts[0],caliop_dts[-1])
    overlap_flags = gc.find_overlap( caliop_timerange, vnp_timeranges )
    indices = np.where(overlap_flags==1)[0]

    save_paths = np.array([], dtype=object)

    for index in indices:

        print ('Find collocation pixels for:')
        print ('File 1:', cal_name)
        print ('File 2:', os.path.basename(vnp03_files[index]))

        vnp03_name = os.path.basename(vnp03_files[index])
        pos = vnp03_name.find('.A')
        vnp_timeflag = vnp03_name[pos+2:pos+14]

        clayer1km_geo = ir.load_caliop_clayer1km_geoloc(cal_1km_file=clayer1km_file)
        vnp_geo = ir.load_viirs_vnp03_geoloc(vnp03_file=vnp03_files[index])

        caliop_lat = clayer1km_geo['Latitude']
        caliop_lon = clayer1km_geo['Longitude']
        caliop_dts = clayer1km_geo['Profile_Datetime']

        viirs_lat = vnp_geo['Latitude']
        viirs_lon = vnp_geo['Longitude']
        viirs_dt  = vnp_geo['Datetime'][1]

        collocation_indexing = gc.track_swath_collocation(track_lat=caliop_lat, track_lon=caliop_lon, track_time=caliop_dts,
                               swath_lat= viirs_lat, swath_lon= viirs_lon, swath_time= viirs_dt,
                               swath_resolution=viirs_resolution,
                               maximum_distance=maximum_distance, maximum_interval=maximum_interval)

        caliop_ind = collocation_indexing['track_index_x']
        if ( len(np.where(caliop_ind>=0)[0])<=1 ):
            print ( 'No collocate pixel found' )
            print ( '' )
            continue
        else:
            n_col =  len(np.where(caliop_ind>=0)[0])
            print("Collocated pixels: %5d" % n_col)
            print ( '' )

        #save co-location indices to files
        sav_name = 'CAL_' + cal_timeflag + '_VNP_' + vnp_timeflag + '_Index.h5'
        sav_file = save_path+'/'+sav_name
        sav_id = h5py.File(sav_file,'w')
        sav_id.create_dataset('CALIPSO_Track_Index',data=collocation_indexing['track_index_x'])
        sav_id.create_dataset('VIIRS_CrossTrack_Index',data=collocation_indexing['swath_index_y'])
        sav_id.create_dataset('VIIRS_AlongTrack_Index',data=collocation_indexing['swath_index_x'])
        sav_id.create_dataset('CALIPSO_VIIRS_Distance',data=collocation_indexing['swath_track_distance'])
        sav_id.create_dataset('CALIPSO_VIIRS_Interval',data=collocation_indexing['swath_track_time_difference'])
        sav_id.close()
        print( 'one index file is saved as ', sav_file)
        save_paths = np.append(save_paths, sav_file)

    return save_paths;


if __name__ =='__main__':

    parser = argparse.ArgumentParser(description='This code is an example of collocating CALIPSO and VIIRS')
    parser.add_argument('-md','--maximum_distance', help='Define the maximum distance of collocated pixels in kilometer', default=5.0)
    parser.add_argument('-mt','--maximum_timeinterval', help='Define the maximum time interval of collocated pixels in minutes', default=15.0)
    parser.add_argument('-sr','--swath_resolution', help='Define the pixel resolution of swath instrument in kilometer', default=0.75)
    parser.add_argument('-tp','--track_instrument_path', help='Define the path of CALIPSO L2 files', required=True)
    parser.add_argument('-sgp','--swath_geo_path', help='Define the path of VIIRS VNP03 files', required=True)
    parser.add_argument('-sdp','--swath_data_path', help='Define the path of VIIRS VNP02 files', required=True)
    parser.add_argument('-sp','--save_path', help='Define the path of output files', required=True)

    args = vars(parser.parse_args())

    #collocate caliop with viirs
    maximum_distance = float(args['maximum_distance'])
    maximum_interval = float(args['maximum_timeinterval'])
    viirs_resolution = float(args['swath_resolution'])

    clayer1km_path = args['track_instrument_path'].strip()
    vnp03_path = args['swath_geo_path'].strip()
    vnp02_path = args['swath_data_path'].strip()
    save_path = args['save_path'].strip()
    if not os.path.exists(save_path):
       os.makedirs(save_path)

    clayer1km_files = sorted(glob.glob(clayer1km_path+'*.hdf'))
    vnp03_files = sorted(glob.glob(vnp03_path+'*.nc'))
    kwargv = { "maximum_distance": maximum_distance, "maximum_interval": maximum_interval, "viirs_resolution": viirs_resolution, "vnp03_files": vnp03_files, "save_path": save_path}


    #create a client at the same node
    client = Client()

    #collocate_viirs_calipso() will be executed in parallel via multiple threads
    tt = client.map(collocate_viirs_calipso, clayer1km_files, **kwargv)

    # aggregate the result
    for future, result in as_completed(tt, with_results= True):
        print("result", result)
