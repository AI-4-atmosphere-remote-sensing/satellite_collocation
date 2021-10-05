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

# function name: calculate_solar_geometry
# purpose: Calculate solar zenith angle and azimuthal angle
# input: timeflag
    #timeflag format: YYYYDDDHHMM
    #YYYY: year (e.g. 2018)
    #DDD:  Day of the year (e.g., 243)
    #HH:   Hour (0-23)
    #MM:   Minute (0-59)
# input: lat, array of latitude in degree
# input: lon, array of longitude in degree
# lat and lon must have the same dimensions
# output: SZA: solar zenith angle in degree (0~180)
# output: SAA: solar azimuthal angle in degree (-180~180)

# usage: solar_angles = calculate_solar_geometry(timeflag='20182250030',lat=np.arange(10),lon=np.arange(10))

def calculate_solar_geometry(timeflag='',lat='',lon=''):

    year= int(timeflag[0:4])
    doy = int(timeflag[4:7])
    hour= int(timeflag[7:9])
    minute=int(timeflag[9:11])
    
    timefrac = hour*1.0+minute/60.0
    
    #calculate solar angles
    tsm = timefrac + lon/15.0
    lonr = lon*pi/180.0
    latr = lat*pi/180.0
    
    a1 = (1.00554*doy-6.28306) * pi/180.0
    a2 = (1.93946*doy + 23.35089) * pi/180.0
    et = -7.67825*sin(a1) - 10.09176*sin(a2)
    
    tsv = tsm + et/60.0 - 12.0
    
    ah = tsv*15.0*pi/180.0
    
    a3 = (0.9683*doy - 78.00878)*pi/180.0
    delta = 23.4856 * sin(a3) *pi/180.0
    
    cos_delta = cos(delta)
    sin_delta = sin(delta)
    cos_ah = np.cos(ah)
    sin_latr = np.sin(latr)
    cos_latr = np.cos(latr)
    amuzero = sin_latr * sin_delta + cos_latr*cos_delta*cos_ah
    
    elev = np.arcsin(amuzero)
    cos_elev = np.cos(elev)
    
    az = cos_delta * np.sin(ah) / cos_elev
    caz = ( -cos_latr*sin_delta + sin_latr*cos_delta*cos_ah ) / cos_elev
    
    az[az>=1.0] = 1.0
    az[az<=-1.0] = -1.0
    azim = np.arcsin(az)
    
    index1 = np.where( caz<= 0 )
    azim[index1] = pi - azim[index1]
    index2 = np.where( (caz>0) & (az<=0) )
    azim[index2] = 2.*pi+azim[index2]
    
    azim = azim + pi

    index3 = np.where( azim>(pi*2.) )
    azim[index3] = azim[index3] - pi*2.
    
    elev = elev / (pi/180.0)
    sza  = 90.0 - elev
    saa  = azim / (pi/180.0)
    
    index4 = np.where( saa >= 180.0 )
    saa[index4] = saa[index4] - 360.0
    
    return {'SZA':sza, 'SAA':saa}
