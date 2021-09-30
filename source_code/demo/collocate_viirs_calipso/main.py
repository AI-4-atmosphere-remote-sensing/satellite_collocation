# this is a demo to show how to collocate CALIPSO 1km Cloud Layer L2 product with VIIRS Data

general_lib_path = '/umbc/rs/nasa-access/codes/chenxi_general_code_testing/python/general_lib/'

import sys
sys.path.insert(1,general_lib_path)
import instrument_reader as ir
import general_collocation as gc
import numpy as np
import glob
import os
import h5py
from datetimerange import DateTimeRange

#collocate caliop with viirs
maximum_distance = 5.0  #kilometer
maximum_interval = 15.0 #minute
viirs_resolution = 0.75 #kilometer
