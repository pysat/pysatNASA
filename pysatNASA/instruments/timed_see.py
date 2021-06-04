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
flatten_twod
    If True, then two dimensional data is flattened across
    columns. Name mangling is used to group data, first column
    is 'name', last column is 'name_end'. In between numbers are
    appended 'name_1', 'name_2', etc. All data for a given 2D array
    may be accessed via, data.loc[:, 'item':'item_end']
    If False, then 2D data is stored as a series of DataFrames,
    indexed by Epoch. data.loc[0, 'item']
    (default=True)

Note
----
- no tag required

Warnings
--------
- Currently no cleaning routine.

"""

import datetime as dt
import functools
import pandas as pds
import warnings

from pysat import logger
from pysat.instruments.methods import general as mm_gen

from pysatNASA.instruments.methods import cdaweb as cdw

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'timed'
name = 'see'
tags = {'': ''}
inst_ids = {'': [tag for tag in tags.keys()]}

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'': dt.datetime(2009, 1, 1)}}

# ----------------------------------------------------------------------------
# Instrument methods


def init(self):
    """Initializes the Instrument object with instrument specific values.

    Runs once upon instantiation.

    """

    rules_url = 'https://www.timed.jhuapl.edu/WWW/scripts/mdc_rules.pl'
    ackn_str = ' '.join(('Please see the Rules of the Road at', rules_url))
    logger.info(ackn_str)
    self.acknowledgements = ackn_str
    self.references = ' '.join(('Woods, T. N., Eparvier, F. G., Bailey,',
                                'S. M., Chamberlin, P. C., Lean, J.,',
                                'Rottman, G. J., Solomon, S. C., Tobiska,',
                                'W. K., and Woodraska, D. L. (2005),',
                                'Solar EUV Experiment (SEE): Mission',
                                'overview and first results, J. Geophys.',
                                'Res., 110, A01312,',
                                'doi:10.1029/2004JA010765.'))

    return


def clean(self):
    """Routine to return TIMED SEE data cleaned to the specified level

    Note
    ----
    No cleaning currently available.

    """
    warnings.warn('no cleaning routines available for TIMED SEE data')

    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
fname = 'timed_l3a_see_{year:04d}{month:02d}{day:02d}_v{version:02d}.cdf'
supported_tags = {'': {'': fname}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags,
                               file_cadence=pds.DateOffset(months=1))

# Set the load routine
load = functools.partial(cdw.load, file_cadence=pds.DateOffset(months=1))

# Set the download routine
basic_tag = {'remote_dir': ''.join(('/pub/data/timed/see/data/level3a_cdf',
                                    '/{year:4d}/{month:02d}/')),
             'fname': fname}
download_tags = {'': {'': basic_tag}}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)
