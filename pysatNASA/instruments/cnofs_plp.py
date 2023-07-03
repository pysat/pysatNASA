# -*- coding: utf-8 -*-
"""Module for the C/NOFS PLP instrument.

Supports the Planar Langmuir Probe (PLP) onboard the Communication
and Navigation Outage Forecasting System (C/NOFS) satellite. Downloads
data from the NASA Coordinated Data Analysis Web (CDAWeb).

Description from CDAWeb:

The Planar Langmuir Probe on C/NOFS is a suite of 2 current measuring sensors
mounted on the ram facing surface of the spacecraft.  The primary sensor is an
Ion Trap (conceptually similar to RPAs flown on many other spacecraft) capable
of measuring ion densities as low as 1 cm-3 with a 12 bit log electrometer.
The secondary senor is a swept bias planar Langmuir probe (Surface Probe)
capable of measuring Ne, Te, and spacecraft potential.

The ion number density is the one second average of the ion density sampled at
either 32, 256, 512, or 1024 Hz (depending on the mode).

The ion density standard deviation is the standard deviation of the samples
used to produce the one second average number density.

DeltaN/N is the detrened ion number density 1 second standard deviation divided
by the mean 1 sec density.

The electron density, electron temperature, and spacecraft potential are all
derived from a least squares fit to the current-bias curve from the Surface
Probe.

The data is PRELIMINARY, and as such, is intended for BROWSE PURPOSES ONLY.


Properties
----------
platform
    'cnofs'
name
    'plp'
tag
    None supported
inst_id
    None supported


Warnings
--------
- The data are PRELIMINARY, and as such, are intended for BROWSE PURPOSES ONLY.
- Currently no cleaning routine.
- Module not written by PLP team.


References
----------
A brief discussion of the C/NOFS mission and instruments can be found at
de La Beaujardière, O., et al. (2004), C/NOFS: A mission to forecast
scintillations, J. Atmos. Sol. Terr. Phys., 66, 1573–1591,
doi:10.1016/j.jastp.2004.07.030.

"""

import datetime as dt
import functools

from pysat.instruments.methods import general as mm_gen

from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import cnofs as mm_cnofs
from pysatNASA.instruments.methods import general as mm_nasa

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'cnofs'
name = 'plp'
tags = {'': ''}
inst_ids = {'': ['']}

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'': dt.datetime(2009, 1, 1)}}

# ----------------------------------------------------------------------------
# Instrument methods

# Use standard init routine
init = functools.partial(mm_nasa.init, module=mm_cnofs, name=name)


# Use default clean
clean = mm_nasa.clean


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
fname = ''.join(('cnofs_plp_plasma_1sec_{year:04d}{month:02d}{day:02d}',
                 '_v{version:02d}.cdf'))
supported_tags = {'': {'': fname}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the load routine
load = cdw.load

# Set the download routine
download_tags = {'': {'': 'CNOFS_PLP_PLASMA_1SEC'}}
download = functools.partial(cdw.cdas_download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.cdas_list_remote_files,
                                      supported_tags=download_tags)
