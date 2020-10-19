# -*- coding: utf-8 -*-
"""
Ion Velocity Meter (IVM) support for the NASA/INPE SPORT CubeSat.

This mission is still in development. This routine is here to help
with the development of code associated with SPORT and the IVM.

Properties
----------
platform
    'sport'
name
    'ivm'
tag
    '', 'L1', 'L2'
inst_id
    None supported

Warnings
--------
- Currently no cleaning routine.

"""

import datetime as dt
import functools
import logging
import warnings

import pysat
from pysat.instruments.methods import general as mm_gen

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------
# Instrument attributes
platform = 'sport'
name = 'ivm'
tags = {'': 'Level-2 IVM Files',
        'L1': 'Level-1 IVM Files',
        'L0': 'Level-0 IVM Files'}
inst_ids = {'': [tag for tag in tags.keys()]}

# ----------------------------------------------------------------------------
# Instrument test attributes

# A good day to download test data for. Downloads aren't currently supported
_test_dates = {'': {kk: dt.datetime(2019, 1, 1) for kk in tags.keys()}}
_test_download = {'': {kk: False for kk in tags.keys()}}

# ----------------------------------------------------------------------------
# Instrument methods


def init(self):
    """Initializes the Instrument object with instrument specific values.

    Runs once upon instantiation.

    """
    self.acknowledgements = ' '.join(("Mission acknowledgements and data",
                                      "restrictions will be printed here",
                                      "when available."))
    self.references = 'Mission papers to be added when published'
    logger.info(self.acknowledgements)

    return


def clean(self):
    """Routine to return SPORT IVM data cleaned to the specified level

    Note
    ----
    No cleaning currently available for SPORT IVM.

    """
    warnings.warn("No cleaning currently available for SPORT IVM")

    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
prefix = 'SPORT_{tag}_IVM_'
format_str = ''.join(('{year:04d}-{month:02d}-{day:02d}',
                      '_v{version:02d}r{revision:04d}.NC'))
supported_tags = {'': {'': ''.join((prefix.format(tag='L2'), format_str)),
                       'L1': ''.join((prefix.format(tag='L1'), format_str)),
                       'L0': ''.join((prefix.format(tag='L0'), format_str))}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)


def load(fnames, tag=None, inst_id=None, **kwargs):
    """Loads SPORT IVM data using pysat.utils.load_netcdf4.

    This routine is called as needed by pysat. It is not intended
    for direct user interaction.

    Parameters
    ----------
    fnames : array-like
        iterable of filename strings, full path, to data files to be loaded.
        This input is nominally provided by pysat itself.
    tag : string
        tag name used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself.
    inst_id : string
        Satellite ID used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself.
    **kwargs : extra keywords
        Passthrough for additional keyword arguments specified when
        instantiating an Instrument object. These additional keywords
        are passed through to this routine by pysat.

    Returns
    -------
    data, metadata
        Data and Metadata are formatted for pysat. Data is a pandas
        DataFrame while metadata is a pysat.Meta instance.

    Note
    ----
    Any additional keyword arguments passed to pysat.Instrument
    upon instantiation are passed along to this routine and through
    to the load_netcdf4 call.

    Examples
    --------
    ::

        inst = pysat.Instrument('sport', 'ivm')
        inst.load(2019,1)

    """

    return pysat.utils.load_netcdf4(fnames, **kwargs)


def download(date_array, tag, inst_id, data_path=None):
    """Downloads data for SPORT IVM, once SPORT is operational and in orbit.

    Parameters
    ----------
    date_array : array-like
        list of datetimes to download data for. The sequence of dates need
        not be contiguous.
    tag : string ('')
        Tag identifier used for particular dataset. This input is provided by
        pysat.
    inst_id : string  ('')
        Satellite ID string identifier used for particular dataset. This input
        is provided by pysat.
    data_path : string (None)
        Path to directory to download data to.

    """

    warnings.warn('Downloads are not currently supported - not launched yet!')

    pass


def clean(self):
    """Routine to return SPORT IVM data cleaned to the specified level

    Note
    ----
    No cleaning currently available for SPORT IVM.

    """

    warnings.warn("No cleaning currently available for SPORT")

    return
