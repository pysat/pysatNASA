# -*- coding: utf-8 -*-
"""Supports the Ion Drift Meter (IDM) instrument on
Dynamics Explorer 2 (DE2).

From CDAWeb:


References
----------

Properties
----------
platform
    'de2'
name
    'idm'
inst_id
    None Supported
tag
    None Supported

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
name = 'idm'
tags = {'': '2 sec cadence IDM data'}  # this is the default cadence
inst_ids = {'': ['']}

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'': dt.datetime(1983, 1, 1)}}

# ----------------------------------------------------------------------------
# Instrument methods


def init(self):
    """Initializes the Instrument object with instrument specific values.

    Runs once upon instantiation.

    """

    logger.info(mm_de2.ackn_str)
    self.acknowledgements = mm_de2.ackn_str
    self.references = mm_de2.refs['idm']
    return


def clean(self):
    """Routine to return DE2 IDM data cleaned to the specified level

    Note
    ----
    'clean' - Not specified
    'dusty' - Not specified
    'dirty' - Not specified
    'none'  No cleaning applied, routine not called in this case.

    """
    warnings.warn('No cleaning routines available for DE2 IDM')

    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
fname = 'de2_vion250ms_idm_{year:04d}{month:02d}{day:02d}_v{version:02d}.cdf'
supported_tags = {'': {'': fname}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the load routine
load = cdw.load

# Set the download routine
basic_tag = {'remote_dir': ''.join(('/pub/data/de/de2/plasma_idm',
                                    '/vion250ms_cdaweb/{year:4d}/')),
             'fname': fname}
download_tags = {'': {'': basic_tag}}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)
