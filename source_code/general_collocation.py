#general collocation 
#this package includes necessary functions for finding collocated pixel indices from different instruments

import os
import numpy as np
from pyhdf.SD import SD, SDC
from pyhdf.HDF import *
from pyhdf.V import VD
from pyhdf.VS import *
from netCDF4 import Dataset
from math import *
import datetime
from datetimerange import DateTimeRange

import satellite_geo as sg


# function name: find_overlap
# purpose: Find temporally overlapped source files with a given target file 
# input: target_timerange [DateTimeRange object from "get_xxxx_timerange" function in instrument_reader.py]
# input: source_timeranges [DateTimeRange object from "get_xxxx_timerange" function in instrument_reader.py]
# output: Overlapping flag of each source timeranges [0: non-overlapping, 1: overlapping]
# usage: overlap_flag = find_overlap(calipso_timerange,viirs_timeranges)

def find_overlap(target_timerange,source_timeranges):

    overlap_flag = np.zeros(len(source_timeranges),dtype=np.int8)
    for i, timerange in enumerate(source_timeranges):
        if (target_timerange.is_intersection(timerange)):
            overlap_flag[i] = 1

    return overlap_flag

# function name: track_swath_collocation
# purpose: Find Collocation Pixels from a track (1-D) of geolocations and a swath (2-D) of geolocations
# input: track_lat, track_lon, track_time
#        1-D lat/lon/time of a track of pixels (e.g., from CALIPSO/CATS/CloudSat)
#        Datetime objects for all track pixels are needed (but can be identical) 
# input: swath_lat, swath_lon, swath_time
#        2-D lat/lon of a swath of pixels (e.g., from MODIS/VIIRS)
#        only a single swath_time is needed for all pixels
# input: swath_resolution
#        native spatial resolution in kilometer of the swath data (e.g., MODIS=1, VIIRS=0.75)
# input: maximum_distance, maximum_interval
#        the maximum spatial distance (in kilometer) and maximum time interval (in minute) between a track pixel and a swath pixel
#        e.g., 5km and 5 minutes, the code will find collocated pixel pairs with maximum spatial distance 5km and +/- 5minutes
# output: Dictionary
#.        'swath_index_x': 1-D array of x indices for collocated swath pixels (valid range >=0, -1 means no collocation)
#         'swath_index_y': 1-D array of y indices for collocated swath pixels (valid range >=0, -1 means no collocation),
#         'track_index_x': 1-D array of x indices for collocated track pixels (valid range >=0, -1 means no collocation)
#         'swath_track_distance': 1-D array of distances between collocated swath and track pixels (valid range >=0, -9999.99 means no collocation)
#         'swath_track_time_difference': 1-D array of time interval between collocated swath and track pixels 
#                                        (>0 means swath observations are made before track pixels, <0 otherwise, -9999.99 means no collocation)
# usage: overlap_flag = find_overlap(calipso_timerange,viirs_timeranges)

def track_swath_collocation(track_lat='',track_lon='',track_time='',
                            swath_lat='',swath_lon='',swath_time='',swath_resolution='',
                            maximum_distance='',maximum_interval=''):

    #step 1: define search start/end datetimes
    search_sdt = swath_time - datetime.timedelta(minutes=maximum_interval)
    search_edt = swath_time + datetime.timedelta(minutes=maximum_interval)

    n_profile = len(track_lat)

    swath_ind_x = np.full(n_profile,-1,dtype='i')
    swath_ind_y = np.full(n_profile,-1,dtype='i')
    swath_track_dist = np.full(n_profile,-9999.99)
    swath_track_tdif = np.full(n_profile,-9999.99)
    track_ind_x = np.full(n_profile,-1,dtype='i')

    #step 2: find track profiles within the search range
    profile_index = np.where( (track_time < search_edt) &
                              (track_time > search_sdt) )[0]

    if (len(profile_index) == 0):
        return {'swath_index_x':swath_ind_x, 'swath_index_y':swath_ind_y,
                'track_index_x':track_ind_x, 'swath_track_distance':swath_track_dist,
                'swath_track_time_difference':swath_track_tdif}

    lon_sub = track_lon[profile_index]
    lat_sub = track_lat[profile_index]

    #collocation method 1:
    dist = np.zeros
    swath_x = swath_lon.shape[0]
    swath_y = swath_lon.shape[1]

    dist_threshold = 200 #kilometers
    step_x = int ((dist_threshold / swath_resolution) / 3)
    step_y = int ((dist_threshold / swath_resolution) / 3)
    step_x = min(max(step_x,1), swath_x)
    step_y = min(max(step_y,1), swath_y)

#    step_x = max(int(swath_x/50),1)
#    step_y = max(int(swath_y/50),1)

    distances = sg.targets_distance(lat_sub,lon_sub,swath_lat[::step_x,::step_y],swath_lon[::step_x,::step_y])

    if (distances.min() >= dist_threshold):
        return {'swath_index_x':swath_ind_x, 'swath_index_y':swath_ind_y,
                'track_index_x':track_ind_x, 'swath_track_distance':swath_track_dist,
                'swath_track_time_difference':swath_track_tdif}

    for i_profile in range(0,len(profile_index)):
        this_dist = distances[:,:,i_profile]
        if (this_dist.min() >= dist_threshold):
            continue
        min_ind = np.unravel_index(this_dist.argmin(), this_dist.shape)

        search_s1 = max(int(min_ind[0] * step_x - step_x/2 - 5), 0)
        search_e1 = min(int(min_ind[0] * step_x + step_x/2 + 5), swath_lat.shape[0])

        search_s2 = max(int(min_ind[1] * step_y - step_y/2 - 5), 0)
        search_e2 = min(int(min_ind[1] * step_y + step_y/2 + 5), swath_lat.shape[1])

        refine_dist = sg.target_distance(lat_sub[i_profile],lon_sub[i_profile],
                                         swath_lat[search_s1:search_e1,search_s2:search_e2],
                                         swath_lon[search_s1:search_e1,search_s2:search_e2])

        if (refine_dist.min() >= maximum_distance):
            continue

        refine_ind = np.unravel_index(refine_dist.argmin(), refine_dist.shape)
        swath_ind_x[profile_index[i_profile]] = refine_ind[0] + search_s1
        swath_ind_y[profile_index[i_profile]] = refine_ind[1] + search_s2
        swath_track_dist[profile_index[i_profile]] = refine_dist.min()
        swath_track_tdif[profile_index[i_profile]] = (track_time[profile_index[i_profile]] - swath_time).total_seconds()/60.
        track_ind_x[profile_index[i_profile]] = profile_index[i_profile]

    uncollocated_index = np.where(track_ind_x<0)
    if (len(uncollocated_index[0])>0):
        swath_ind_x[uncollocated_index] = -1
        swath_ind_y[uncollocated_index] = -1
        swath_track_dist[uncollocated_index] = -9999.99
        swath_track_tdif[uncollocated_index] = -9999.99
    
    return {'swath_index_x':swath_ind_x, 'swath_index_y':swath_ind_y,
            'track_index_x':track_ind_x, 'swath_track_distance':swath_track_dist,
            'swath_track_time_difference':swath_track_tdif}