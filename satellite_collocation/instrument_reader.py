#Instrument Reader
#This package includes necessary functions for loading data from different instruments

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

# function name: get_modis_viirs_timerange
# purpose: Get the Date Time Range of a set of MODIS or VIIRS file names
# input: datetime_range = {FILENAMES}
# output: list of Datetime Ranges
# usage: modis_datetimeranges = get_modis_viirs_timerange(list_of_modis_filenames)
#.       viirs_datetimeranges = get_modis_viirs_timerange(list_of_viirs_filenames)

def get_modis_viirs_timerange(mvfiles):

    n_file = len(mvfiles)
    timerange = []

    for i, mvfile in enumerate(mvfiles):
        mvname = os.path.basename(mvfile)
        pos = mvname.find('.A')
        timeflag = mvname[pos+2:pos+14]
        if (mvname[0] == 'M'):
            granule = 4.9
        if (mvname[0] == 'V'):
            granule = 5.9

        dt_start = datetime.datetime.strptime(timeflag,'%Y%j.%H%M')
        dt_end = dt_start + datetime.timedelta(minutes=granule)
        timerange.append( DateTimeRange(dt_start,dt_end) )

    return timerange

# function name: get_cris_timerange
# purpose: Get the Date Time Range of a set of CrIS file names
# input: datetime_range = {FILENAMES}
# output: list of Datetime Ranges
# usage: cris_datetimeranges = get_cris_timerange(list_of_cris_filenames)

def get_cris_timerange(crisfiles):

    n_file = len(crisfiles)
    timerange = []

    for i, crisfile in enumerate(crisfiles):
        crisname = os.path.basename(crisfile)
        pos = crisname.find('CRIS.')
        timeflag = crisname[pos+5:pos+18]
        granule = 5.9
        dt_start = datetime.datetime.strptime(timeflag,'%Y%m%dT%H%M')
        dt_end = dt_start + datetime.timedelta(minutes=granule)
        timerange.append( DateTimeRange(dt_start,dt_end) )

    return timerange 


  
# function name: load_abi_geoloc
# purpose: Read 2D Latitude/Longitude from GOES-R ABI L1 file
# input: abi_l1_file = {FILENAME}
# output: Dictionary 'Longitude', 'Latitude', and 'Space_Mask' masked 2D array
# usage: abi_l1_geo = load_abi_geoloc(abi_file='...')

def load_abi_geoloc(abi_file='',params={}):
    
    #ABI Height:
    abi_height = 42164.16 #in kilometer
    h = abi_height
    r_eq = 6378.1370 #km   semi-major axis
    r_pol= 6356.7523 #km   semi-minor axis
    d = h*h - r_eq*r_eq
    f = (1.0/298.257222101)
    fp = (1.0/((1.0-f)*(1.0-f)))
    
    #read constant
    fid = Dataset(abi_file,'r')
    x = fid.variables['x']
    y = fid.variables['y']
    lamda   = x[:]
    theta   = y[:]
    proj = fid.variables['goes_imager_projection']
    lon0 = getattr(proj,'longitude_of_projection_origin')
    lat0 = getattr(proj,'latitude_of_projection_origin')
    
    fid.close()
    
    #calculate lat/lon 
    nx = len(lamda)
    ny = len(theta)
    
    lat = np.full([ny,nx],fill_value=np.nan,dtype=np.float32)
    lon = np.full([ny,nx],fill_value=np.nan,dtype=np.float32)
    c1  = np.full([ny,nx],fill_value=np.nan,dtype=np.float32)
    c2  = np.full([ny,nx],fill_value=np.nan,dtype=np.float32)
    sd  = np.full([ny,nx],fill_value=np.nan,dtype=np.float32)
    sn  = np.full([ny,nx],fill_value=np.nan,dtype=np.float32)
    s1  = np.full([ny,nx],fill_value=np.nan,dtype=np.float32)
    s2  = np.full([ny,nx],fill_value=np.nan,dtype=np.float32)
    s3  = np.full([ny,nx],fill_value=np.nan,dtype=np.float32)
    sxy = np.full([ny,nx],fill_value=np.nan,dtype=np.float32)
    
    lamda_geos = np.full([ny,nx],fill_value=np.nan,dtype=np.float32)
    theta_geos = np.full([ny,nx],fill_value=np.nan,dtype=np.float32)
    space_mask = np.zeros([ny,nx],dtype=np.int8)
    
    for j in range(ny):
        lamda_geos[j,:] = np.arctan( np.tan(lamda)/np.cos(theta[j]) )
        theta_geos[j,:] = np.arcsin( np.sin(theta[j])*np.cos(lamda) )

    c1 = (h * np.cos(lamda_geos) * np.cos(theta_geos)) * (h * np.cos(lamda_geos) * np.cos(theta_geos))
    c2 = (np.cos(theta_geos) * np.cos(theta_geos) + fp * np.sin(theta_geos) * np.sin(theta_geos)) * d
    valid_ind = np.where(c1>=c2)
    
    sd[valid_ind] = np.sqrt(c1[valid_ind]-c2[valid_ind])
    cosx = np.cos(lamda_geos[valid_ind])
    cosy = np.cos(theta_geos[valid_ind])
    sinx = np.sin(lamda_geos[valid_ind])
    siny = np.sin(theta_geos[valid_ind])
    
    sn[valid_ind] = ( (h * cosx * cosy - sd[valid_ind]) /
                      (cosy * cosy + fp * siny * siny) )
    s1[valid_ind] = h - sn[valid_ind] * cosx * cosy
    s2[valid_ind] = sn[valid_ind] * sinx * cosy
    s3[valid_ind] = -1.0 * sn[valid_ind] * siny
    
    sxy[valid_ind] = np.sqrt(s1[valid_ind]*s1[valid_ind] + s2[valid_ind]*s2[valid_ind])
    lon[valid_ind] = np.arctan(s2[valid_ind]/s1[valid_ind]) + lon0 * pi/180.0
    lat[valid_ind] = np.arctan(-1.0*fp*(s3[valid_ind]/sxy[valid_ind]))
    
    lon[valid_ind] = lon[valid_ind] * 180.0/pi
    lat[valid_ind] = lat[valid_ind] * 180.0/pi
    
    lon[lon<-180.0] += 360.0
    lon[lon >180.0] += -360.0
    
    valid = np.where( (abs(lat)<=90) & (abs(lon)<=180) )
    space_mask[valid] = 1
    lat[space_mask==0] = np.nan
    lon[space_mask==0] = np.nan
    
    return {'Latitude':lat,'Longitude':lon,'Space_Mask':space_mask}

# function name: load_caliop_clayer1km_geoloc
# purpose: Read 1D Latitude/Longitude/UTC_Time from CALIOP Level-2 Cloud Layer 1km Product
# input: cal_1km_file = {FILENAME}
# output: Dictionary 'Longitude', 'Latitude', 'UTC_Time'
# usage: caliop_clayer1km_geo = load_caliop_clayer1km_geo(cal_1km_file='...')

def load_caliop_clayer1km_geoloc(cal_1km_file='',params={}):
  
    try:
        cal_1km_id = SD(cal_1km_file,SDC.READ)
        cal_lon = cal_1km_id.select('Longitude').get()
        cal_lat = cal_1km_id.select('Latitude').get()
        cal_igbp= np.squeeze(cal_1km_id.select('IGBP_Surface_Type').get())
        cal_snic= np.squeeze(cal_1km_id.select('Snow_Ice_Surface_Type').get())
        cal_utc = cal_1km_id.select('Profile_UTC_Time').get()
        cal_1km_id.end()

        cal_snic = cal_snic.astype(np.int16)
        cstart_date = int(cal_utc[0] + 20000000.)
        cend_date = int(cal_utc[-1]+ 20000000.)
        cstart_time = (cal_utc[0] - cstart_date + 20000000.) * 24. * 3600.
        cend_time = (cal_utc[-1] - cend_date + 20000000.) * 24. * 3600.
        cstart_dt = datetime.datetime.strptime(str(cstart_date),'%Y%m%d') + datetime.timedelta(seconds=cstart_time[0])
        cend_dt = datetime.datetime.strptime(str(cend_date),'%Y%m%d') + datetime.timedelta(seconds=cend_time[0])
        cal_range1 = cstart_dt.strftime("%Y-%m-%dT%H:%M:%S")
        cal_range2 = cend_dt.strftime("%Y-%m-%dT%H:%M:%S")
        cal_timerange = DateTimeRange(cal_range1, cal_range2)
        #print (cal_timerange)
        n_profile = cal_lon.shape[0]
        prof_s = 0
        prof_e = n_profile
        profile_dts = list()
        profile_deltas = (cal_utc - cal_utc[0]) * 3600. * 24.
        for i_profile in range(0,n_profile):
            profile_dt = cstart_dt + datetime.timedelta(seconds=int(profile_deltas[i_profile]))
            profile_dts.append(profile_dt)

    except:
        cal_lon = np.full(1,-9999.99)
        cal_lat = np.full(1,-9999.99)
        cal_utc = np.full(1,-9999.99)
        cal_igbp= np.full(1,-1)
        cal_snic= np.full(1,-1)
        n_profile = 0
        profile_dts = list()

    return {'Longitude':cal_lon, 'Latitude':cal_lat, 'IGBP_Type':cal_igbp, 'Snow_Ice_Type':cal_snic, 'Profile_Datetime':np.asarray(profile_dts)}

  
# function name: load_viirs_vnp03_geoloc
# purpose: Read 2D Latitude/Longitude from VIIRS SNPP L1 Product
# input: vnp03_file = {FILENAME}
# output: Dictionary 'Longitude', 'Latitude', masked 2D array, and Granule starting, middle, and ending times
# usage: vnp03_geo = load_viirs_vnp03_geo(vnp03_file='...')

def load_viirs_vnp03_geoloc(vnp03_file='',params={}):

    vnp03_filename = os.path.basename(vnp03_file)
    vnp03_timeflag = vnp03_filename[vnp03_filename.find('.A')+2:vnp03_filename.find('.A')+14]
    sdt = datetime.datetime.strptime(vnp03_timeflag,'%Y%j.%H%M')
    mdt = sdt + datetime.timedelta(minutes=3, seconds=0)
    edt = sdt + datetime.timedelta(minutes=5, seconds=59)
    try:
        viirs_vnp03_id = Dataset(vnp03_file,'r')
        lat = viirs_vnp03_id['geolocation_data/latitude'][:]
        lon = viirs_vnp03_id['geolocation_data/longitude'][:]
        lsm = viirs_vnp03_id['geolocation_data/land_water_mask'][:]
    except:
        lat = -9999.99
        lon = -9999.99
        lsm = -1
    return {'Longitude':lon, 'Latitude':lat, 'LandSeaMask':lsm, 'Datetime':[sdt,mdt,edt]}
  
 
# function name: load_modis_mod03_geoloc
# purpose: Read 2D Latitude/Longitude from MODIS L1 MO(Y)D03 Product
# input: mod03_file = {FILENAME}
# output: Dictionary 'Longitude', 'Latitude', masked 2D array, and Granule starting, middle, and ending times
# usage: mod03_geo = load_modis_mod03_geo(mod03_file='...')

def load_modis_mod03_geoloc(mod03_file='',params={}):

    mod03_filename = os.path.basename(mod03_file)
    mod03_timeflag = mod03_filename[mod03_filename.find('.A')+2:mod03_filename.find('.A')+14]
    sdt = datetime.datetime.strptime(mod03_timeflag,'%Y%j.%H%M')
    mdt = sdt + datetime.timedelta(minutes=2, seconds=30)
    edt = sdt + datetime.timedelta(minutes=4, seconds=59)
    try:
        modis_mod03_id = SD(mod03_file,SDC.READ)
        lat = modis_mod03_id.select('Latitude').get()
        lon = modis_mod03_id.select('Longitude').get()
        lsm = modis_mod03_id.select('Land/SeaMask').get()
    except:
        lat = -9999.99
        lon = -9999.99
        lsm = -1
    return {'Longitude':lon, 'Latitude':lat, 'LandSeaMask':lsm, 'Datetime':[sdt,mdt,edt]}
  
# function name: load_modis_mod02_reflectance_1km
# purpose: Read 2D uncorrected reflectance (raw data) from MODIS L1 MO(Y)D02 Product
# input: mod02_file = {FILENAME}
# output: Dictionary 'R??_uncorrectted'
# usage: mod02_reflancetance = load_modis_mod02_reflance(mod02_file='...')
# note: bi-directional reflectance = uncorrected reflectance / cos(solar zenith angle)

def load_modis_mod02_reflectance_1km(m02_file='',band='',params={}):

    m02_id = SD(m02_file,SDC.READ)

    r250_id = m02_id.select('EV_250_Aggr1km_RefSB')
    r250_scale = r250_id.attributes()['reflectance_scales']
    r250_offset= r250_id.attributes()['reflectance_offsets']
    n250 = r250_id.get()
    r250 = np.asarray(n250,dtype='f4')
    n_band = n250.shape[0]
    for i_band in range(n_band):
        r250[i_band,:,:] = (n250[i_band,:,:] + r250_offset[i_band]) * r250_scale[i_band]
    index = np.where(n250>32767)
    r250[index[0],index[1],index[2]] = -9999.99
    r01 = np.squeeze(r250[0,:,:])
    r02 = np.squeeze(r250[1,:,:])

    r500_id = m02_id.select('EV_500_Aggr1km_RefSB')
    r500_scale = r500_id.attributes()['reflectance_scales']
    r500_offset= r500_id.attributes()['reflectance_offsets']
    n500 = r500_id.get()
    r500 = np.asarray(n500,dtype='f4')
    n_band = n500.shape[0]
    for i_band in range(n_band):
        r500[i_band,:,:] = (n500[i_band,:,:] + r500_offset[i_band]) * r500_scale[i_band]
    index = np.where(n500>32767)
    r500[index[0],index[1],index[2]] = -9999.99
    r03 = np.squeeze(r500[0,:,:])
    r04 = np.squeeze(r500[1,:,:])
    r05 = np.squeeze(r500[2,:,:])
    r06 = np.squeeze(r500[3,:,:])
    r07 = np.squeeze(r500[4,:,:])
    
    r1km_id = m02_id.select('EV_1KM_RefSB')
    r1km_scale = r1km_id.attributes()['reflectance_scales']
    r1km_offset= r1km_id.attributes()['reflectance_offsets']

    n1km = r1km_id.get()
    r1km = np.asarray(n1km,dtype='f4')
    n_band = n1km.shape[0]
    for i_band in range(n_band):
        r1km[i_band,:,:] = (n1km[i_band,:,:] + r1km_offset[i_band]) * r1km_scale[i_band]
    index = np.where(n1km>32767)
    r1km[index[0],index[1],index[2]] = -9999.99
    r08 = np.squeeze(r1km[0,:,:])
    r09 = np.squeeze(r1km[1,:,:])
    r10 = np.squeeze(r1km[2,:,:])
    r11 = np.squeeze(r1km[3,:,:])
    r12 = np.squeeze(r1km[4,:,:])
    r13l = np.squeeze(r1km[5,:,:])
    r13h = np.squeeze(r1km[6,:,:])
    r14l = np.squeeze(r1km[7,:,:])
    r14h = np.squeeze(r1km[8,:,:])
    r15 = np.squeeze(r1km[9,:,:])
    r16 = np.squeeze(r1km[10,:,:])
    r17 = np.squeeze(r1km[11,:,:])
    r18 = np.squeeze(r1km[12,:,:])
    r19 = np.squeeze(r1km[13,:,:])
    r26 = np.squeeze(r1km[14,:,:])
    
    m02_id.end()
    
    return {'R01_Uncorrected':r01, 'R02_Uncorrected':r02,
            'R03_Uncorrected':r03, 'R04_Uncorrected':r04,
            'R05_Uncorrected':r05, 'R06_Uncorrected':r06, 'R07_Uncorrected':r07,
            'R08_Uncorrected':r08, 'R09_Uncorrected':r09,
            'R10_Uncorrected':r10, 'R11_Uncorrected':r11, 'R12_Uncorrected':r12,
            'R13l_Uncorrected':r13l, 'R13h_Uncorrected':r13h, 'R14l_Uncorrected':r14l, 'R14h_Uncorrected':r14h,
            'R15_Uncorrected':r15, 'R16_Uncorrected':r16, 'R17_Uncorrected':r17, 'R18_Uncorrected':r18,
            'R19_Uncorrected':r19, 'R26_Uncorrected':r26 }
 
# function name: load_modis_mod02_emission_1km
# purpose: Read 2D radiance (IR) from MODIS L1 MO(Y)D02 Product
# input: mod02_file = {FILENAME}
# output: Dictionary 'Radxx'
# usage: mod02_emission = load_modis_mod02_emission_1km(mod02_file='...')

def load_modis_mod02_emission_1km(m02_file='',params={}):

    m02_id = SD(m02_file,SDC.READ)
    e1km_id = m02_id.select('EV_1KM_Emissive')
    e1km_scale = e1km_id.attributes()['radiance_scales']
    e1km_offset= e1km_id.attributes()['radiance_offsets']

    n1km = e1km_id.get()
    e1km = np.asarray(n1km,dtype='f4')
    n_band = n1km.shape[0]
    for i_band in range(n_band):
        e1km[i_band,:,:] = (e1km[i_band,:,:] - e1km_offset[i_band]) * e1km_scale[i_band]
    index = np.where(n1km>32767)
    e1km[index[0],index[1],index[2]] = -9999.99
    e20 = np.squeeze(e1km[0,:,:])
    e21 = np.squeeze(e1km[1,:,:])
    e22 = np.squeeze(e1km[2,:,:])
    e23 = np.squeeze(e1km[3,:,:])
    e24 = np.squeeze(e1km[4,:,:])
    e25 = np.squeeze(e1km[5,:,:])
    e27 = np.squeeze(e1km[6,:,:])
    e28 = np.squeeze(e1km[7,:,:])
    e29 = np.squeeze(e1km[8,:,:])
    e30 = np.squeeze(e1km[9,:,:])
    e31 = np.squeeze(e1km[10,:,:])
    e32 = np.squeeze(e1km[11,:,:])
    e33 = np.squeeze(e1km[12,:,:])
    e34 = np.squeeze(e1km[13,:,:])
    e35 = np.squeeze(e1km[14,:,:])
    e36 = np.squeeze(e1km[15,:,:])

    m02_id.end()

    return {'Rad20':e20, 'Rad21':e21,
            'Rad22':e22, 'Rad23':e23,
            'Rad24':e24, 'Rad25':e25,
            'Rad27':e27, 'Rad28':e28,
            'Rad29':e29, 'Rad30':e30,
            'Rad31':e31, 'Rad32':e32,
            'Rad33':e33, 'Rad34':e34,
            'Rad35':e35, 'Rad36':e36}


# function name: load_collocate_viirs_dataset
# purpose: Read 2D VIIRS dataset(s) into 1D array(s)
# input: viirs_file = {FILENAME}
# input: viirs_along = {1D array of VIIRS along track indices, index starts from 0}
# input: viirs_cross = {1D array of VIIRS across track indices, index starts from 0}
# input: selected_datasets = {Full name of selected 2D datasets}
# output: 1D array(s) of selected datasets
# note: viirs_along and viirs_cross must have the same number of elements
# usage: viirs_datasets = load_collocate_viirs_dataset(viirs_file='VNP02MOD.A2013050.2306.001.2017291120825.nc',
#                                                      viirs_along=[0,3,6,100,300],viirs_along=[0,150,633,700,2000],
#                                                      selected_dataset=['observation_data/M02','observation_data/M05'])  
  
def load_collocate_viirs_dataset(viirs_file='',viirs_along='',viirs_cross='',selected_datasets=''):

    ind = np.where(viirs_along>=0)
    if (len(ind)<=0):
        return
    fid = Dataset(viirs_file)

    save_data = {}
    for selected_dataset in selected_datasets:
        dataset = fid[selected_dataset][:]
        save_dataset = dataset[viirs_along[ind],viirs_cross[ind]]
        #sid.create_dataset(selected_dataset,data=save_dataset)

        save_data[selected_dataset] = save_dataset
    fid.close()

    return save_data  
  
# function name: load_collocate_caliop_dataset
# purpose: Read CALIPSO dataset(s)
# input: calipso_file = {FILENAME} 
# input: calipso_index = {1D array of CALIPSO profile indices, index starts from 0}
# input: selected_datasets = {Full name of selected CALIPSO datasets}
# output: 1D array(s) of selected datasets
# usage: caliop_datasets = load_collocate_caliop_dataset(calipso_file='CAL_LID_L2_01kmCLay-Standard-V4-10.2017-01-01T05-38-12ZN.hdf',
#                                                        calipso_index=[0,3,6,100,300],
#                                                        selected_dataset=['Longitude','Latitude',
#                                                        'IGBP_Surface_Type','Snow_Ice_Surface_Type',
#                                                        'Number_Layers_Found','Feature_Classification_Flags'])  


def load_collocate_caliop_dataset(calipso_file='',calipso_index='',selected_datasets=''):

    ind = np.where(calipso_index>=0)
    if (len(ind)<=0):
        return

    fid = SD(calipso_file,SDC.READ)

    save_data = {}

    for selected_dataset in selected_datasets:
        print (selected_dataset)
        dataset = np.squeeze(fid.select(selected_dataset).get())
        n_dim = len(dataset.shape)
        print ('Dimension',n_dim)
        dims = dataset.shape
        if (n_dim==1):
            save_dataset = dataset[calipso_index[ind]]
        if (n_dim==2):
            save_dataset = dataset[calipso_index[ind],:]
        if (n_dim==3):
            save_dataset = dataset[calipso_index[ind],:,:]

        save_data[selected_dataset] = save_dataset

    fid.end()

    return save_data
