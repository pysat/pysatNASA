#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3986131
#
# DISTRIBUTION STATEMENT A: Approved for public release. Distribution is
# unlimited.
# ----------------------------------------------------------------------------
"""Module for the MAVEN magnetometer.

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
inst_id
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
tags = {'': 'Level 2 magnetometer data'}
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
download_tags = {'': {'': 'MVN_MAG_L2-SUNSTATE-1SEC'}}
download = functools.partial(cdw.cdas_download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.cdas_list_remote_files,
                                      supported_tags=download_tags)

# Set the load routine
load = functools.partial(cdw.load, epoch_name='epoch',
                         pandas_format=pandas_format, use_cdflib=True)
