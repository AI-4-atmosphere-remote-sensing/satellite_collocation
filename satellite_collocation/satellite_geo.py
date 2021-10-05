import numpy as np
from math import *

def target_distance(target_lat, target_lon, granule_lat, granule_lon):
    # approximate radius of earth in km
    earth_radius = 6373.0

    shape = granule_lat.shape
    n_element = granule_lat.size

    locs_1 = np.deg2rad([[target_lat,target_lon]])

    granule_locs = np.zeros([n_element,2])
    granule_locs[:,0] = np.reshape(granule_lat,(n_element))
    granule_locs[:,1] = np.reshape(granule_lon,(n_element))

    locs_2 = np.deg2rad(granule_locs)

    lat_dif = (locs_1[:,0][:,None]/2 - locs_2[:,0]/2)
    lon_dif = (locs_1[:,1][:,None]/2 - locs_2[:,1]/2)

    np.sin(lat_dif, out=lat_dif)
    np.sin(lon_dif, out=lon_dif)

    np.power(lat_dif, 2, out=lat_dif)
    np.power(lon_dif, 2, out=lon_dif)

    lon_dif *= ( np.cos(locs_1[:,0])[:,None] * np.cos(locs_2[:,0]) )
    lon_dif += lat_dif
    lon_dif[lon_dif>1.0] = 1.0

    np.arctan2(np.power(lon_dif,.5), np.power(1-lon_dif,.5), out = lon_dif)
    lon_dif *= ( 2 * earth_radius )

    distance = np.reshape(lon_dif,shape)

    return distance
  
  
def targets_distance(target_lats, target_lons, granule_lat, granule_lon):

    # approximate radius of earth in km
    earth_radius = 6373.0

    shape = granule_lat.shape
    n_element = granule_lat.size
    n_target = len(target_lats)

    granule_locs = np.zeros([n_element,2])
    granule_locs[:,0] = np.reshape(granule_lat,(n_element))
    granule_locs[:,1] = np.reshape(granule_lon,(n_element))

    locs_1 = np.zeros([n_target,2])
    locs_1[:,0:1] = np.deg2rad(target_lats)
    locs_1[:,1:2] = np.deg2rad(target_lons)

    distance = np.zeros([shape[0], shape[1], n_target])
    locs_2 = np.deg2rad(granule_locs)

    lat_dif = (locs_1[:,0][:,None]/2 - locs_2[:,0]/2)
    lon_dif = (locs_1[:,1][:,None]/2 - locs_2[:,1]/2)

    np.sin(lat_dif, out=lat_dif)
    np.sin(lon_dif, out=lon_dif)

    np.power(lat_dif, 2, out=lat_dif)
    np.power(lon_dif, 2, out=lon_dif)

    lon_dif *= ( np.cos(locs_1[:,0])[:,None] * np.cos(locs_2[:,0]) )
    lon_dif += lat_dif
    lon_dif[lon_dif>1.0] = 1.0

    np.arctan2(np.power(lon_dif,.5), np.power(1-lon_dif,.5), out = lon_dif)
    lon_dif *= ( 2 * earth_radius )

    distance = np.reshape(np.transpose(lon_dif), (shape[0],shape[1],n_target) )

    return distance


def calculate_geos_geometry(timeflag='',lat='',lon=''):
    
    #timeflag format: YYYYDDDHHMM
    #YYYY: year (e.g. 2018)
    #DDD:  Day of the year (e.g., 243)
    #HH:   Hour (0-23)
    #MM:   Minute (0-59)
    year= int(timeflag[0:4])
    doy = int(timeflag[4:7])
    hour= int(timeflag[7:9])
    minute=int(timeflag[9:11])
    
    return
