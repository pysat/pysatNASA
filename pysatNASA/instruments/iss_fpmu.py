# -*- coding: utf-8 -*-
"""Module for the ISS FPMU instrument.

Supports the Floating Potential Measurement Unit
(FPMU) instrument onboard the International Space
Station (ISS). Downloads data from the NASA
Coordinated Data Analysis Web (CDAWeb).

Properties
----------
platform
    'iss'
name
    'fpmu'
tag
    None Supported
inst_id
    None supported

Warnings
--------
- Currently clean only replaces fill values with Nans.
- Module not written by FPMU team.

"""

import datetime as dt
import functools

from pysat.instruments.methods import general as mm_gen
from pysat import logger

from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import general as mm_nasa

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'iss'
name = 'fpmu'
tags = {'': ''}
inst_ids = {'': ['']}

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'': dt.datetime(2017, 10, 1)}}

# ----------------------------------------------------------------------------
# Instrument methods


def init(self):
    """Initialize the Instrument object with instrument specific values.

    Runs once upon instantiation.

    """

    ackn_str = ' '.join(('Data provided through NASA CDAWeb.  Contact',
                         'Rob.Suggs@nasa.gov for support and use.'))
    logger.info(ackn_str)
    self.acknowledgements = ackn_str
    self.references = ' '.join(('V. N. Coffey et al., "Validation of the',
                                'Plasma Densities and Temperatures From',
                                'the ISS Floating Potential Measurement',
                                'Unit," in IEEE Transactions on Plasma',
                                'Science, vol. 36, no. 5, pp. 2301-2308,',
                                'Oct. 2008,',
                                'doi: 10.1109/TPS.2008.2004271.\n',
                                'A. Barjatya, C.M. Swenson, D.C.',
                                'Thompson, and K.H. Wright Jr., Data',
                                'analysis of the Floating Potential',
                                'Measurement Unit aboard the',
                                'International Space Station, Rev. Sci.',
                                'Instrum. 80, 041301 (2009),',
                                'https://doi.org/10.1063/1.3116085'))

    return


# Use default clean
clean = mm_nasa.clean


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
fname = 'iss_sp_fpmu_{year:04d}{month:02d}{day:02d}_v{version:02d}.cdf'
supported_tags = {'': {'': fname}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the load routine
load = cdw.load

# Set the download routine
download_tags = {'': {'': 'ISS_SP_FPMU'}}
download = functools.partial(cdw.cdas_download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.cdas_list_remote_files,
                                      supported_tags=download_tags)
