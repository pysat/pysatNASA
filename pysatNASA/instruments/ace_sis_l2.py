# -*- coding: utf-8 -*-
"""Module for the Advanced Composition Explorer (ACE) SIS instrument.

Properties
----------
platform
    'ace'
name
    'sis_l2'
tag
    'base' or 'key'
inst_id
    '256sec' or '1hr'

References
----------
- Stone, E., Frandsen, A., Mewaldt, R. et al. The Advanced Composition Explorer.
  Space Science Reviews 86, 1–22 (1998). https://doi.org/10.1023/A:1005082526237
- Stone, E., Cohen, C., Cook, W. et al. The Solar Isotope Spectrometer for the
  Advanced Composition Explorer. Space Science Reviews 86, 357–408 (1998).
  https://doi.org/10.1023/A:1005027929871

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
tags = {'base': 'ACE/SIS Solar Isotope Spectrometer Base Data',
        'key': 'ACE/SIS Solar Isotope Spectrometer Key Parameters'}
inst_ids = {'256sec': ['base'],
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

# Use default ace clean
clean = mm_ace.clean

# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
strid = {'256sec': {'base': 'h1'},
         '1hr': {'base': 'h2', 'key': 'k0'}}
fname = ''.join(('ac_{sid:s}_sis_{{year:4d}}{{month:02d}}{{day:02d}}_',
                 'v{{version:02d}}.cdf'))
supported_tags = {id: {tag: fname.format(sid=strid[id][tag])
                       for tag in inst_ids[id]}
                  for id in inst_ids.keys()}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the load routine
load = functools.partial(mm_ace.load, to_pandas=False)

# Set the download routine
download_tags = {'256sec': {'base': 'AC_H1_SIS'},
                 '1hr': {'base': 'AC_H2_SIS', 'key': 'AC_K0_SIS'}}

download = functools.partial(cdw.cdas_download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.cdas_list_remote_files,
                                      supported_tags=download_tags)
