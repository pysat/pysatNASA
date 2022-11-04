# -*- coding: utf-8 -*-
"""The DE2 IDM instrument.

Supports the Ion Drift Meter (IDM) instrument
on Dynamics Explorer 2 (DE2).

From CDAWeb (adapted):

This directory gathers data for the IDM instrument that flew on the DE 2 spacecraft
which was launched on 3 August 1981 into an elliptical orbit with an altitude range
of 300 km to 1000 km and re-entered the atmosphere on 19 February 1983.

(NSSDC ID: 81-070B-06D)
This data set provides the cross track ion drift with a time resolution of
125 milli-seconds for the time period from Aug 15, 1981 to Feb 16, 1983. The
ASCII version was generated at NSSDC from the originally PI-submitted binary
data.


References
----------
Heelis, R. A., W. B. Hanson, C. R. Lippincott, D. R. Zuccaro, L. L. Harmon,
B. J. Holt, J. E. Doherty, R. A. Power, The ion drift meter for Dynamics
Explorer-B, Space Sci. Instrum., 5, 511, 1981.

Properties
----------
platform
    'de2'
name
    'idm'
inst_id
    None Supported
tag
    None Supported

Warnings
--------
- Currently no cleaning routine.

"""

import datetime as dt
import functools

from pysat.instruments.methods import general as mm_gen

from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import de2 as mm_de2
from pysatNASA.instruments.methods import general as mm_nasa

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'de2'
name = 'idm'
tags = {'': '1 s cadence Neutral Atmosphere Composition Spectrometer data'}
inst_ids = {'': ['']}
pandas_format = False

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'': dt.datetime(1983, 1, 1)}}

# ----------------------------------------------------------------------------
# Instrument methods


# Use standard init routine
init = functools.partial(mm_nasa.init, module=mm_de2, name=name)

# No cleaning, use standard warning function instead
clean = mm_nasa.clean_warn

# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
fname = 'de2_vion250ms_idm_{year:04d}{month:02d}{day:02d}_v{version:02d}.cdf'
supported_tags = {'': {'': fname}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Use the default CDAWeb method
load = functools.partial(cdw.load, pandas_format=pandas_format)


def preprocess(self):
    """Apply DE2 IDM default attributes.

    Note
    ----
    Corrects the epoch names

    """

    self.data = self.data.rename({'record0': 'Epoch_velZ',
                                  'record1': 'Epoch_velY'})
    return


# Support download routine
basic_tag = {'remote_dir': ''.join(('/pub/data/de/de2/plasma_idm',
                                    '/vion250ms_cdaweb/{year:4d}/')),
             'fname': fname}
download_tags = {'': {'': basic_tag}}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Support listing files currently on CDAWeb
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)
