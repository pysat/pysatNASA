"""Module for the DE2 VEFI instrument.

From CDAWeb (adpated):
This directory gathers data for the VEFI instrument that flew on the DE 2
spacecraft which was launched on 3 August 1981 into an elliptical orbit with
an altitude range of 300 km to 1000 km and re-entered the atmosphere on
19 February 1983.

dca   (NSSDC ID: 81-070B-02C)

This data set contains the averaged (2 samples per second) DC electric fields in
spacecraft coordinates and orbit information in ASCII format.

ac   (NSSDC ID: 81-070B-02E)

This data set contains the averaged AC electric field data (1 or 2 points per
second) and orbit information.

References
----------
Maynard, N. C., E. A. Bielecki, H. G. Burdick, Instrumentation for vector
electric field measurements from DE-B, Space Sci. Instrum., 5, 523, 1981.

Properties
----------
platform
    'de2'
name
    'vefi'
inst_id
    None Supported
tag
    'dca' or 'ac'


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
name = 'vefi'
tags = {'': '62 ms combination of Electric Field and Magnetometer',
        'dca': '500 ms cadence DC Averaged Electric Field data',
        'ac': '500 ms cadence AC Electric Field data'}
inst_ids = {'': [tag for tag in tags]}

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {tag: dt.datetime(1983, 1, 1) for tag in tags}}


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
datestr = '{year:04d}{month:02d}{day:02d}_v{version:02d}'
fid = {'': '62ms_vefimagb',
       'ac': 'ac500ms_vefi',
       'dca': 'dca500ms_vefi'}
fname = 'de2_{fid:s}_{datestr:s}.cdf'
supported_tags = {'': {tag: fname.format(fid=fid[tag], datestr=datestr)
                       for tag in tags}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the load routine
# Forcing use of cdflib as default since pysatCDF has a known issue with vefi
# data.  See pysat/pysatCDF#48
load = functools.partial(cdw.load, use_cdflib=True)

# Set the download routine
download_tags = {'': {'': 'DE2_62MS_VEFIMAGB',
                      'ac': 'DE2_AC500MS_VEFI',
                      'dca': 'DE2_DCA500MS_VEFI'}}
download = functools.partial(cdw.cdas_download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.cdas_list_remote_files,
                                      supported_tags=download_tags)
