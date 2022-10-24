# this is a demo to show how to collocate CALIPSO 1km Cloud Layer L2 product with VIIRS Data

from satellite_collocation import *
import sys
import satellite_collocation.instrument_reader as ir
import satellite_collocation.general_collocation as gc
import satellite_collocation.version as version
import numpy as np
import glob
import os
import h5py
from datetimerange import DateTimeRange

import argparse
import string

parser = argparse.ArgumentParser(description='This code is an example of collocating CALIPSO and VIIRS')
parser.add_argument('-md','--maximum_distance', help='Define the maximum distance of collocated pixels in kilometer', default=5.0)
parser.add_argument('-mt','--maximum_timeinterval', help='Define the maximum time interval of collocated pixels in minutes', default=15.0)
parser.add_argument('-sr','--swath_resolution', help='Define the pixel resolution of swath instrument in kilometer', default=0.75)
parser.add_argument('-tp1','--track_instrument_path1', help='Define the path of CALIPSO L2 1km files', required=True)
parser.add_argument('-tp5','--track_instrument_path5', help='Define the path of CALIPSO L2 5km files', default="None")
parser.add_argument('-sgp','--swath_geo_path', help='Define the path of VIIRS VNP03 files', required=True)
parser.add_argument('-sdp','--swath_data_path', help='Define the path of VIIRS VNP02 files', required=True)
parser.add_argument('-sp','--save_path', help='Define the path of output files', default='./')

args = vars(parser.parse_args())

#collocate caliop with viirs
maximum_distance = float(args['maximum_distance'])
maximum_interval = float(args['maximum_timeinterval'])
viirs_resolution = float(args['swath_resolution'])

clayer1km_path = args['track_instrument_path1'].strip()
clayer5km_path = args['track_instrument_path5'].strip()
vnp03_path = args['swath_geo_path'].strip()
vnp02_path = args['swath_data_path'].strip()
save_path = args['save_path'].strip()

#collocate caliop with viirs
#maximum_distance = 5.0  #kilometer
#maximum_interval = 15.0 #minute
#viirs_resolution = 0.75 #kilometer

#clayer1km_path = '/umbc/rs/nasa-access/users/jianwu/collocation-test-data/CALIPSO-L2-01km-CLayer/'
#clayer5km_path = '/umbc/rs/nasa-access/users/jianwu/collocation-test-data/CALIPSO-L2-05km-CLayer/'
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
        calipso_dataset_clayer_names_1km = ['Longitude','Latitude','Layer_Top_Altitude','Layer_Base_Altitude',
                                           'Layer_Top_Temperature','Layer_Base_Temperature', 'Opacity_Flag',
                                           'Integrated_Attenuated_Total_Color_Ratio',
                                           'Integrated_Attenuated_Backscatter_532',
                                           'Integrated_Attenuated_Backscatter_1064',
                                           'IGBP_Surface_Type','Snow_Ice_Surface_Type','Number_Layers_Found',
                                           'Feature_Classification_Flags']
        
        collocation_index_1km = np.where(caliop_ind>=0)[0]
        
        
        caliop_data_1km = ir.load_collocate_caliop_dataset(calipso_file=clayer1km_file,calipso_index=collocation_index_1km,
                      selected_datasets=calipso_dataset_clayer_names_1km)
        
        #find clayer5km file
        if (clayer5km_path!="None"):
            clayer5km_files = sorted(glob.glob(clayer5km_path+'*'+cal_timeflag+'*.hdf'))
            if (len(clayer5km_files)==1):
                clayer5km_file = clayer5km_files[0]
                calipso_dataset_clayer_names_5km = ['Longitude','Latitude','Layer_Top_Altitude','Layer_Base_Altitude',
                                           'Layer_Top_Temperature','Layer_Base_Temperature', 'Opacity_Flag',
                                           'Final_532_Lidar_Ratio', 'Integrated_Particulate_Depolarization_Ratio',
                                           'Integrated_Attenuated_Total_Color_Ratio',
                                           'Integrated_Attenuated_Backscatter_532',
                                           'Integrated_Attenuated_Backscatter_1064',
                                           'Feature_Optical_Depth_532', 'Number_Layers_Found',
                                           'Column_Optical_Depth_Tropospheric_Aerosols_532',
                                           'Column_Optical_Depth_Stratospheric_Aerosols_532',
                                           'Column_Optical_Depth_Tropospheric_Aerosols_1064',
                                           'Column_Optical_Depth_Stratospheric_Aerosols_1064',
                                           'Feature_Classification_Flags']
                collocation_index_5km = collocation_index_1km//5
                caliop_data_5km = ir.load_collocate_caliop_dataset(calipso_file=clayer5km_file,calipso_index=collocation_index_5km,
                                    selected_datasets=calipso_dataset_clayer_names_5km)

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
        
        sav_id.attrs['Version'] = version.version
        sav_id.attrs['Project'] = version.project_name
        sav_id.attrs['Task'] = version.task_name
        sav_id.attrs['Project_PI'] = version.project_pi
        sav_id.attrs['Project_CoIs'] = version.project_cois
        sav_id.attrs['Authors'] = version.software_author
        sav_id.attrs['Contact1'] = version.contact1
        sav_id.attrs['Contact2'] = version.contact2
        sav_id.attrs['Description'] = version.description
        sav_id.attrs['Input_Files'] = cal_name + ',' + os.path.basename(vnp03_files[index])
        sav_id.attrs['CALIPSO_VIIRS_Maximum_Distance_kilometer'] = maximum_distance
        sav_id.attrs['CALIPSO_VIIRS_Maximum_Interval_minute'] = maximum_interval
        
        dset_id = sav_id.create_dataset('CALIPSO_Track_Index',data=collocation_indexing['track_index_x'])
        dset_id.attrs['Description'] = 'CALIPSO Track Indices, start from 0. Negative if unusable.'
        dset_id.attrs['fillvalue'] = -1

        dset_id = sav_id.create_dataset('VIIRS_CrossTrack_Index',data=collocation_indexing['swath_index_y'])
        dset_id.attrs['Description'] = 'VIIRS Cross Track Indices, valid range 0 - 3199. Negative if unusable.'
        dset_id.attrs['fillvalue'] = -1

        dset_id = sav_id.create_dataset('VIIRS_AlongTrack_Index',data=collocation_indexing['swath_index_x'])
        dset_id.attrs['Description'] = 'VIIRS Along Track Indices, valid range 0 - 3247. Negative if unusable.'
        dset_id.attrs['fillvalue'] = -1

        dset_id = sav_id.create_dataset('CALIPSO_VIIRS_Distance',data=collocation_indexing['swath_track_distance'])
        dset_id.attrs['Description'] = 'Distances between CALIPSO and VIIRS pixels in kilometer. Negative if unusable.'
        dset_id.attrs['fillvalue'] = -9999.99

        dset_id = sav_id.create_dataset('CALIPSO_VIIRS_Interval',data=collocation_indexing['swath_track_time_difference'])
        dset_id.attrs['Description'] = 'Time interval between CALIPSO and VIIRS pixels in minute. Positive if CALIPSO observes after VIIRS'
        dset_id.attrs['fillvalue'] = -9999.99
        
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
