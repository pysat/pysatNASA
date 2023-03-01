# -*- coding: utf-8 -*-
"""Module for the Advanced Composition Explorer (ACE) EPAM instrument.

References
----------
- Stone, E., Frandsen, A., Mewaldt, R. et al. The Advanced Composition Explorer.
  Space Science Reviews 86, 1–22 (1998). https://doi.org/10.1023/A:1005082526237
- Gold, R., Krimigis, S., Hawkins, S. et al. Electron, Proton, and Alpha Monitor
  on the Advanced Composition Explorer spacecraft. Space Science Reviews 86,
  541–562 (1998). https://doi.org/10.1023/A:1005088115759

Properties
----------
platform
    'ace'
name
    'epam_l2'
tag
    'base' or 'key'
inst_id
    '12sec', '5min', '1hr'

Note
----
- Level 1 ACE data is maintained at pysatSpaceWeather.
- Release notes at
  https://cdaweb.gsfc.nasa.gov/pub/data/ace/epam/epam_level2_release_notes.txt

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
name = 'epam_l2'
tags = {'base': 'ACE/EPAM Solar Energetic Particle Base Data',
        'key': 'ACE/EPAM Solar Energetic Particle Key Parameters'}
inst_ids = {'12sec': ['base'],
            '5min': ['key', 'base'],
            '1hr': ['key', 'base']}
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
strid = {'12sec': {'base': 'h3'},
         '5min': {'base': 'h1', 'key': 'k0'},
         '1hr': {'base': 'h2', 'key': 'k1'}}
fname = ''.join(('ac_{sid:s}_epm_{{year:4d}}{{month:02d}}{{day:02d}}_',
                 'v{{version:02d}}.cdf'))
supported_tags = {id: {tag: fname.format(sid=strid[id][tag])
                       for tag in inst_ids[id]}
                  for id in inst_ids.keys()}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the load routine
load = functools.partial(cdw.load, pandas_format=pandas_format)

# Set the download routine
remote_dir = '/pub/data/ace/epam/level_2_cdaweb/epm_{sid:s}/{{year:4d}}/'
download_tags = {id: {tag: {'remote_dir': remote_dir.format(sid=strid[id][tag]),
                            'fname': fname.format(sid=strid[id][tag])}
                      for tag in inst_ids[id]}
                 for id in inst_ids.keys()}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)
