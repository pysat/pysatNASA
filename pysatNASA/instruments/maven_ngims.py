# -*- coding: utf-8 -*-
"""Module for MAVEN NGIMS.

Supports the Neutral Gas and Ion Mass Spectrometer
(NGIMS) instrument onboard the Mars Atmosphere and
Volatile Evolution (MAVEN) mission. Downloads data
from the NASA Planetary Data System (PDS).

Properties
----------
platform
    'maven'
name
    'ngims'
tag
    'csn' or 'ion'
sat_id
    None Supported

Warnings
--------
- Currently no cleaning routine.
- Module not written by NGIMS team.

"""

import datetime as dt
import functools

import pandas as pds

import pysat
from pysat.instruments.methods import general as mm_gen
from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import general as mm_nasa

platform = 'maven'
name = 'ngims'
tags = {'csn': 'Neutral Composition Data',
        'ion': 'Ion Composition Data'}
inst_ids = {'': ['csn', 'ion']}
_test_dates = {'': {'csn': dt.datetime(2018, 8, 1),
                    'ion': dt.datetime(2018, 8, 1)}}

# support list files routine
# use the default CDAWeb method
fname1 = ''.join(['mvn_ngi_l2_csn-abund-?????_{year:04d}{month:02d}',
                  '{day:02d}T{hour:02d}{minute:02d}{second:02d}_',
                  'v{version:02d}_r{revision:02d}.csv'])
fname2 = ''.join(['mvn_ngi_l2_ion-abund-?????_{year:04d}{month:02d}',
                  '{day:02d}T{hour:02d}{minute:02d}{second:02d}_',
                  'v{version:02d}_r{revision:02d}.csv'])
supported_tags = {'': {'csn': fname1,
                       'ion': fname2}}

multi_file_day = True

list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)
# support download routine
# use the default CDAWeb method modified for the PDS website
basic_tag1 = {'remote_dir': ''.join(('/PDS/data/PDS4/MAVEN/ngims_bundle/l2/',
                                     '{year:04d}/{month:02d}/')),
              'fname': fname1}
basic_tag2 = {'remote_dir': ''.join(('/PDS/data/PDS4/MAVEN/ngims_bundle/l2/',
                                     '{year:04d}/{month:02d}/')),
              'fname': fname2}
supported_tags = {'': {'csn': basic_tag1,
                       'ion': basic_tag2}}
download = functools.partial(cdw.download, supported_tags=supported_tags,
                             remote_url='https://atmos.nmsu.edu')

# support listing files currently on CDAWeb
list_remote_files = functools.partial(cdw.list_remote_files,
                                      remote_url='https://atmos.nmsu.edu',
                                      supported_tags=supported_tags)


def load(fnames, tag=None, inst_id=None):
    """Load data files.

    Parameters
    ------------
    fnames : pandas.Series
        Series of filenames
    tag : str
        tag or None (default=None)
    sat_id : str
        satellite id or None (default=None)

    Returns
    ---------
    data : pandas.DataFrame
        Object containing satellite data
    meta : pysat.Meta
        Object containing metadata such as column names and units

    Notes
    -----
    Called by pysat. Not intended for direct use by user.


    """

    ldata = []
    for fname in fnames:
        ldata.append(pds.read_csv(fname, index_col=0, parse_dates=True))

    if len(ldata) > 0:
        data = pds.concat(ldata)
    else:
        data = pds.DataFrame()

    meta = pysat.Meta()

    return data, meta


def init(self):
    """Initialize."""

    return


# Use default clean
clean = mm_nasa.clean
