# this is a demo to show how to collocate CALIPSO 1km Cloud Layer L2 product with VIIRS Data

from satellite_collocation import *
import sys
import satellite_collocation.instrument_reader as ir
import satellite_collocation.general_collocation as gc
import numpy as np
import glob
import os
import h5py
from datetimerange import DateTimeRange

import argparse
import string

parser = argparse.ArgumentParser(description='This code is an example of collocating CALIPSO and VIIRS')
parser.add_argument('-md','--maximum_distance', help='Define the maximum distance of collocated pixels in kilometer', required=True)
parser.add_argument('-mt','--maximum_timeinterval', help='Define the maximum time interval of collocated pixels in minutes',required=True)
parser.add_argument('-sr','--swath_resolution', help='Define the pixel resolution of swath instrument in kilometer', required=True)
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

#collocate caliop with viirs
#maximum_distance = 5.0  #kilometer
#maximum_interval = 15.0 #minute
#viirs_resolution = 0.75 #kilometer

#clayer1km_path = '/umbc/rs/nasa-access/users/jianwu/collocation-test-data/CALIPSO-L2-01km-CLayer/'
#vnp03_path = '/umbc/rs/nasa-access/users/jianwu/collocation-test-data/VNP03MOD-VIIRS-Coordinates/'
#vnp02_path = '/umbc/rs/nasa-access/users/jianwu/collocation-test-data/VNP02MOD-VIIRS-Attributes/'
#save_path = '/umbc/rs/nasa-access/users/jianwu/collocation-test-data/collocation-output/'

clayer1km_files = sorted(glob.glob(clayer1km_path+'*.hdf'))
vnp03_files = sorted(glob.glob(vnp03_path+'*.nc'))
vnp_timeranges = ir.get_modis_viirs_timerange(vnp03_files)
print ('vnp_timeranges:', vnp_timeranges)

for clayer1km_file in clayer1km_files:

    print (clayer1km_file)
    cal_name = os.path.basename(clayer1km_file)
    pos = cal_name.find('V4-10.')
    cal_timeflag = cal_name[pos+6:pos+27]
    #print (cal_timeflag)

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

        #load collocated dataset(s) from CALIPSO and VIIRS
        calipso_dataset_names = ['Longitude','Latitude','Layer_Top_Temperature','Layer_Top_Pressure',
                            'IGBP_Surface_Type','Snow_Ice_Surface_Type','Number_Layers_Found',
                            'Feature_Classification_Flags']

        caliop_data = ir.load_collocate_caliop_dataset(calipso_file=clayer1km_file,calipso_index=collocation_indexing['track_index_x'],
                      selected_datasets=calipso_dataset_names)

        vnp02_file = glob.glob(vnp02_path+'*'+vnp_timeflag+'*.nc')
        if (len(vnp02_file)!=1):
            continue
        viirs_02_datasets = ['/observation_data/M01', '/observation_data/M02', '/observation_data/M03',
                             '/observation_data/M04', '/observation_data/M05', '/observation_data/M06',
                             '/observation_data/M07', '/observation_data/M08', '/observation_data/M09',
                             '/observation_data/M10', '/observation_data/M11', '/observation_data/M12',
                             '/observation_data/M13', '/observation_data/M14', '/observation_data/M15',
                             '/observation_data/M16']
        
        #get observations of collocated VIIRS pixels
        viirs_along = collocation_indexing['swath_index_x']
        viirs_cross = collocation_indexing['swath_index_y']
        viirs_data = ir.load_collocate_viirs_dataset(viirs_file=vnp02_file[0],viirs_along=viirs_along,
                     viirs_cross=viirs_cross,selected_datasets=viirs_02_datasets)

        #get surrounding narrow band of collocated VIIRS pixels
        #[left_end-collocated-right_end]
        left_end = -2
        right_end = 2
        viirs_data_narrow_belt = ir.load_surrounding_viirs_dataset(viirs_file=vnp02_file[0],viirs_along=viirs_along,
                                 viirs_cross=viirs_cross,left_end=left_end,right_end=right_end,selected_datasets=viirs_02_datasets)

        #save co-location indices to files
        sav_name = 'CAL_' + cal_timeflag + '_VNP_' + vnp_timeflag + '_Index.h5'
        sav_id = h5py.File(save_path+sav_name,'w')
        sav_id.create_dataset('CALIPSO_Track_Index',data=collocation_indexing['track_index_x'])
        sav_id.create_dataset('VIIRS_CrossTrack_Index',data=collocation_indexing['swath_index_y'])
        sav_id.create_dataset('VIIRS_AlongTrack_Index',data=collocation_indexing['swath_index_x'])
        sav_id.create_dataset('CALIPSO_VIIRS_Distance',data=collocation_indexing['swath_track_distance'])
        sav_id.create_dataset('CALIPSO_VIIRS_Interval',data=collocation_indexing['swath_track_time_difference'])

        save_viirs_02_datasets_names = ['VIIRS_M01', 'VIIRS_M02', 'VIIRS_M03',
                                        'VIIRS_M04', 'VIIRS_M05', 'VIIRS_M06',
                                        'VIIRS_M07', 'VIIRS_M08', 'VIIRS_M09',
                                        'VIIRS_M10', 'VIIRS_M11', 'VIIRS_M12',
                                        'VIIRS_M13', 'VIIRS_M14', 'VIIRS_M15',
                                        'VIIRS_M16']

        for viirs_02_dataset in viirs_02_datasets:
            sav_id.create_dataset(viirs_02_dataset,data=viirs_data_narrow_belt[viirs_02_dataset])
        sav_id.close()

       
        #finished
        #You are able to save collocated CALIPSO data (caliop_data) and VIIRS data (viirs_data) to any files.
