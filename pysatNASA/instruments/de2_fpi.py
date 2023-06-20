# -*- coding: utf-8 -*-
"""The DE2 FPI instrument.

Supports the Fabry-Perot Interferometer (FPI) instrument on Dynamics Explorer 2
(DE2).

From CDAWeb:

The Fabry-Perot Interferometer (FPI) was a high-resolution remote sensing
instrument designed to measure the thermospheric temperature, meridional wind,
and density of the following metastable atoms: atomic oxygen (singlet S and D)
and the 2P state of ionic atomic oxygen. The FPI performed a wavelength analysis
on the light detected from the thermospheric emission features by spatially
scanning the interference fringe plane with a multichannel array detector. The
wavelength analysis characterized the Doppler line profile of the emitting
species. A sequential altitude scan performed by a commandable horizon scan
mirror provided a cross-sectional view of the thermodynamic and dynamic state of
the thermosphere below the DE 2 orbit. The information obtained from this
investigation was used to study the dynamic response of the thermosphere to the
energy sources caused by magnetospheric electric fields and the absorption of
solar ultraviolet light in the thermosphere. The instrument was based on the
visible airglow experiment (VAE) used in the AE program. The addition of a
scanning mirror, the Fabry-Perot etalon, an image plane detector, and a
calibration lamp were the principal differences. Interference filters isolated
lines at (in Angstroms) 5577, 6300, 7320, 5896, and 5200. The FPI had a field of
view of 0.53 deg (half-cone angle). More details are found in P. B. Hays et al.,
Space Sci. Instrum., v. 5, n. 4, p. 395, 1981. From February 16, 1982 to
September 11, 1982 the DE satellite was inverted and the FPI measured galactic
emissions.

Properties
----------
platform
    'de2'
name
    'fpi'
tag
    None Supported
inst_id
    None Supported


Warnings
--------
- Currently no cleaning routine.


References
----------
Hays, P B, Killeen, T L, and Kennedy, B C. "Fabry-Perot interferometer on
Dynamics Explorer". Space Sci. Instrum., 5, 395-416, 1981.

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
name = 'fpi'
tags = {'': '8 s cadence Fabry-Perot Interferometer data'}
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
fname = 'de2_neutral8s_fpi_{year:04d}{month:02d}{day:02d}_v{version:02d}.cdf'
supported_tags = {'': {'': fname}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Use the default CDAWeb method
load = cdw.load

# Support download routine
download_tags = {'': {'': 'DE2_NEUTRAL8S_FPI'}}
download = functools.partial(cdw.cdas_download, supported_tags=download_tags)

# Support listing files currently on CDAWeb
list_remote_files = functools.partial(cdw.cdas_list_remote_files,
                                      supported_tags=download_tags)
