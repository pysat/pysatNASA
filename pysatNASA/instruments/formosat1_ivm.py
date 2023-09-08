# -*- coding: utf-8 -*-
"""Module for the Formosat-1 IVM instrument.

Supports the Ion Velocity Meter (IVM) onboard the Formosat-1 (formerly
ROCSAT-1) mission. Downloads data from the NASA Coordinated Data Analysis
Web (CDAWeb).

Properties
----------
platform
    'formosat1'
name
    'ivm'
tag
    None
inst_id
    None supported

Warnings
--------
- Currently no cleaning routine.

"""

import datetime as dt
import functools

from pysat.instruments.methods import general as mm_gen

from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import formosat as mm_formosat
from pysatNASA.instruments.methods import general as mm_nasa

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'formosat1'
name = 'ivm'
tags = {'': ''}
inst_ids = {'': ['']}

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'': dt.datetime(2002, 1, 1)}}

# ----------------------------------------------------------------------------
# Instrument methods

init = functools.partial(mm_nasa.init, module=mm_formosat, name=name)


# Use default clean
clean = mm_nasa.clean

# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
fname = 'rs_k0_ipei_{year:04d}{month:02d}{day:02d}_v{version:02d}.cdf'
supported_tags = {'': {'': fname}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the load routine
load = cdw.load

# Set the download routine
download_tags = {'': {'': 'RS_K0_IPEI'}}
download = functools.partial(cdw.cdas_download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.cdas_list_remote_files,
                                      supported_tags=download_tags)
