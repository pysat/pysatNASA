# -*- coding: utf-8 -*-
"""Module for the Advanced Composition Explorer (ACE) SIS instrument.

References
----------
- Stone, E., Frandsen, A., Mewaldt, R. et al. The Advanced Composition Explorer.
  Space Science Reviews 86, 1–22 (1998). https://doi.org/10.1023/A:1005082526237
- Stone, E., Cohen, C., Cook, W. et al. The Solar Isotope Spectrometer for the
  Advanced Composition Explorer. Space Science Reviews 86, 357–408 (1998).
  https://doi.org/10.1023/A:1005027929871

Properties
----------
platform
    'ace'
name
    'sis_l2'
tag
    None supported
inst_id
    ['h1', 'h2', 'k0']

Note
----
- Level 1 ACE data is maintained at pysatSpaceWeather.

Warnings
--------
- The cleaning parameters for the instrument are still under development.

"""

import datetime as dt
import functools

from pysat.instruments.methods import general as mm_gen

from pysatNASA.instruments.methods import ace as mm_ace
from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import general as mm_nasa

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'ace'
name = 'sis_l2'
tags = {'': ''}
inst_ids = {id: [tag for tag in tags.keys()] for id in ['h1', 'h2', 'k0']}
pandas_format = False

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {id: {'': dt.datetime(2022, 1, 1)} for id in inst_ids.keys()}

# ----------------------------------------------------------------------------
# Instrument methods


# Use standard init routine
init = functools.partial(mm_nasa.init, module=mm_ace, name=name)

# No cleaning, use standard warning function instead
clean = mm_nasa.clean_warn


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
fname = ''.join(('ac_{inst_id:s}_sis_{{year:4d}}{{month:02d}}{{day:02d}}_',
                 'v{{version:02d}}.cdf'))
supported_tags = {id: {'': fname.format(inst_id=id)} for id in inst_ids.keys()}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the load routine
load = functools.partial(cdw.load, pandas_format=pandas_format)

# Set the download routine
remote_dir = '/pub/data/ace/sis/level_2_cdaweb/sis_{inst_id:s}/{{year:4d}}/'
download_tags = {}
for inst_id in inst_ids.keys():
    download_tags[inst_id] = {'': {
        'remote_dir': remote_dir.format(inst_id=inst_id),
        'fname': fname.format(inst_id=inst_id)}}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)
