# -*- coding: utf-8 -*-
"""Module for the DE2 LANG instrument.

Supports the Langmuir Probe (LANG) instrument on Dynamics Explorer 2 (DE2).

From CDAWeb:

The Langmuir Probe Instrument (LANG) was a cylindrical electrostatic probe that
obtained measurements of electron temperature, Te, and electron or ion
concentration, Ne or Ni, respectively, and spacecraft potential.  Data from
this investigation were used to provide temperature and density measurements
along magnetic field lines related to thermal energy and particle flows within
the magnetosphere-ionosphere system, to provide thermal plasma conditions for
wave-particle interactions, and to measure large-scale and fine-structure
ionospheric effects of energy deposition in the ionosphere.  The Langmuir Probe
instrument was identical to that used on the AE satellites and the Pioneer
Venus Orbiter. Two independent sensors were connected to individual adaptive
sweep voltage circuits which continuously tracked the changing electron
temperature and spacecraft potential, while autoranging electrometers adjusted
their gain in response to the changing plasma density. The control signals used
to achieve this automatic tracking provided a continuous monitor of the
ionospheric parameters without telemetering each volt-ampere (V-I) curve.
Furthermore, internal data storage circuits permitted high resolution, high
data rate sampling of selected V-I curves for transmission to ground to verify
or correct the inflight processed data. Time resolution was 0.5 seconds.


Properties
----------
platform
    'de2'
name
    'lang'
tag
    None Supported
inst_id
    None Supported


Warnings
--------
- Currently no cleaning routine.


References
----------
J. P. Krehbiel, L. H. Brace, R. F. Theis, W. H. Pinkus, and R. B. Kaplan,
"The Dynamics Explorer 2 Langmuir Probe (LANG)", Space Sci. Instrum., 5,
493-502, 1981.

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
name = 'lang'
tags = {'': '500 ms cadence Langmuir Probe data'}
inst_ids = {'': [tag for tag in tags.keys()]}

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {tag: dt.datetime(1983, 1, 1) for tag in tags.keys()}}

# ----------------------------------------------------------------------------
# Instrument methods


# Use standard init routine
init = functools.partial(mm_nasa.init, module=mm_de2, name=name)

# Use default clean
clean = mm_nasa.clean

# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
fname = 'de2_plasma500ms_lang_{year:04d}{month:02d}{day:02d}_v{version:02d}.cdf'
supported_tags = {'': {'': fname}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the load routine
load = cdw.load

# Set the download routine
download_tags = {'': {'': 'DE2_PLASMA500MS_LANG'}}
download = functools.partial(cdw.cdas_download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.cdas_list_remote_files,
                                      supported_tags=download_tags)
