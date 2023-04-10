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
import warnings

import pysat
from pysat.instruments.methods import general as mm_gen

from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import omni as mm_omni

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
    pysat.logger.info(ackn_str)
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

# Set the list_remote_files routine
download_tags = {'': {'1min': 'OMNI_HRO_1MIN', '5min': 'OMNI_HRO_5MIN'}}
download = functools.partial(cdw.cdas_download,
                             supported_tags=download_tags)

list_remote_files = functools.partial(cdw.cdas_list_remote_files,
                                      supported_tags=download_tags)


# Set the load routine
def load(fnames, tag='', inst_id='', file_cadence=pds.DateOffset(months=1),
         flatten_twod=True, use_cdflib=None):
    """Load data and fix meta data.

    Parameters
    ----------
    fnames : pandas.Series
        Series of filenames
    tag : str
        tag or None (default='')
    inst_id : str
        satellite id or None (default='')
    file_cadence : dt.timedelta or pds.DateOffset
        pysat assumes a daily file cadence, but some instrument data files
        contain longer periods of time.  This parameter allows the specification
        of regular file cadences greater than or equal to a day (e.g., weekly,
        monthly, or yearly). (default=dt.timedelta(days=1))
    flatted_twod : bool
        Flattens 2D data into different columns of root DataFrame rather
        than produce a Series of DataFrames. (default=True)
    use_cdflib : bool or NoneType
        If True, force use of cdflib for loading. If False, prevent use of
        cdflib for loading. If None, will use pysatCDF if available with
        cdflib as fallback. (default=None)

    Returns
    -------
    data : pandas.DataFrame
        Object containing satellite data
    meta : pysat.Meta
        Object containing metadata such as column names and units

    """

    data, meta = cdw.load(fnames, tag=tag, inst_id=inst_id,
                          file_cadence=file_cadence, flatten_twod=flatten_twod,
                          use_cdflib=use_cdflib)

    return data, meta


# Local Functions (deprecated)

def deprecated(func):
    """Warn users that function has moved locations.

    Decorator function for deprecation warnings.

    """

    def func_wrapper(*args, **kwargs):
        """Wrap functions that use the decorator function."""

        warn_message = ' '.join(
            ['pysatNASA.instruments.omni_hro.{:}'.format(func.__name__),
             'has been moved to',
             'pysatNASA.instruments.methods.omni.{:}.'.format(func.__name__),
             'Please update your path to suppress this warning.',
             'This redirect will be removed in v0.1.0.'])
        # Triggered if OMMBV is not installed
        warnings.warn(warn_message, DeprecationWarning, stacklevel=2)

        return func(*args, **kwargs)

    return func_wrapper


@deprecated
def time_shift_to_magnetic_poles(inst):
    """Shift OMNI times to intersection with the magnetic pole.

    .. deprecated:: 0.0.4
    This function has been moved to `pysatNASA.instruments.methods.omni`.  This
    redirect will be removed in v0.1.0+.

    Parameters
    ----------
    inst : Instrument class object
        Instrument with OMNI HRO data

    Note
    ----
    - Time shift calculated using distance to bow shock nose (BSN)
      and velocity of solar wind along x-direction.
    - OMNI data is time-shifted to bow shock. Time shifted again
      to intersections with magnetic pole.

    Warnings
    --------
    Use at own risk.

    """

    mm_omni.time_shift_to_magnetic_poles(inst)

    return


@deprecated
def calculate_clock_angle(inst):
    """Calculate IMF clock angle and magnitude of IMF in GSM Y-Z plane.

    .. deprecated:: 0.0.4
    This function has been moved to `pysatNASA.instruments.methods.omni`.  This
    redirect will be removed in v0.1.0+.

    Parameters
    -----------
    inst : pysat.Instrument
        Instrument with OMNI HRO data

    """

    mm_omni.calculate_clock_angle(inst)

    return


@deprecated
def calculate_imf_steadiness(inst, steady_window=15, min_window_frac=0.75,
                             max_clock_angle_std=(90.0 / np.pi),
                             max_bmag_cv=0.5):
    """Calculate IMF steadiness and add parameters to instrument data.

    .. deprecated:: 0.0.4
    This function has been moved to `pysatNASA.instruments.methods.omni`.  This
    redirect will be removed in v0.1.0+.

    Parameters
    ----------
    inst : pysat.Instrument
        Instrument with OMNI HRO data
    steady_window : int
        Window for calculating running statistical moments in min (default=15)
    min_window_frac : float
        Minimum fraction of points in a window for steadiness to be calculated
        (default=0.75)
    max_clock_angle_std : float
        Maximum standard deviation of the clock angle in degrees (default=22.5)
    max_bmag_cv : float
        Maximum coefficient of variation of the IMF magnitude in the GSM
        Y-Z plane (default=0.5)

    Note
    ----
    Uses clock angle standard deviation and the coefficient of variation of
    the IMF magnitude in the GSM Y-Z plane

    """

    mm_omni.calculate_imf_steadiness(inst, steady_window=steady_window,
                                     min_window_frac=min_window_frac,
                                     max_clock_angle_std=max_clock_angle_std,
                                     max_bmag_cv=max_bmag_cv)
    return


@deprecated
def calculate_dayside_reconnection(inst):
    """Calculate the dayside reconnection rate (Milan et al. 2014).

    .. deprecated:: 0.0.4
    This function has been moved to `pysatNASA.instruments.methods.omni`.  This
    redirect will be removed in v0.1.0+.

    Parameters
    ----------
    inst : pysat.Instrument
        Instrument with OMNI HRO data, requires BYZ_GSM and clock_angle

    Note
    ----
    recon_day = 3.8 Re (Vx / 4e5 m/s)^1/3 Vx B_yz (sin(theta/2))^9/2

    """

    mm_omni.calculate_dayside_reconnection(inst)
    return
