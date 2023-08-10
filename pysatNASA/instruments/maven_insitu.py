# -*- coding: utf-8 -*-
"""Module for the MAVEN insitu instrument.

Created by: Teresa Esman, NPP at GSFC

Supports the Key parameter (kp) data from multiple instruments
onboard the Mars Atmosphere and Volatile Evolution (MAVEN) satellite.

Accesses local data in CDF format.
Downlaods from CDAWeb.

Properties
----------
platform
    'maven'
name
    'insitu'
tag
    None supported


Examples
--------
::
    import pysat
    from pysat.utils import registry
    registry.register_by_module(pysatNASA.instruments)


    insitu = pysat.Instrument(platform='MAVEN', name='insitu')
    insitu.download(dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 31))
    insitu.load(2020, 1, use_header = True)
"""

import datetime as dt
import functools
import pysat
from pysat.instruments.methods import general as mm_gen
from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import general as mm_nasa
from pysatNASA.instruments.methods import maven as mm_mvn

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'maven'
name = 'insitu'
tags = {'': ''}
inst_ids = {'': ['']}

pandas_format = False

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'': dt.datetime(2020, 1, 1)}}

# ----------------------------------------------------------------------------
# Instrument methods

# Use standard init routine
init = functools.partial(mm_nasa.init, module=mm_mvn, name=name)


def clean(self):
    """Clean MAVEN insitu kp data to the specified level.

    Note
    ----
        Supports 'none'. Method is
        not called by pysat if clean_level is None or 'none'.
    """
    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the MAVEN and pysat methods

# Set the list_files routine
fname = ''.join(('mvn_insitu_kp-4sec_{year:04d}{month:02d}{day:02d}_',
                 'v{version:02d}_r{revision:02d}.cdf'))
supported_tags = {'': {'': fname}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)
# Set the download routine
basic_tag = {'remote_dir': ''.join(('/pub/data/maven/insitu/kp-4sec/',
                                    'cdfs/{year:04d}/{month:02d}')),
             'fname': fname}
download_tags = {'': {'': basic_tag}}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)


def init(self):
    """Initialize the Instrument object with instrument specific values.

    Runs once upon instantiation.

    Parameters
    -----------
    self : pysat.Instrument
        Instrument class object
    """

    pysat.logger.info(mm_mvn.ackn_str)
    self.acknowledgements = mm_mvn.ackn_str
    self.references = mm_mvn.references

    return


# Set the load routine
load = functools.partial(cdw.load, epoch_name='epoch',
                         pandas_format=pandas_format, use_cdflib=True)
