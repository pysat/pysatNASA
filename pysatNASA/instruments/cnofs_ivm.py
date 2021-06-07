# -*- coding: utf-8 -*-
"""Supports the Ion Velocity Meter (IVM) onboard the Communication
and Navigation Outage Forecasting System (C/NOFS) satellite, part
of the Coupled Ion Netural Dynamics Investigation (CINDI). Downloads
data from the NASA Coordinated Data Analysis Web (CDAWeb) in CDF
format.

The IVM is composed of the Retarding Potential Analyzer (RPA) and
Drift Meter (DM). The RPA measures the energy of plasma along the
direction of satellite motion. By fitting these measurements
to a theoretical description of plasma the number density, plasma
composition, plasma temperature, and plasma motion may be determined.
The DM directly measures the arrival angle of plasma. Using the reported
motion of the satellite the angle is converted into ion motion along
two orthogonal directions, perpendicular to the satellite track.

References
----------
A brief discussion of the C/NOFS mission and instruments can be found at
de La Beaujardière, O., et al. (2004), C/NOFS: A mission to forecast
scintillations, J. Atmos. Sol. Terr. Phys., 66, 1573–1591,
doi:10.1016/j.jastp.2004.07.030.

Discussion of cleaning parameters for ion drifts can be found in:
Burrell, Angeline G., Equatorial topside magnetic field-aligned ion drifts
at solar minimum, The University of Texas at Dallas, ProQuest
Dissertations Publishing, 2012. 3507604.

Discussion of cleaning parameters for ion temperature can be found in:
Hairston, M. R., W. R. Coley, and R. A. Heelis (2010), Mapping the
duskside topside ionosphere with CINDI and DMSP, J. Geophys. Res.,115,
A08324, doi:10.1029/2009JA015051.


Properties
----------
platform
    'cnofs'
name
    'ivm'
tag
    None supported
inst_id
    None supported

Warnings
--------
- The sampling rate of the instrument changes on July 29th, 2010.
  The rate is attached to the instrument object as .sample_rate.

- The cleaning parameters for the instrument are still under development.

"""

import datetime as dt
import functools

import numpy as np

from pysat import logger
from pysat.instruments.methods import general as mm_gen

from pysatNASA.instruments.methods import cnofs as mm_cnofs
from pysatNASA.instruments.methods import cdaweb as cdw

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'cnofs'
name = 'ivm'
tags = {'': ''}
inst_ids = {'': ['']}

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'': dt.datetime(2009, 1, 1)}}

# ----------------------------------------------------------------------------
# Instrument methods


def init(self):
    """Initializes the Instrument object with instrument specific values.

    Runs once upon instantiation.

    """
    logger.info(mm_cnofs.ackn_str)
    self.acknowledgements = mm_cnofs.ackn_str
    self.references = '\n'.join((mm_cnofs.refs['mission'],
                                 mm_cnofs.refs['ivm']))

    return


def preprocess(self):
    """Apply C/NOFS IVM default attributes

    Note
    ----
    The sample rate for loaded data is attached at inst.sample_rate
    before any attached custom methods are executed.

    """

    self.sample_rate = 1.0 if self.date >= dt.datetime(2010, 7, 29) else 2.0
    return


def clean(self):
    """Routine to return C/NOFS IVM data cleaned to the specified level

    Note
    ----
    Supports 'clean', 'dusty', 'dirty'

    """

    # Make sure all -999999 values are NaN
    self.data = self.data.replace(-999999., np.nan)

    # Set maximum flags
    if self.clean_level == 'clean':
        max_rpa_flag = 1
        max_idm_flag = 0
    elif self.clean_level == 'dusty':
        max_rpa_flag = 3
        max_idm_flag = 3
    else:
        max_rpa_flag = 4
        max_idm_flag = 6

    # Find bad drifts according to quality flags
    idm_mask = self.data['driftMeterflag'] > max_idm_flag
    rpa_mask = self.data['RPAflag'] > max_rpa_flag

    # Also exclude RPA drifts where the velocity is set to zero
    if (self.clean_level == 'clean') or (self.clean_level == 'dusty'):
        if 'ionVelocityX' in self.data.columns:
            # Possible unrealistic velocities - value may be set to zero
            # in fit routine instead of using a flag
            vel_mask = self.data['ionVelocityX'] == 0.0
            rpa_mask = rpa_mask | vel_mask

    # Replace bad drift meter values with NaNs
    if idm_mask.any():
        data_labels = ['ionVelocityY', 'ionVelocityZ']
        for label in data_labels:
            self.data[label] = np.where(idm_mask, np.nan, self.data[label])

        # Only remove field-aligned drifts if IDM component is large enough
        unit_vecs = {'ionVelmeridional': 'meridionalunitvector',
                     'ionVelparallel': 'parallelunitvector',
                     'ionVelzonal': 'zonalunitvector'}
        for label in unit_vecs.keys():
            for coord in ['Y', 'Z']:
                coord_label = ''.join([unit_vecs[label], coord])
                vec_mask = idm_mask & (np.abs(self.data[coord_label]) >= 0.01)
                self.data[label] = np.where(vec_mask, np.nan, self.data[label])

    # Replace bad rpa values with NaNs
    if rpa_mask.any():
        data_labels = ['ionVelocityX', 'sensPlanePot', 'sensPlanePotvar']
        for label in data_labels:
            self.data[label] = np.where(rpa_mask, np.nan, self.data[label])

        # Only remove field-aligned drifts if RPA component is large enough
        unit_vecs = {'ionVelmeridional': 'meridionalunitvectorX',
                     'ionVelparallel': 'parallelunitvectorX',
                     'ionVelzonal': 'zonalunitvectorX'}
        for label in unit_vecs:
            vec_mask = rpa_mask & (np.abs(self.data[unit_vecs[label]]) >= 0.01)
            self.data[label] = np.where(vec_mask, np.nan, self.data[label])

    # Replace non-velocity data values where fits are bad. This test is
    # separate from the drifts, as confidence in the fitted values decreases
    # as the complexity increases. Densities are the most robust, followed by
    # composition and temperatures.
    rpa_mask = self.data['RPAflag'] > 4
    if rpa_mask.any():
        data_labels = ['Ni', 'ionDensity', 'ionDensityvariance',
                       'ionTemperature', 'ionTemperaturevariance',
                       'ion1fraction', 'ion1variance',
                       'ion2fraction', 'ion2variance',
                       'ion3fraction', 'ion3variance',
                       'ion4fraction', 'ion4variance',
                       'ion5fraction', 'ion5variance']
        for label in data_labels:
            self.data[label] = np.where(rpa_mask, np.nan, self.data[label])

    # Additional checks for clean and dusty data
    if self.clean_level == 'dusty' or self.clean_level == 'clean':
        # Low O+ concentrations for RPA Flag of 3 are suspect.  Apply the O+
        # concentration criteria from Burrell, 2012.  Using the ion density
        # from the RPA fit ('ionDensity') instead of the measurement from the
        # zero volt current ('Ni').
        n_oplus = self.data['ion1fraction'] * self.data['ionDensity']
        low_odens_mask = (self.data['RPAflag'] == 3) & (n_oplus <= 3.0e4)

        # 100% O+ creates a shallow fit region for the ram velocity
        shallow_fit_mask = self.data['ion1fraction'] >= 1.0

        # Exclude areas where either of these are true
        oplus_mask = low_odens_mask | shallow_fit_mask

        # Only remove data if RPA component of drift is greater than 1%
        unit_vecs = {'ionVelmeridional': 'meridionalunitvectorX',
                     'ionVelparallel': 'parallelunitvectorX',
                     'ionVelzonal': 'zonalunitvectorX'}
        for label in unit_vecs:
            omask = oplus_mask & (np.abs(self.data[unit_vecs[label]]) >= 0.01)
            self.data[label] = np.where(omask, np.nan, self.data[label])

        # Remove the RPA component of the ram velocity regardless of orientation
        self.data['ionVelocityX'] = np.where(oplus_mask, np.nan,
                                             self.data['ionVelocityX'])

        # Check for bad temperature fits (O+ < 15%), replace with NaNs.
        # Criteria from Hairston et al, 2010.
        oplus_mask = self.data['ion1fraction'] < 0.15
        self.data['ionTemperature'] = np.where(oplus_mask, np.nan,
                                               self.data['ionTemperature'])

        # The ion fractions should always sum to one and never drop below zero
        ifracs = ['ion{:d}fraction'.format(i) for i in np.arange(1, 6)]
        ion_sum = np.sum([self.data[label] for label in ifracs], axis=0)
        ion_min = np.min([self.data[label] for label in ifracs], axis=0)
        ion_mask = (ion_sum != 1.0) | (ion_min < 0.0)
        for label in ifracs:
            self.data[label] = np.where(ion_mask, np.nan, self.data[label])

    # Ensure the time in seconds of day doesn't go above 86400 and MLT is
    # between 0 and 24
    itime, = np.where((self.data.time <= 86400.0) & (self.data['mlt'] >= 0.0)
                      & (self.data['mlt'] <= 24.0))
    self.data = self[itime, :]  # Use pysat indexing to retrieve desired data

    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
fname = 'cnofs_cindi_ivm_500ms_{year:4d}{month:02d}{day:02d}_v{version:02d}.cdf'
supported_tags = {'': {'': fname}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the load routine
load = cdw.load

# Set the download routine
basic_tag = {'remote_dir': '/pub/data/cnofs/cindi/ivm_500ms_cdf/{year:4d}/',
             'fname': fname}
download_tags = {'': {'': basic_tag}}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)
