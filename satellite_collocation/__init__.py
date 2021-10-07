"""Top-level package for satellite collocation code."""

__author__ = """Chenxi Wang"""
__email__ = 'chenxi@umbc.edu'
__version__ = '0.1.0'


from . import *

# if somebody does "from Sample import *", this is what they will
# be able to access:
__all__ = [
    'general_collocation'
    ,'instrument_reader'
    ,'satellite_geo'
]
