# -*- coding: utf-8 -*-
"""The DE2 NACS instrument.

Supports the Neutral Atmosphere Composition Spectrometer (NACS) instrument
on Dynamics Explorer 2 (DE2).

From CDAWeb:

The Neutral Atmosphere Composition Spectrometer (NACS) was designed to obtain
in situ measurements of the neutral atmospheric composition and to study the
variations of the neutral atmosphere in response to energy coupled into it from
the magnetosphere.  Because temperature enhancements, large-scale circulation
cells, and wave propagation are produced by energy input (each of which
posseses a specific signature in composition variation), the measurements
permitted the study of the partition, flow, and deposition of energy from the
magnetosphere. Specifically, the investigation objective was to characterize
the composition of the neutral atmosphere with particular emphasis on
variability in constituent densities driven by interactions in the atmosphere,
ionosphere, and magnetosphere system. The quadrupole mass spectrometer used was
nearly identical to those flown on the AE-C, -D, and -E missions. The electron-
impact ion source was used in a closed mode. Atmospheric particles entered an
antechamber through a knife-edged orifice, where they were thermalized to the
instrument temperature. The ions with the selected charge-to-mass ratios had
stable trajectories through the hyperbolic electric field, exited the analyzer,
and entered the detection system. An off-axis beryllium-copper dynode
multiplier operating at a gain of 2.E6 provided an output pulse of electrons
for each ion arrival. The detector output had a pulse rate proportional to the
neutral density in the ion source of the selected mass. The instrument also
included two baffles that scanned across the input orifice for optional
measurement of the zonal and vertical components of the neutral wind. The mass
select system provided for 256 mass values between 0 and 51 atomic mass units
(u) or each 0.2 u. It was possible to call any one of these mass numbers into
each of eight 0.016-s intervals. This sequence was repeated each 0.128 s.

This data set includes daily files of the PI-provided DE-2 NACS 1-second data
and corresponding orbit parameters.  The data set was generated at NSSDC from
the original PI-provided data and software (SPTH-00010) and from the
orbit/attitude database and software that is part of the DE-2 UA data set
(SPIO-00174). The original NACS data were provided by the PI team in a highly
compressed VAX/VMS binary format on magnetic tapes. The data set covers the
whole DE-2 mission time period. Each data point is an average over the normally
8 measurements per second. Densities and relative errors are provided for
atomic oxygen (O), molecular nitrogen (N2), helium (He), atomic nitrogen (N),
and argon (Ar).  The data quality is generally quite good below 500 km, but
deteriorates towards higher altitudes as oxygen and molecular nitrogen approach
their background values (which could only be determined from infrequent
spinning orbits) and the count rate for Ar becomes very low. The difference
between minimum (background) and maximum count rate for atomic nitrogen
(estimated from mass 30) was so small that results are generally poor.  Data
were lost between 12 March 1982 and 31 March 1982 when the counter overflowed.


References
----------
G. R. Carrignan, B. P. Block, J. C. Maurer,  A. E. Hedin, C. A. Reber,
N. W. Spencer, "The neutral mass spectrometer on Dynamics Explorer B",
Space Sci. Instrum., 5, 429-441, 1981.

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
pandas_format=False

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
