# -*- coding: utf-8 -*-
"""Supports the GUVI instrument on TIMED.

Downloads data from the NASA Coordinated Data
Analysis Web (CDAWeb).

Supports two options for loading that may be
specified at instantiation.

Properties
----------
platform
    'timed'
name
    'guvi'
tag
    None
inst_id
    None supported

Note
----
- no tag required

Warnings
--------
- Currently no cleaning routine.


Example
-------
::

    import pysat
    ivm = pysat.Instrument(platform='timed', name='guvi', inst_id='l1c')
    ivm.download(dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 31))
    ivm.load(2020, 1)

Author
------
L. A. Navarro (luis.navarro@colorado.edu)

"""

import datetime as dt
import functools
import pandas as pds
import warnings

from pysat import logger
from pysat.instruments.methods import general as mm_gen

from pysatNASA.instruments.methods import cdaweb as cdw

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'timed'
name = 'guvi'
tags = {'': ''}
inst_ids = {'': [tag for tag in tags.keys()]}

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'': dt.datetime(2009, 1, 1)}}

# ----------------------------------------------------------------------------
# Instrument methods


def init(self):
    """Initializes the Instrument object with instrument specific values.

    Runs once upon instantiation.

    """

    rules_url = 'http://guvitimed.jhuapl.edu/home_guvi-datausage'
    ackn_str = ' '.join(('Please see the Rules of the Road at', rules_url))
    logger.info(ackn_str)
    self.acknowledgements = ackn_str
    self.references = ' '.join(('Paxton,L. J., Christensen, A. B., Humm, D. C., Ogorzalek,',
                                'B. S., Pardoe, C. T., Monison, D., Weiss, M. B., Cram, W.,',
                                'Lew, P. H., Mabry, D. J., Goldstena, J. O., Gary, A.,', 
                                'Persons, D. F., Harold, M. J., Alvarez, E. B., ErcoF, C. J.,',
                                'Strickland, D. J., Meng, C.-I.',
                                'Global ultraviolet imager (GUVI): Measuring composition and',
                                'energy inputs for the NASA Thermosphere Ionosphere Mesosphere',
                                'Energetics and Dynamics (TIMED) mission.',
                                'Optical spectroscopic techniques and instrumentation for atmospheric',
                                'and space research III. Vol. 3756. International Society for Optics',
                                'and Photonics, 1999.'))

    return


def clean(self):
    """Routine to return TIMED GUVI data cleaned to the specified level

    Note
    ----
    No cleaning currently available.

    """
    warnings.warn('no cleaning routines available for TIMED GUVI data')

    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
fname = 'timed_L1Cdisk_guvi_{year:04d}{month:02d}{day:02d}{hour:02d}{minute:02d}{second:02d}_v{version:02d}.cdf'
supported_tags = {'': {'': fname}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags,
                               file_cadence=pds.DateOffset(hours=1))

# Set the load routine
load = functools.partial(cdw.load, file_cadence=pds.DateOffset(hours=1))

# Set the download routine
basic_tag = {'remote_dir': ''.join(('/pub/data/timed/guvi/levels_v10/level1c/disk_cdf',
                                    '/{year:4d}/{month:02d}/')),
             'fname': fname}
download_tags = {'': {'': basic_tag}}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)
