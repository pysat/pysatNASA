# -*- coding: utf-8 -*-
"""Supports the Vector Electric Field Instrument (VEFI)
onboard the Communication and Navigation Outage Forecasting
System (C/NOFS) satellite. Downloads data from the
NASA Coordinated Data Analysis Web (CDAWeb).

Description from CDAWeb:

The DC vector magnetometer on the CNOFS spacecraft is a three axis, fluxgate
sensor with active thermal control situated on a 0.6m boom.  This magnetometer
measures the Earth's magnetic field using 16 bit A/D converters at 1 sample per
sec with a range of .. 45,000 nT.  Its primary objective on the CNOFS
spacecraft is to enable an accurate V x B measurement along the spacecraft
trajectory.  In order to provide an in-flight calibration of the magnetic field
data, we compare the most recent POMME model (the POtsdam Magnetic Model of the
Earth, http://geomag.org/models/pomme5.html) with the actual magnetometer
measurements to help determine a set of calibration parameters for the gains,
offsets, and non-orthogonality matrix of the sensor axes.  The calibrated
magnetic field measurements are provided in the data file here. The VEFI
magnetic field data file currently contains the following variables:
B_north   Magnetic field in the north direction
B_up      Magnetic field in the up direction
B_west    Magnetic field in the west direction

The data is PRELIMINARY, and as such, is intended for BROWSE PURPOSES ONLY.

References
----------
A brief discussion of the C/NOFS mission and instruments can be found at
de La Beaujardière, O., et al. (2004), C/NOFS: A mission to forecast
scintillations, J. Atmos. Sol. Terr. Phys., 66, 1573–1591,
doi:10.1016/j.jastp.2004.07.030.

Properties
----------
platform
    'cnofs'
name
    'vefi'
tag
    Select measurement type, one of {'dc_b'}
inst_id
    None supported


Note
----
- tag = 'dc_b': 1 second DC magnetometer data


Warnings
--------
- The data is PRELIMINARY, and as such, is intended for BROWSE PURPOSES ONLY.
- Limited cleaning routine.
- Module not written by VEFI team.

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
name = 'vefi'
tags = {'dc_b': 'DC Magnetometer data - 1 second'}
inst_ids = {'': ['dc_b']}

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'dc_b': dt.datetime(2009, 1, 1)}}

# ----------------------------------------------------------------------------
# Instrument methods


def init(self):
    """Initializes the Instrument object with instrument specific values.

    Runs once upon instantiation.

    """
    logger.info(mm_cnofs.ackn_str)
    self.acknowledgements = mm_cnofs.ackn_str
    self.references = '\n'.join((mm_cnofs.refs['mission'],
                                 mm_cnofs.refs['vefi']))

    return


def clean(self):
    """Routine to return VEFI data cleaned to the specified level

    Note
    ----
    'dusty' or 'clean' removes data when interpolation flag is set to 1
    'dirty' is the same as 'none'

    """

    if (self.clean_level == 'dusty') | (self.clean_level == 'clean'):
        idx, = np.where(self['B_flag'] == 0)
        self.data = self[idx, :]

    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
fname = ''.join(('cnofs_vefi_bfield_1sec_{year:04d}{month:02d}{day:02d}',
                 '_v{version:02d}.cdf'))
supported_tags = {'': {'dc_b': fname}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the load routine
load = cdw.load

# Set the download routine
basic_tag = {'remote_dir': '/pub/data/cnofs/vefi/bfield_1sec/{year:4d}/',
             'fname': fname}
download_tags = {'': {'dc_b': basic_tag}}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)
