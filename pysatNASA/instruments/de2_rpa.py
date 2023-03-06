# -*- coding: utf-8 -*-
"""Module for the DE2 RPA instrument.

Supports the Retarding Potential Analyzer (RPA) instrument on Dynamics
Explorer 2 (DE2).

From CDAWeb:

The Retarding Potential Analyzer (RPA) measured the bulk ion velocity in the
direction of the spacecraft motion, the constituent ion concentrations, and the
ion temperature along the satellite path. These parameters were derived from a
least squares fit to the ion number flux vs energy curve obtained by sweeping
or stepping the voltage applied to the internal retarding grids of the RPA. In
addition, a separate wide aperture sensor, a duct sensor, was flown to measure
the spectral characteristics of iregularities in the total ion concentration.
The measured parameters obtained from this investigation were important to the
understanding of mechanisms that influence the plasma; i.e., to understand the
coupling between the solar wind and the earth's atmosphere. The measurements
were made with a multigridded planar retarding potential analyzer very similar
in concept and geometry to the instruments carried on the AE satellites. The
retarding potential was variable in the range from approximately +32 to 0 V.
The details of this voltage trace, and whether it was continuous or stepped,
depended on the operating mode of the instrument. Specific parameters deduced
from these measurements were ion temperature; vehicle potential; ram component
of the ion drift velocity; the ion and electron concentration irregularity
spectrum; and the concentration of H+, He+, O+, and Fe+, and of molecular ions
near perigee.

It includes the DUCT portion of the high resolutiondata from the Dynamics
Explorer 2 (DE-2) Retarding Potential Analyzer (RPA) for the whole DE-2 mission
time period in ASCII format. This version was generated at NSSDC from the
PI-provided binary data (SPIO-00232). The DUCT files include RPA measurements
ofthe total ion concentration every 64 times per second. Due to a failure in
the instrument memory system RPA data are not available from 81317 06:26:40 UT
to 82057 13:16:00 UT. This data set is based on the revised version of the RPA
files that was submitted by the PI team in June of 1995. The revised RPA data
include a correction to the spacecraft potential.


Properties
----------
platform
    'de2'
name
    'rpa'
inst_id
    None Supported
tag
    None Supported


Warnings
--------
- Currently no cleaning routine.


References
----------
W. B. Hanson, R. A. Heelis, R. A. Power, C. R. Lippincott, D. R. Zuccaro,
B. J. Holt, L. H. Harmon, and S. Sanatani, “The retarding potential analyzer
for dynamics explorer-B,” Space Sci. Instrum. 5, 503–510 (1981).

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
name = 'rpa'
tags = {'': '2 sec cadence RPA data'}  # this is the default cadence
inst_ids = {'': ['']}

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
fname = 'de2_ion2s_rpa_{year:04d}{month:02d}{day:02d}_v{version:02d}.cdf'
supported_tags = {'': {'': fname}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the load routine
load = cdw.load

# Set the download routine
basic_tag = {'remote_dir': ''.join(('/pub/data/de/de2/plasma_rpa',
                                    '/ion2s_cdaweb/{year:4d}/')),
             'fname': fname}
download_tags = {'': {'': basic_tag}}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)
