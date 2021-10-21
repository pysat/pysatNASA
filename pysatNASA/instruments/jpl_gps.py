# -*- coding: utf-8 -*-
"""Module for the JPL GPS data products.

References
----------
TBC

Properties
----------
platform
    'jpl'
name
    'gps'
tag
    ['roti']
inst_id
    None supported

Warnings
--------
- The cleaning parameters for the instrument are still under development.

"""

import datetime as dt
import functools

from pysat.instruments.methods import general as mm_gen
from pysat import logger

from pysatNASA.instruments.methods import cdaweb as cdw

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'jpl'
name = 'gps'
tags = {'roti': 'Rate of change in TEC'}
inst_ids = {'': ['roti']}
pandas_format = False
# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'roti': dt.datetime(2013, 1, 1)}}

# ----------------------------------------------------------------------------
# Instrument methods


def init(self):
    """Initialize the Instrument object with instrument specific values.

    Runs once upon instantiation.

    """
    logger.info('')
    self.acknowledgements = 'add acknowledgement'
    self.references = 'Add refs'

    return


def clean(self):
    """Clean JPL GPS data to the specified level.

    Note
    ----
    Supports 'clean', 'dusty', 'dirty'

    """

    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
fname = 'gps_roti15min_jpl_{year:4d}{month:02d}{day:02d}_v{version:02d}.cdf'
supported_tags = {'': {'roti': fname}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the load routine
load = cdw.load

# Set the download routine
basic_tag = {'remote_dir': '/pub/data/gps/roti15min_jpl/{year:4d}/',
             'fname': fname}
download_tags = {'': {'roti': basic_tag}}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)
