# -*- coding: utf-8 -*-
"""Module for the MAVEN mag instrument.

Supports the Magnetometer (MAG) onboard the Mars Atmosphere
and Volatile Evolution (MAVEN) satellite.
Accesses local data in CDF format.
Downloads from CDAWeb.

Properties
----------
platform
    'maven'
name
    'mag'
tag
    None supported

Warnings
--------

- Only supports level-2 sunstate 1 second data.

Examples
--------
::
    import pysat


    mag = pysat.Instrument(platform='maven', name='mag')
    mag.download(dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 31))
    mag.load(2020, 1, use_header = True)

"""

import datetime as dt
import functools

from pysat.instruments.methods import general as mm_gen
from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import general as mm_nasa
from pysatNASA.instruments.methods import maven as mm_mvn

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'maven'
name = 'mag'
tags = {'': 'l2'}
inst_ids = {'': ['']}

pandas_format = False
# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'': dt.datetime(2020, 1, 1)}}

# ----------------------------------------------------------------------------
# Instrument methods

# Use standard init routine
init = functools.partial(mm_nasa.init, module=mm_mvn, name=name)


# Use default clean
clean = mm_nasa.clean


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the CDAWeb and pysat methods

# Set the list_files routine
fname = ''.join(('mvn_mag_l2-sunstate-1sec_{year:04d}{month:02d}{day:02d}_',
                 'v{version:02d}_r{revision:02d}.cdf'))
supported_tags = {'': {'': fname}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)
# Set the download routine
basic_tag = {'remote_dir': ''.join(('/pub/data/maven/mag/l2/sunstate-1sec',
                                    '/cdfs/{year:04d}/{month:02d}')),
             'fname': fname}
download_tags = {'': {'': basic_tag}}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)

# Set the load routine
load = functools.partial(cdw.load, epoch_name='epoch',
                         pandas_format=pandas_format, use_cdflib=True)
