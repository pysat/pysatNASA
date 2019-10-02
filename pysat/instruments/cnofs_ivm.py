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

A brief discussion of the C/NOFS mission and instruments can be found at
de La Beaujardière, O., et al. (2004), C/NOFS: A mission to forecast
scintillations, J. Atmos. Sol. Terr. Phys., 66, 1573–1591,
doi:10.1016/j.jastp.2004.07.030.

Parameters
----------
platform : string
    'cnofs'
name : string
    'ivm'
tag : string
    None supported
sat_id : string
    None supported

Warnings
--------
- The sampling rate of the instrument changes on July 29th, 2010.
  The rate is attached to the instrument object as .sample_rate.

- The cleaning parameters for the instrument are still under development.

"""
from __future__ import print_function
from __future__ import absolute_import

import functools

import numpy as np

import pysat

from .methods import nasa_cdaweb as cdw

platform = 'cnofs'
name = 'ivm'
tags = {'': ''}
sat_ids = {'': ['']}
test_dates = {'': {'': pysat.datetime(2009, 1, 1)}}


# support list files routine
# use the default CDAWeb method
fname = 'cnofs_cindi_ivm_500ms_{year:4d}{month:02d}{day:02d}_v01.cdf'
supported_tags = {'': {'': fname}}
list_files = functools.partial(cdw.list_files,
                               supported_tags=supported_tags)

# support load routine
# use the default CDAWeb method
load = cdw.load

# support download routine
# use the default CDAWeb method
basic_tag = {'dir': '/pub/data/cnofs/cindi/ivm_500ms_cdf',
             'remote_fname': '{year:4d}/' + fname,
             'local_fname': fname}
supported_tags = {'': {'': basic_tag}}
download = functools.partial(cdw.download, supported_tags)
# support listing files currently on CDAWeb
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=supported_tags)


def default(ivm):
    ivm.sample_rate = 1.0 if ivm.date >= pysat.datetime(2010, 7, 29) else 2.0


def clean(inst):
    """Routine to return C/NOFS IVM data cleaned to the specified level

    Parameters
    -----------
    inst : (pysat.Instrument)
        Instrument class object, whose attribute clean_level is used to return
        the desired level of data selectivity.

    Returns
    --------
    Void : (NoneType)
        data in inst is modified in-place.

    Notes
    --------
    Supports 'clean', 'dusty', 'dirty'

    """

    # make sure all -999999 values are NaN
    inst.data.replace(-999999., np.nan, inplace=True)

    # Set maximum flags
    if inst.clean_level == 'clean':
        max_rpa_flag = 1
        max_dm_flag = 0
    elif inst.clean_level == 'dusty':
        max_rpa_flag = 3
        max_dm_flag = 3
    else:
        max_rpa_flag = 4
        max_dm_flag = 6

    # First pass, keep good RPA fits
    idx, = np.where(inst.data.RPAflag <= max_rpa_flag)
    inst.data = inst[idx, :]

    # Second pass, find bad drifts, replace with NaNs
    idx, = np.where(inst.data.driftMeterflag > max_dm_flag)

    # Also exclude very large drifts and drifts where 100% O+
    if (inst.clean_level == 'clean') | (inst.clean_level == 'dusty'):
        try:
            # unrealistic velocities
            idx2, = np.where(np.abs(inst.data.ionVelmeridional) >= 10000.)
            idx = np.unique(np.concatenate((idx, idx2)))
        except AttributeError:
            pass

    if len(idx) > 0:
        drift_labels = ['ionVelmeridional', 'ionVelparallel', 'ionVelzonal',
                        'ionVelocityX', 'ionVelocityY', 'ionVelocityZ']
        for label in drift_labels:
            inst[label][idx] = np.NaN

    # Check for bad RPA fits in dusty regime.
    # O+ concentration criteria from Burrell, 2012
    # Shallow Fit region from Klenzing and Stoneback ????
    if (inst.clean_level == 'dusty'):
        # shallow fit region for vx
        idx, = np.where(inst.data.ion1fraction >= 1.0)
        # Low O+ concentrations for RPA Flag of 3 are suspect
        nO = inst.data.ion1fraction*inst.data.Ni
        idx2, = np.where((inst.data.RPAflag == 3) & (nO <= 3.0e4))
        idx = np.unique(np.concatenate((idx, idx2)))
        # However, only remove these if RPA component of drift is significant
        unit_vecs = {'ionVelmeridional': 'meridionalunitvectorX',
                     'ionVelparallel': 'parallelunitvectorX',
                     'ionVelzonal': 'zonalunitvectorX'}
        for label in unit_vecs:
            idx0, = np.where(np.abs(inst[unit_vecs[label]]) >= 0.01)
            idx0 = np.unique(np.concatenate((idx, idx0)))
            inst[label][idx0] = np.NaN

    # Check for bad temperature fits (O+ < 15%), replace with NaNs
    # Criteria from Hairston et al, 2015
    if (inst.clean_level == 'clean') | (inst.clean_level == 'dusty'):
        idx, = np.where(inst.data.ion1fraction < 0.15)
        inst['ionTemperature'][idx] = np.NaN

    # basic quality check on drifts and don't let UTS go above 86400.
    idx, = np.where(inst.data.time <= 86400.)
    inst.data = inst[idx, :]

    # make sure MLT is between 0 and 24
    idx, = np.where((inst.data.mlt >= 0) & (inst.data.mlt <= 24.))
    inst.data = inst[idx, :]
    return
