# -*- coding: utf-8 -*-
"""Supports the Vector Electric Field Instrument (VEFI) on
Dynamics Explorer 2 (DE2).

From CDAWeb:




References
----------


Properties
----------
platform
    'de2'
name
    'vefi'
inst_id
    None Supported
tag
    'dca' or 'ac'


Warnings
--------
- Currently no cleaning routine.


Authors
-------
J. Klenzing

"""

import datetime as dt
import functools
import warnings

from pysat import logger
from pysat.instruments.methods import general as mm_gen
from pysatNASA.instruments.methods import de2 as mm_de2
from pysatNASA.instruments.methods import cdaweb as cdw

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'de2'
name = 'vefi'
tags = {'dca': '500 ms cadence DC Averaged Electric Field data',
        'ac': '500ms cadence AC Electric Field data'}
inst_ids = {'': ['dca', 'ac']}

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {tag: dt.datetime(1983, 1, 1) for tag in tags}}

# ----------------------------------------------------------------------------
# Instrument methods


def init(self):
    """Initializes the Instrument object with instrument specific values.

    Runs once upon instantiation.

    """

    logger.info(mm_de2.ackn_str)
    self.acknowledgements = mm_de2.ackn_str
    self.references = mm_de2.refs['vefi']
    return


def clean(self):
    """Routine to return DE2 VEFI data cleaned to the specified level

    Note
    ----
    'clean' - Not specified
    'dusty' - Not specified
    'dirty' - Not specified
    'none'  No cleaning applied, routine not called in this case.

    """
    warnings.warn('No cleaning routines available for DE2 VEFI')

    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
datestr = '{year:04d}{month:02d}{day:02d}_v{version:02d}'
fname = 'de2_{tag:s}500ms_vefi_{datestr:s}.cdf'
supported_tags = {'': {tag: fname.format(tag=tag, datestr=datestr)
                       for tag in tags}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the load routine
load = cdw.load

# Set the download routine
download_tags = {'': {tag: {'remote_dir': ''.join(('/pub/data/de/de2/',
                                                   'electric_fields_vefi/',
                                                   tag, '500ms_vefi_cdaweb/',
                                                   '{year:4d}/')),
                            'fname': fname.format(tag=tag, datestr=datestr)}
                      for tag in tags}}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)
