# -*- coding: utf-8 -*-
"""Module for the MAVEN sep instrument.

Supports the Solar Energetic Particle (SEP) data from
onboard the Mars Atmosphere and Volatile Evolution (MAVEN) satellite.

Accesses local data in CDF format.
Downloads from CDAWeb.

Properties
----------
platform
    'maven'
name
    'sep'
tag
    None supported
inst_id
    ['s1', 's2']

Examples
--------
::
    import pysat

    insitu = pysat.Instrument(platform='maven', name='sep', inst_id='s1')
    insitu.download(dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 31))
    insitu.load(2020, 1, use_header=True)

"""

import datetime as dt
import functools

from pysat.instruments.methods import general as mm_gen
from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import general as mm_nasa
from pysatNASA.instruments.methods import maven as mm_mvn

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'maven'
name = 'sep'
tags = {'': 'Level 2 Solar Energetic Particle data'}
inst_ids = {'s1': [''], 's2': ['']}

pandas_format = False

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {id: {'': dt.datetime(2020, 1, 1)} for id in inst_ids.keys()}
# TODO(#218, #222): Remove when compliant with multi-day load tests
_new_tests = {inst_id: {tag: False for tag in tags.keys()}
              for inst_id in inst_ids.keys()}

# ----------------------------------------------------------------------------
# Instrument methods

# Use standard init routine
init = functools.partial(mm_nasa.init, module=mm_mvn, name=name)


# Use default clean
clean = mm_nasa.clean


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the MAVEN and pysat methods

# Set the list_files routine
fname = ''.join(('mvn_sep_l2_s1-cal-svy-full_{year:04d}{month:02d}{day:02d}_',
                 'v{version:02d}_r{revision:02d}.cdf'))

fname2 = ''.join(('mvn_sep_l2_s2-cal-svy-full_{year:04d}{month:02d}{day:02d}_',
                 'v{version:02d}_r{revision:02d}.cdf'))

supported_tags = {'s1': {'': fname},
                  's2': {'': fname2}}

list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the download routine
basic_tag = {'remote_dir': ''.join(('/pub/data/maven/sep/l2/s1-cal-svy-full',
                                    '/{year:04d}/{month:02d}')),
             'fname': fname}

basic_tag2 = {'remote_dir': ''.join(('/pub/data/maven/sep/l2/s2-cal-svy-full',
                                    '/{year:04d}/{month:02d}')),
              'fname': fname2}

download_tags = {'s1': {'': basic_tag},
                 's2': {'': basic_tag2}}

# Set the download routine
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)

# Set the load routine
load = functools.partial(cdw.load, epoch_name='epoch',
                         pandas_format=pandas_format, use_cdflib=True)
