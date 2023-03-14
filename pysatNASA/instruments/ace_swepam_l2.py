# -*- coding: utf-8 -*-
"""Module for the Advanced Composition Explorer (ACE) EPAM instrument.

Properties
----------
platform
    'ace'
name
    'swepam_l2'
tag
    'base' or 'key'
inst_id
    '64sec', '5min', '1hr'

References
----------
- Stone, E., Frandsen, A., Mewaldt, R. et al. The Advanced Composition Explorer.
  Space Science Reviews 86, 1–22 (1998). https://doi.org/10.1023/A:1005082526237
- McComas, D., Bame, S., Barker, P. et al. Solar Wind Electron Proton Alpha
  Monitor (SWEPAM) for the Advanced Composition Explorer. Space Science Reviews
  86, 563–612 (1998). https://doi.org/10.1023/A:1005040232597

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
tags = {'base': 'ACE/SWEPAM Solar Wind Experiment Base Data',
        'key': 'ACE/SWEPAM Solar Wind Experiment Key Parameters'}
inst_ids = {'64sec': ['base'],
            '5min': ['key'],
            '1hr': ['key', 'base']}
pandas_format = False

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {id: {tag: dt.datetime(2021, 1, 1) for tag in inst_ids[id]}
               for id in inst_ids.keys()}

# ----------------------------------------------------------------------------
# Instrument methods


# Use standard init routine
init = functools.partial(mm_nasa.init, module=mm_ace, name=name)

# Use default ace clean
clean = mm_ace.clean

# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
strid = {'64sec': {'base': 'h0'},
         '5min': {'key': 'k0'},
         '1hr': {'base': 'h2', 'key': 'k1'}}
fname = ''.join(('ac_{sid:s}_swe_{{year:4d}}{{month:02d}}{{day:02d}}_',
                 'v{{version:02d}}.cdf'))
supported_tags = {id: {tag: fname.format(sid=strid[id][tag])
                       for tag in inst_ids[id]}
                  for id in inst_ids.keys()}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the load routine
meta_translation = {'CATDESC': 'desc', 'FILLVAL': 'fill',
                    'LABLAXIS': 'plot_label', 'VALIDMAX': 'value_max',
                    'VALIDMIN': 'value_min', 'VAR_NOTES': 'notes'}
load = functools.partial(cdw.load, pandas_format=pandas_format,
                         meta_translation=meta_translation)

# Set the download routine
remote_dir = '/pub/data/ace/swepam/level_2_cdaweb/swe_{sid:s}/{{year:4d}}/'
download_tags = {id: {tag: {'remote_dir': remote_dir.format(sid=strid[id][tag]),
                            'fname': fname.format(sid=strid[id][tag])}
                      for tag in inst_ids[id]}
                 for id in inst_ids.keys()}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)
