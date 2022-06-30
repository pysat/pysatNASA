# -*- coding: utf-8 -*-
"""Module for the OMNI HRO instrument.

Supports OMNI Combined, Definitive, IMF and Plasma Data, and Energetic
Proton Fluxes, Time-Shifted to the Nose of the Earth's Bow Shock, plus Solar
and Magnetic Indices. Downloads data from the NASA Coordinated Data Analysis
Web (CDAWeb). Supports both 5 and 1 minute files.

Properties
----------
platform
    'omni'
name
    'hro'
tag
    Select time between samples, one of {'1min', '5min'}
inst_id
    None supported

Note
----
Files are stored by the first day of each month. When downloading use
omni.download(start, stop, freq='MS') to only download days that could possibly
have data.  'MS' gives a monthly start frequency.

This material is based upon work supported by the
National Science Foundation under Grant Number 1259508.

Any opinions, findings, and conclusions or recommendations expressed in this
material are those of the author(s) and do not necessarily reflect the views
of the National Science Foundation.

Warnings
--------
- Currently no cleaning routine. Though the CDAWEB description indicates that
  these level-2 products are expected to be ok.
- Module not written by OMNI team.

"""

import datetime as dt
import functools
import numpy as np
import pandas as pds
import scipy.stats as stats
import warnings

from pysat.instruments.methods import general as mm_gen
from pysat import logger

from pysatNASA.instruments.methods import cdaweb as cdw

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'omni'
name = 'hro'
tags = {'1min': '1-minute time averaged data',
        '5min': '5-minute time averaged data'}
inst_ids = {'': [tag for tag in tags.keys()]}

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'1min': dt.datetime(2009, 1, 1),
                    '5min': dt.datetime(2009, 1, 1)}}

# ----------------------------------------------------------------------------
# Instrument methods


def init(self):
    """Initialize the Instrument object with instrument specific values.

    Runs once upon instantiation.

    """

    ackn_str = ''.join(('For full acknowledgement info, please see: ',
                        'https://omniweb.gsfc.nasa.gov/html/citing.html'))
    self.acknowledgements = ackn_str
    self.references = ' '.join(('J.H. King and N.E. Papitashvili, Solar',
                                'wind spatial scales in and comparisons',
                                'of hourly Wind and ACE plasma and',
                                'magnetic field data, J. Geophys. Res.,',
                                'Vol. 110, No. A2, A02209,',
                                '10.1029/2004JA010649.'))
    logger.info(ackn_str)
    return


def clean(self):
    """Clean OMNI HRO data to the specified level.

    Note
    ----
    'clean' - Replace default fill values with NaN
    'dusty' - Same as clean
    'dirty' - Same as clean
    'none'  - Preserve original fill values

    """
    for key in self.data.columns:
        if key != 'Epoch':
            fill = self.meta[key, self.meta.labels.fill_val]
            if np.asarray(fill).shape == (): 
                idx, = np.where(self[key] == fill)
            else:
                idx, = np.where(self[key] == fill[0])

            # Set the fill values to NaN
            self[idx, key] = np.nan

            # Replace the old fill value with NaN and add this to the notes
            fill_notes = "".join(["Replaced standard fill value with NaN. ",
                                  "Standard value was: {:}".format(
                                      self.meta[key,
                                                self.meta.labels.fill_val])])
            notes = '\n'.join([str(self.meta[key, self.meta.labels.notes]),
                               fill_notes])
            self.meta[key, self.meta.labels.notes] = notes
            self.meta[key, self.meta.labels.fill_val] = np.nan

    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
fname = ''.join(['omni_hro_{tag:s}_{{year:4d}}{{month:02d}}{{day:02d}}_',
                 'v{{version:02d}}.cdf'])
supported_tags = {inst_id: {tag: fname.format(tag=tag) for tag in tags.keys()}
                  for inst_id in inst_ids.keys()}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags,
                               file_cadence=pds.DateOffset(months=1))

# Set the download routine
remote_dir = '/pub/data/omni/omni_cdaweb/hro_{tag:s}/{{year:4d}}/'
download_tags = {inst_id: {tag: {'remote_dir': remote_dir.format(tag=tag),
                                 'fname': supported_tags[inst_id][tag]}
                           for tag in inst_ids[inst_id]}
                 for inst_id in inst_ids.keys()}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)


# Set the load routine
def load(fnames, tag=None, inst_id=None, file_cadence=pds.DateOffset(months=1),
         flatten_twod=True):
    """Load data and fix meta data.

    Parameters
    ----------
    fnames : pandas.Series
        Series of filenames
    tag : str or NoneType
        tag or None (default=None)
    inst_id : str or NoneType
        satellite id or None (default=None)
    file_cadence : dt.timedelta or pds.DateOffset
        pysat assumes a daily file cadence, but some instrument data files
        contain longer periods of time.  This parameter allows the specification
        of regular file cadences greater than or equal to a day (e.g., weekly,
        monthly, or yearly). (default=dt.timedelta(days=1))
    flatted_twod : bool
        Flattens 2D data into different columns of root DataFrame rather
        than produce a Series of DataFrames. (default=True)

    Returns
    -------
    data : pandas.DataFrame
        Object containing satellite data
    meta : pysat.Meta
        Object containing metadata such as column names and units

    """

    data, meta = cdw.load(fnames, tag=tag, inst_id=inst_id,
                          file_cadence=file_cadence, flatten_twod=flatten_twod)

    return data, meta
