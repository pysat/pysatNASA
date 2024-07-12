#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3986131
#
# DISTRIBUTION STATEMENT A: Approved for public release. Distribution is
# unlimited.
# ----------------------------------------------------------------------------
"""The TIMED SABER instrument.

Supports the Sounding of the Atmosphere using Broadband Emission Radiometry
(SABER) instrument on the Thermosphere Ionosphere Mesosphere Energetics
Dynamics (TIMED) satellite.

Properties
----------
platform : str
    'timed'
name : str
    'saber'
tag : str
    None supported
inst_id : str
    None supported

Note
----
Note on Temperature Errors: https://saber.gats-inc.com/temp_errors.php

SABER "Rules of the Road" for DATA USE
Users of SABER data are asked to respect the following guidelines

  - Mission scientific and model results are open to all.
  - Guest investigators, and other members of the scientific community or
    general public should contact the PI or designated team member early in an
    analysis project to discuss the appropriate use of the data.
  - Users that wish to publish the results derived from SABER data should
    normally offer co-authorship to the PI, Associate PI or designated team
    members. Co-authorship may be declined. Appropriate acknowledgement of
    institutions, personnel, and funding agencies should be given.
  - Users should heed the caveats of SABER team members as to the
    interpretation and limitations of the data. SABER team members may insist
    that such caveats be published, even if co-authorship is declined. Data
    and model version numbers should also be specified.
  - Pre-prints of publications and conference abstracts should be widely
    distributed to interested parties within the mission and related projects.


Warnings
--------
- No cleaning routine

"""

import datetime as dt
import functools

# CDAWeb methods prewritten for pysat
from pysat.instruments.methods import general as mm_gen

from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import general as mm_nasa
from pysatNASA.instruments.methods import timed as mm_timed

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'timed'
name = 'saber'
tags = {'': ''}
inst_ids = {'': ['']}

# let pysat know that data is spread across more than one file
multi_file_day = True

# Set to False to specify using xarray (not using pandas)
# Set to True if data will be returned via a pandas DataFrame
pandas_format = False

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'': dt.datetime(2019, 1, 1)}}
_clean_warn = {inst_id: {tag: mm_nasa.clean_warnings
                         for tag in inst_ids[inst_id]}
               for inst_id in inst_ids.keys()}

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
fname = ''.join(('timed_l2a_saber_{year:04d}{month:02d}{day:02d}',
                 '{hour:02d}{minute:02d}_v{version:02d}-{revision:02d}-',
                 '{cycle:02d}.cdf'))
supported_tags = {'': {'': fname}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the load routine. Note that the time variable associated with
# tpaltitude is renamed to avoid conflict with renaming Epoch.
load = functools.partial(cdw.load, pandas_format=pandas_format,
                         drop_dims='record0',
                         var_translation={'time': 'tp_time'},
                         use_cdflib=True)

# Set the download routine
download_tags = {'': {'': 'TIMED_L2A_SABER'}}
download = functools.partial(cdw.cdas_download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.cdas_list_remote_files,
                                      supported_tags=download_tags)
