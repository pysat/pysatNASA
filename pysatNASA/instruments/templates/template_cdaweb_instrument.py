#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3986131
#
# DISTRIBUTION STATEMENT A: Approved for public release. Distribution is
# unlimited.
# ----------------------------------------------------------------------------
"""Template for a pysat.Instrument support file that utilizes CDAWeb methods.

Copy and modify this file as needed when adding a new Instrument to pysat.

DO NOT include the NRL distribution statement in your new file. Contributions
by NRL developers will need to be cleared for classified or controlled information 
separately from the pysat pull request process.

This is a good area to introduce the instrument, provide background
on the mission, operations, instrumenation, and measurements.

Also a good place to provide contact information. This text will
be included in the pysat API documentation.

Properties
----------
platform
    *List platform string here*
name
    *List name string here*
inst_id
    *List supported inst_ids here*
tag
    *List supported tag strings here*

Note
----
- Optional section, remove if no notes

Warnings
--------
- Optional section, remove if no warnings
- Two blank lines needed afterward for proper formatting


Examples
--------
::

    Example code can go here

"""

import datetime as dt
import functools

# The core logger from pysat can be added here
from pysat import logger

# General methods from core pysat code
from pysat.instruments.methods import general as mm_gen

# CDAWeb methods prewritten for pysat
from pysatNASA.instruments.methods import cdaweb as cdw

# The platform and name strings associated with this instrument
# need to be defined at the top level.
# These attributes will be copied over to the Instrument object by pysat.
# The strings used here should also be used to name this file
# `platform_name.py`
platform = ''
name = ''

# Dictionary of data 'tags' and corresponding description
tags = {'': 'description 1',  # A blank string is the default data set
        'tag_string': 'description 2'}  # 'tag_string' is another option

# Let pysat know if there are multiple satellite platforms supported
# by these routines. Define a dictionary keyed by satellite ID, each with a list
# of corresponding tags:
# inst_ids = {'a':['L1', 'L0'], 'b':['L1', 'L2'], 'c':['L1', 'L3']}
inst_ids = {'': ['', 'tag_string']}

# Define good days to download data for pysat testing. The dict
# format is that outer dictionary uses `inst_id` values as keys, while the inner
# dict uses `tag` values as keys with a datetime object as the data value.
# _test_dates = {'a':{'L0':dt.datetime(2019,1,1),
#                     'L1':dt.datetime(2019,1,2)},
#                'b':{'L1':dt.datetime(2019,3,1),
#                     'L2':dt.datetime(2019,11,23),}}
_test_dates = {'': {'': dt.datetime(2019, 1, 1),
                    'tag_string': dt.datetime(2019, 3, 14)}}

# Additional information needs to be defined to support the CDAWeb list files
# routine. We need to define a filename format string for every supported
# combination of inst_id and tag string.
#
# fname1 = 'cnofs_vefi_bfield_1sec_{year:04d}{month:02d}{day:02d}_v05.cdf'
# fname2 = 'cnofs_vefi_acfield_1sec_{year:04d}{month:02d}{day:02d}_v05.cdf'
# supported_tags = {'sat1':{'tag1':fname1},
#                   'sat2':{'tag2':fname2}}
# You can use format keywords year, month, day, hour, min, sec,
# version and revision. See the code docstring for latest standards.
fname = ''.join(('cnofs_vefi_bfield_1sec_{year:04d}{month:02d}{day:02d}',
                 '_v{version:02d}.cdf'))
supported_tags = {'': {'': fname, 'tag_string': fname}}

# Use the CDAWeb methods list files routine. The command
# below presets some of the methods inputs, leaving
# those provided by pysat available when invoked
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

#
# Support load routine
#
# Use the default CDAWeb method
# No other information needs to be supplied here
load = cdw.load

#
# Support download routine
#
# To use the default CDAWeb method we need to provide additional information.
# - directory location on CDAWeb remote server
# - formatting template for filenames on CDAWeb
# - formatting template for files saved to the local disk
# - a dictionary needs to be created for each inst_id and tag
# - combination along with the file format template
# - outer dict keyed by inst_id, inner dict keyed by tag
basic_tag = {'remote_dir': '/pub/data/cnofs/vefi/bfield_1sec',
             'remote_fname': '{year:4d}/' + fname,
             'fname': fname}
basic_tag2 = {'remote_dir': '/pub/data/cnofs/other/bfield_1sec',
              'remote_fname': '{year:4d}/' + fname,
              'fname': fname}
supported_tags = {'': {'': basic_tag, 'tag_string': basic_tag2}}
download = functools.partial(cdw.download, supported_tags=supported_tags)

# Support listing files currently on CDAWeb
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=supported_tags)


def init(self):
    """Initialize the Instrument object with instrument specific values.

    Runs once upon instantiation.

    Note
    ----
    - Acknowledgements and References for this dataset may be defined here or
      in a custom module for a given spacecraft.
      e.g., `pysatNASA.instruments.methods.cnofs`
    - By default, pysat will warn a user if these properties are not attached to
      the instrument object.

    """

    ackn_str = "Acknowledgements can be added here."
    ref_str = ' '.join(("A. Genius et al., (2099),"
                        "'How it all works: A Simplified Tutorial',",
                        "Journal of Some Repute"))

    # Send the acknowledgments to the logger.  These will print to the screen if
    # user settings include logging.INFO
    logger.info(ackn_str)

    # Add acknowledgements to the instrument object.
    self.acknowledgements = ackn_str

    # Add references to the instrument object.
    self.references = ref_str

    return


# Code should be defined below as needed.
def preprocess(self):
    """Perform standard preprocessing.

    This routine is automatically applied to the Instrument object
    on every load by the pysat nanokernel (first in queue).

    Parameters
    ----------
    self : pysat.Instrument
        This object

    """

    return


# Code should be defined below as needed.
def clean(inst):
    """Return `platform_name` data to the specified level..

    Cleaning level is specified in inst.clean_level and pysat
    will accept user input for several strings. The clean_level is
    specified at instantiation of the Instrument object.

    Parameters
    -----------
    inst : pysat.Instrument
        Instrument class object, whose attribute clean_level is used to return
        the desired level of data selectivity.

    Note
    ----
    In general, pysat uses the following nomenclature for cleaning levels

    - 'clean'
        All parameters should be good, suitable for statistical and case studies
    - 'dusty'
        All paramers should generally be good though same may not be great
    - 'dirty'
        There are data areas that have issues, data should be used with caution
    - 'none'
        No cleaning applied, routine not called in this case.

    """

    return
