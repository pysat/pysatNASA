# -*- coding: utf-8 -*-
"""Supports the SEE instrument on TIMED.

Downloads data from the NASA Coordinated Data
Analysis Web (CDAWeb).

Supports two options for loading that may be
specified at instantiation.

Properties
----------
platform
    'timed'
name
    'see'
tag
    None
inst_id
    None supported

Note
----
- no tag required
- cdflib load routine raises ISTP Compliance Warnings for several variables.
  This is due to how the Epoch is listed in the original files.

Warnings
--------
- Currently no cleaning routine.

"""

import datetime as dt
import functools
import pandas as pds

from pysat.instruments.methods import general as mm_gen

from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import general as mm_nasa
from pysatNASA.instruments.methods import timed as mm_timed

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'timed'
name = 'see'
tags = {'': ''}
inst_ids = {'': [tag for tag in tags.keys()]}
pandas_format = False

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'': dt.datetime(2009, 1, 1)}}

# ----------------------------------------------------------------------------
# Instrument methods

init = functools.partial(mm_nasa.init, module=mm_timed, name=name)

# No cleaning, use standard warning function instead
clean = mm_nasa.clean_warn

# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# TODO(#104): Switch to netCDF4 files once unzip (#103) is supported.

# Set the list_files routine
fname = 'timed_l3a_see_{year:04d}{month:02d}{day:02d}_v{version:02d}.cdf'
supported_tags = {'': {'': fname}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags,
                               file_cadence=pds.DateOffset(months=1))

# Set the load routine
load = functools.partial(cdw.load, file_cadence=pds.DateOffset(months=1),
                         pandas_format=pandas_format, use_cdflib=True)

# Set the download routine
download_tags = {'': {'': 'TIMED_L3A_SEE'}}
download = functools.partial(cdw.cdas_download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.cdas_list_remote_files,
                                      supported_tags=download_tags)
