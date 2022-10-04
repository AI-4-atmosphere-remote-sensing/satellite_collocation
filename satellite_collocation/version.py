#version control
version = "1.0"
project_name = "Developing Passive Satellite Cloud Remote Sensing Algorithms Using Collocated Observations, Numerical Simulation and Deep Learning"
task_name = "A convenient and flexible satellite data spatial-temporal collocation system"
description = """This is a general python-based package that allows collocation of data from arbitrary sensors and/or platforms based on
user requirement. The general package includes three major modules, namely instrument reader and unit conversion, geometry
calculation, and data collocation. The instrument reader and unit conversion module provides useful functions that read
geolocation and L1/L2 data from various instruments, such as MODIS, VIIRS, CALIOP, and CloudSat. It also includes methods
that allow convenient unit conversion (e.g., radiance to brightness temperature, radiance to reflectance). The geometry module
consists of functions that efficiently calculate distances between multiple points, and/or find points within given large footprints.
Given maximum spatial distance and time interval, the collocation module automatically records indices from two instruments
that meet the criteria. In general, the package can be applied to instruments on different platforms with different orbits and
spatial resolutions. Users are able to add more reader functions for new instruments in the future."""
project_pi = "Jianwu Wang"
project_cois = "Chenxi Wang, Sanjay Purushotham, Zhibo Zhang, and Kerry Meyer"
software_author = "Chenxi Wang and Jianwu Wang"
contact1 = "jianwu@umbc.edu"
contact2 = "chenxi.wang@nasa.gov"