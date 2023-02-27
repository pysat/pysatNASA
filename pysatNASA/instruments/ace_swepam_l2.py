# -*- coding: utf-8 -*-
"""Module for the Advanced Composition Explorer (ACE) EPAM instrument.

References
----------
- Stone, E., Frandsen, A., Mewaldt, R. et al. The Advanced Composition Explorer.
  Space Science Reviews 86, 1–22 (1998). https://doi.org/10.1023/A:1005082526237
- McComas, D., Bame, S., Barker, P. et al. Solar Wind Electron Proton Alpha
  Monitor (SWEPAM) for the Advanced Composition Explorer. Space Science Reviews
  86, 563–612 (1998). https://doi.org/10.1023/A:1005040232597

Properties
----------
platform
    'ace'
name
    'swepam_l2'
tag
    None supported
inst_id
    ['h0', 'h2', 'k0', 'k1']

Note
----
- Level 1 ACE data is maintained at pysatSpaceWeather.
- Release notes at
  https://cdaweb.gsfc.nasa.gov/pub/data/ace/swepam/swepam_level2_release_notes.txt

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
name = 'swepam_l2'
tags = {'': ''}
inst_ids = {id: [tag for tag in tags.keys()] for id in ['h0', 'h2', 'k0', 'k1']}
pandas_format = False

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {id: {'': dt.datetime(2021, 1, 1)} for id in inst_ids.keys()}

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
fname = ''.join(('ac_{inst_id:s}_swe_{{year:4d}}{{month:02d}}{{day:02d}}_',
                 'v{{version:02d}}.cdf'))
supported_tags = {id: {'': fname.format(inst_id=id)} for id in inst_ids.keys()}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the load routine
load = functools.partial(cdw.load, pandas_format=pandas_format)

# Set the download routine
remote_dir = '/pub/data/ace/swepam/level_2_cdaweb/swe_{inst_id:s}/{{year:4d}}/'
download_tags = {}
for inst_id in inst_ids.keys():
    download_tags[inst_id] = {'': {
        'remote_dir': remote_dir.format(inst_id=inst_id),
        'fname': fname.format(inst_id=inst_id)}}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)
