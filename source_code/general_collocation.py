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



def find_overlap(target_timerange,source_timeranges):

    overlap_flag = np.zeros(len(source_timeranges),dtype=np.int8)
    for i, timerange in enumerate(source_timeranges):
        if (target_timerange.is_intersection(timerange)):
            overlap_flag[i] = 1

    return overlap_flag
