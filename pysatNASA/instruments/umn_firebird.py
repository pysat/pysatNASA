# -*- coding: utf-8 -*-
"""Module for the FIREBIRD cubesat.



Properties
----------
platform
    'umn'
name
    'firebird'
tag
    None
inst_id
    ['fu3', 'fu4']

Warnings
--------
- Currently no cleaning routine.

"""

import datetime as dt
import functools

from pysat.instruments.methods import general as mm_gen
from pysat import logger

from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import general as mm_nasa

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'umn'
name = 'firebird'
tags = {'': ''}
inst_ids = {'fu3': [''], 'fu4': ['']}

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'fu3': {'': dt.datetime(2016, 1, 1)},
               'fu4': {'': dt.datetime(2016, 1, 1)}}

# ----------------------------------------------------------------------------
# Instrument methods


def init(self):
    """Initialize the Instrument object with instrument specific values.

    Runs once upon instantiation.

    """
    self.acknowledgements = ' '.join(('???'))
    self.references = ' '.join(('???'))
    logger.info(self.acknowledgements)

    return


# No cleaning, use standard warning function instead
clean = mm_nasa.clean_warn

# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
fname = ''.join(('{id:}_context_{{year:04d}}{{month:02d}}{{day:02d}}'
                 '_v{{version:02d}}.cdf'))
supported_tags = {
    id: {'': fname.format(id=id.upper())} for id in inst_ids.keys()}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the load routine
load = cdw.load

# Set the download routine
download_tags = {id: {
    '': {'remote_dir': '/firebird/{id:}/{{year:4d}}/'.format(id=id.upper()),
    'fname': fname.format(id=id.upper())}} for id in inst_ids.keys()}
download = functools.partial(cdw.download, supported_tags=download_tags,
                             remote_url='http://rbsp.space.umn.edu')

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)
