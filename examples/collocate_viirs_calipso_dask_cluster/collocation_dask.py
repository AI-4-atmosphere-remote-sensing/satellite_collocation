# this is a demo to show how to collocate CALIPSO 1km Cloud Layer L2 product with VIIRS Data

from satellite_collocation import *

import sys
import dask
from dask.distributed import as_completed
from dask_jobqueue import SLURMCluster
from dask.distributed import Client, LocalCluster
from dask.distributed import wait

import satellite_collocation.instrument_reader as ir
import satellite_collocation.general_collocation as gc
import numpy as np
import glob
import os
import h5py
from datetimerange import DateTimeRange

def collocate_viirs_calipso(clayer1km_file, vnp03_file):

    print ('clayer1km_file:', clayer1km_file)
    print ('vnp03_file:', vnp03_file)
    vnp_timeranges = ir.get_modis_viirs_timerange([vnp03_file])

    cal_name = os.path.basename(clayer1km_file)
    pos = cal_name.find('V4-10.')
    cal_timeflag = cal_name[pos+6:pos+27]
    print (cal_timeflag)

    clayer1km_geo = ir.load_caliop_clayer1km_geoloc(cal_1km_file=clayer1km_file)
    caliop_dts = clayer1km_geo['Profile_Datetime']
    caliop_timerange = DateTimeRange(caliop_dts[0],caliop_dts[-1])
    overlap_flags = gc.find_overlap( caliop_timerange, vnp_timeranges )
    indices = np.where(overlap_flags==1)[0]

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
        return caliop_ind;


if __name__ =='__main__':

    #collocate caliop with viirs
    maximum_distance = 5.0  #kilometer
    maximum_interval = 15.0 #minute
    viirs_resolution = 0.75 #kilometer

    clayer1km_path = '/umbc/rs/nasa-access/users/jianwu/collocation-test-data/CALIPSO-L2-01km-CLayer/'
    vnp03_path = '/umbc/rs/nasa-access/users/jianwu/collocation-test-data/VNP03MOD-VIIRS-Coordinates/'
    save_path = '/umbc/rs/nasa-access/users/jianwu/collocation-test-data/collocation-output/'

    clayer1km_files = sorted(glob.glob(clayer1km_path+'*.hdf'))
    vnp03_files = sorted(glob.glob(vnp03_path+'*.nc'))

    #create a slurm cluster and get its client 
    '''
    cluster = SLURMCluster(cores=32, memory='390 GB',processes=32, project='pi_jianwu',\
        queue='high_mem', walltime='16:00:00', job_extra=['--exclusive', '--qos=medium+'])
    cluster.scale(jobs=2)
    print(cluster.job_script())
    client = Client(cluster)
    '''
    #create a client at the same node, useful for debugging
    client = Client()
    tt = client.map(collocate_viirs_calipso, clayer1km_files, vnp03_files)

    # aggregate the result
    for future, result in as_completed(tt, with_results= True):
        print(result)
