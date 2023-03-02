# -*- coding: utf-8 -*-
"""Module for the Advanced Composition Explorer (ACE) MAG instrument.

Properties
----------
platform
    'ace'
name
    'mag_l2'
tag
    'base' or 'key'
inst_id
    '1sec', '16sec', '4min', '5min', '1hr'

References
----------
- Stone, E., Frandsen, A., Mewaldt, R. et al. The Advanced Composition Explorer.
  Space Science Reviews 86, 1–22 (1998). https://doi.org/10.1023/A:1005082526237
- Smith, C., L'Heureux, J., Ness, N. et al. The ACE Magnetic Fields Experiment.
  Space Science Reviews 86, 613–632 (1998).
  https://doi.org/10.1023/A:1005092216668

Note
----
- Level 1 ACE data is maintained at pysatSpaceWeather.
- Release notes at
  https://cdaweb.gsfc.nasa.gov/pub/data/ace/mag/mag_level2_release_notes.txt

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
name = 'mag_l2'
tags = {'base': 'ACE Magnetic Field Base Data',
        'key': 'ACE Magnetic Field Key Parameters'}
inst_ids = {'1sec': ['base'],
            '16sec': ['base', 'key'],
            '4min': ['base'],
            '5min': ['key'],
            '1hr': ['base', 'key']}
pandas_format = False
# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {id: {tag: dt.datetime(2022, 1, 1) for tag in inst_ids[id]}
               for id in inst_ids.keys()}

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
strid = {'1sec': {'base': 'h3'},
         '16sec': {'base': 'h0', 'key': 'k1'},
         '4min': {'base': 'h1'},
         '5min': {'key': 'k0'},
         '1hr': {'base': 'h2', 'key': 'k2'}}
fname = ''.join(('ac_{sid:s}_mfi_{{year:4d}}{{month:02d}}{{day:02d}}_',
                 'v{{version:02d}}.cdf'))
supported_tags = {id: {tag: fname.format(sid=strid[id][tag])
                       for tag in inst_ids[id]}
                  for id in inst_ids.keys()}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the load routine
load = functools.partial(cdw.load, pandas_format=pandas_format)

# Set the download routine
remote_dir = '/pub/data/ace/mag/level_2_cdaweb/mfi_{sid:s}/{{year:4d}}/'
download_tags = {id: {tag: {'remote_dir': remote_dir.format(sid=strid[id][tag]),
                            'fname': fname.format(sid=strid[id][tag])}
                      for tag in inst_ids[id]}
                 for id in inst_ids.keys()}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)
