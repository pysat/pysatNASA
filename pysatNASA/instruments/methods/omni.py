# -*- coding: utf-8 -*-
"""Module for the OMNI HRO supporting functions."""


import numpy as np
import pandas as pds
from scipy import stats

import pysat


def time_shift_to_magnetic_poles(inst):
    """Shift OMNI times to intersection with the magnetic pole.

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

    # Need to fill in Vx to get an estimate of what is going on.
    inst['Vx'] = inst['Vx'].interpolate('nearest')
    inst['Vx'] = inst['Vx'].fillna(method='backfill')
    inst['Vx'] = inst['Vx'].fillna(method='pad')

    inst['BSN_x'] = inst['BSN_x'].interpolate('nearest')
    inst['BSN_x'] = inst['BSN_x'].fillna(method='backfill')
    inst['BSN_x'] = inst['BSN_x'].fillna(method='pad')

    # Make sure there are no gaps larger than a minute.
    inst.data = inst.data.resample('1T').interpolate('time')

    time_x = inst['BSN_x'] * 6371.2 / -inst['Vx']
    idx, = np.where(np.isnan(time_x))
    if len(idx) > 0:
        pysat.logger.info(time_x[idx])
        pysat.logger.info(time_x)
    time_x_offset = [pds.DateOffset(seconds=time)
                     for time in time_x.astype(int)]
    new_index = []
    for i, time in enumerate(time_x_offset):
        new_index.append(inst.data.index[i] + time)
    inst.data.index = new_index
    inst.data = inst.data.sort_index()

    return


def calculate_clock_angle(inst):
    """Calculate IMF clock angle and magnitude of IMF in GSM Y-Z plane.

    Parameters
    -----------
    inst : pysat.Instrument
        Instrument with OMNI HRO data

    """

    # Calculate clock angle in degrees
    clock_angle = np.degrees(np.arctan2(inst['BY_GSM'], inst['BZ_GSM']))
    clock_angle[clock_angle < 0.0] += 360.0
    inst['clock_angle'] = pds.Series(clock_angle, index=inst.data.index)

    # Calculate magnitude of IMF in Y-Z plane
    inst['BYZ_GSM'] = pds.Series(np.sqrt(inst['BY_GSM']**2
                                         + inst['BZ_GSM']**2),
                                 index=inst.data.index)

    return


def calculate_imf_steadiness(inst, steady_window=15, min_window_frac=0.75,
                             max_clock_angle_std=(90.0 / np.pi),
                             max_bmag_cv=0.5):
    """Calculate IMF steadiness and add parameters to instrument data.

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

    # We are not going to interpolate through missing values
    rates = {'': 1, '1min': 1, '5min': 5}
    sample_rate = int(rates[inst.tag])
    max_wnum = np.floor(steady_window / sample_rate)
    if max_wnum != steady_window / sample_rate:
        steady_window = int(max_wnum * sample_rate)
        pysat.logger.warning(" ".join(("sample rate is not a factor of the",
                                       "statistical window")))
        pysat.logger.warning(" ".join(("new statistical window is",
                                       "{:.1f}".format(steady_window))))

    min_wnum = int(np.ceil(max_wnum * min_window_frac))

    # Calculate the running coefficient of variation of the BYZ magnitude
    byz_mean = inst['BYZ_GSM'].rolling(min_periods=min_wnum, center=True,
                                       window=steady_window).mean()
    byz_std = inst['BYZ_GSM'].rolling(min_periods=min_wnum, center=True,
                                      window=steady_window).std()
    inst['BYZ_CV'] = pds.Series(byz_std / byz_mean, index=inst.data.index)

    # Calculate the running circular standard deviation of the clock angle
    circ_kwargs = {'high': 360.0, 'low': 0.0, 'nan_policy': 'omit'}
    ca_std = inst['clock_angle'].rolling(min_periods=min_wnum,
                                         window=steady_window,
                                         center=True).apply(stats.circstd,
                                                            kwargs=circ_kwargs,
                                                            raw=True)
    inst['clock_angle_std'] = pds.Series(ca_std, index=inst.data.index)

    # Determine how long the clock angle and IMF magnitude are steady
    imf_steady = np.zeros(shape=inst.data.index.shape)

    steady = False
    for i, cv in enumerate(inst.data['BYZ_CV']):
        if steady:
            del_min = int((inst.data.index[i]
                           - inst.data.index[i - 1]).total_seconds() / 60.0)
            if np.isnan(cv) or np.isnan(ca_std[i]) or del_min > sample_rate:
                # Reset the steadiness flag if fill values are encountered, or
                # if an entry is missing
                steady = False

        if cv <= max_bmag_cv and ca_std[i] <= max_clock_angle_std:
            # Steadiness conditions have been met
            if steady:
                imf_steady[i] = imf_steady[i - 1]

            imf_steady[i] += sample_rate
            steady = True

    inst['IMF_Steady'] = pds.Series(imf_steady, index=inst.data.index)
    return


def calculate_dayside_reconnection(inst):
    """Calculate the dayside reconnection rate (Milan et al. 2014).

    Parameters
    ----------
    inst : pysat.Instrument
        Instrument with OMNI HRO data, requires BYZ_GSM and clock_angle

    Note
    ----
    recon_day = 3.8 Re (Vx / 4e5 m/s)^1/3 Vx B_yz (sin(theta/2))^9/2

    """

    rearth = 6371008.8  # Earth radius in m
    sin_htheta = np.power(np.sin(np.radians(0.5 * inst['clock_angle'])), 4.5)
    byz = inst['BYZ_GSM'] * 1.0e-9  # Convert from nT to T
    vx = inst['flow_speed'] * 1000.0  # Convert to m/s from km/s

    recon_day = 3.8 * rearth * vx * byz * sin_htheta * np.power((vx / 4.0e5),
                                                                1.0 / 3.0)
    inst['recon_day'] = pds.Series(recon_day, index=inst.data.index)
    return
