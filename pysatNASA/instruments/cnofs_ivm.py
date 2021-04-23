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

    # make sure all -999999 values are NaN
    self.data.replace(-999999., np.nan, inplace=True)

    # Set maximum flags
    if self.clean_level == 'clean':
        max_rpa_flag = 1
        max_dm_flag = 0
    elif self.clean_level == 'dusty':
        max_rpa_flag = 3
        max_dm_flag = 3
    else:
        max_rpa_flag = 4
        max_dm_flag = 6

    # Find bad drifts according to quality flags
    idm = self.data.driftMeterflag > max_dm_flag
    irpa = self.data.RPAflag > max_rpa_flag

    # Also exclude RPA drifts where the velocity is set to zero
    if (self.clean_level == 'clean') | (self.clean_level == 'dusty'):
        if 'ionVelocityX' in self.data.columns:
            # unrealistic velocities - value set by fit routine
            idx2 = (np.abs(self.data.ionVelocityX) == 0.0)
            irpa = (irpa | idx2)

    # Replace bad drift meter values with NaNs
    if len(idm) > 0:
        data_labels = ['ionVelocityY', 'ionVelocityZ']
        for label in data_labels:
            self[idm, label] = np.NaN
        # Only remove field-alligned drifts if DM component is large enough
        unit_vecs = {'ionVelmeridional': 'meridionalunitvectorY',
                     'ionVelparallel': 'parallelunitvectorY',
                     'ionVelzonal': 'zonalunitvectorY'}
        for label in unit_vecs:
            idx0 = idm & (np.abs(self[unit_vecs[label]]) >= 0.01)
            self[idx0, label] = np.NaN
        unit_vecs = {'ionVelmeridional': 'meridionalunitvectorZ',
                     'ionVelparallel': 'parallelunitvectorZ',
                     'ionVelzonal': 'zonalunitvectorZ'}
        for label in unit_vecs:
            idx0 = idm & (np.abs(self[unit_vecs[label]]) >= 0.01)
            self[idx0, label] = np.NaN

    # Replace bad rpa values with NaNs
    if len(irpa) > 0:
        data_labels = ['ionVelocityX', 'sensPlanePot', 'sensPlanePotvar']
        for label in data_labels:
            self[irpa, label] = np.NaN
        # Only remove field-alligned drifts if RPA component is large enough
        unit_vecs = {'ionVelmeridional': 'meridionalunitvectorX',
                     'ionVelparallel': 'parallelunitvectorX',
                     'ionVelzonal': 'zonalunitvectorX'}
        for label in unit_vecs:
            idx0 = irpa & (np.abs(self[unit_vecs[label]]) >= 0.01)
            self[idx0, label] = np.NaN

    # Replace densities and temps where fits are bad
    # This is separate from the drifts as confidence in the densities is higher
    irpa = self.data.RPAflag > 4
    if len(irpa) > 0:
        data_labels = ['Ni', 'ionDensity', 'ionDensityvariance',
                       'ionTemperature', 'ionTemperaturevariance',
                       'ion1fraction', 'ion1variance',
                       'ion2fraction', 'ion2variance',
                       'ion3fraction', 'ion3variance',
                       'ion4fraction', 'ion4variance',
                       'ion5fraction', 'ion5variance']
        for label in data_labels:
            self[irpa, label] = np.NaN

    # Additional checks for clean and dusty data
    if self.clean_level == 'dusty' or self.clean_level == 'clean':
        # Low O+ concentrations for RPA Flag of 3 are suspect
        # O+ concentration criteria from Burrell, 2012
        nO = self.data.ion1fraction * self.data.Ni
        ind_low_odens = (self.data.RPAflag == 3) & (nO <= 3.0e4)
        # 100% O+ creates a shallow fit region for the ram velocity
        ind_shallow_fit = self.data.ion1fraction >= 1.0
        # Exclude areas where either of these are true
        idx = ind_low_odens | ind_shallow_fit

        # Only remove data if RPA component of drift is greater than 1%
        unit_vecs = {'ionVelmeridional': 'meridionalunitvectorX',
                     'ionVelparallel': 'parallelunitvectorX',
                     'ionVelzonal': 'zonalunitvectorX'}
        for label in unit_vecs:
            idx0 = idx & (np.abs(self[unit_vecs[label]]) >= 0.01)
            self[idx0, label] = np.NaN

        # The RPA component of the ram velocity
        self[idx, 'ionVelocityX'] = np.NaN

        # Check for bad temperature fits (O+ < 15%), replace with NaNs
        # Criteria from Hairston et al, 2010
        idx = self.data.ion1fraction < 0.15
        self[idx, 'ionTemperature'] = np.NaN

        # The ion fractions should always sum to one and never drop below zero
        ifracs = ['ion{:d}fraction'.format(i) for i in np.arange(1, 6)]
        ion_sum = np.sum([self[label] for label in ifracs], axis=0)
        ion_min = np.min([self[label] for label in ifracs], axis=0)
        idx = ((ion_sum != 1.0) | (ion_min < 0.0))
        for label in ifracs:
            self[idx, label] = np.NaN

    # basic quality check on drifts and don't let UTS go above 86400.
    idx, = np.where(self.data.time <= 86400.)
    self.data = self[idx, :]

    # make sure MLT is between 0 and 24
    idx, = np.where((self.data.mlt >= 0) & (self.data.mlt <= 24.))
    self.data = self[idx, :]
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
