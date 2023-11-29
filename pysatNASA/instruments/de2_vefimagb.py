"""Module for the DE2 VEFI instrument.

From CDAWeb (adpated):
This directory gathers data for the VEFI and Magnetometer instruments that flew
on the DE 2 spacecraft which was launched on 3 August 1981 into an elliptical
orbit with an altitude range of 300 km to 1000 km and re-entered the atmosphere
on 19 February 1983.


References
----------
Maynard, N. C., E. A. Bielecki, H. G. Burdick, Instrumentation for vector
electric field measurements from DE-B, Space Sci. Instrum., 5, 523, 1981.

Properties
----------
platform
    'de2'
name
    'vefimagb'
tag
    'e', 'b'
inst_id
    none supported

Note
----
Electric and Magnetic fields have the same cadence, but different time indices.
Currently loads one index per instrument. Files kept in the same directory to
prevent duplication of downloads.

Examples
--------
::

    import datetime as dt
    import pysat

    # Set electric field instrument
    vefi = pysat.Instrument(platform='de2', name='vefimagb', tag='e')
    vefi.download(dt.datetime(1983, 1, 1))

    # Set magnetic field instrument
    mag = pysat.Instrument(platform='de2', name='vefimagb', tag='b')

    # Both instruments can be loaded from the same download
    vefi.load(1983, 1)
    mag.load(1983, 1)


"""

import datetime as dt
import functools
import os

import pysat
from pysat.instruments.methods import general as mm_gen
from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import de2 as mm_de2
from pysatNASA.instruments.methods import general as mm_nasa

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'de2'
name = 'vefimagb'
tags = {'e': '62 ms cadence Electric Field data',
        'b': '62 ms cadence Magnetometer data'}
inst_ids = {'': [tag for tag in tags.keys()]}

# Because both data products are stored in one file, tag not used
directory_format = os.path.join('{platform}', '{name}', '{inst_id}')

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {tag: dt.datetime(1983, 1, 1) for tag in tags.keys()}}


# ----------------------------------------------------------------------------
# Instrument methods

# Use standard init routine
init = functools.partial(mm_nasa.init, module=mm_de2, name='vefi')

# Use default clean
clean = mm_nasa.clean

# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
datestr = '{year:04d}{month:02d}{day:02d}_v{version:02d}'
fname = 'de2_62ms_vefimagb_{datestr:s}.cdf'
supported_tags = {'': {tag: fname.format(datestr=datestr)
                       for tag in tags.keys()}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)


# Set the load routine
def load(fnames, tag='', inst_id=''):
    """Load DE2 VEFI data.

    This routine is called as needed by pysat. It is not intended
    for direct user interaction.

    Parameters
    ----------
    fnames : array-like
        Iterable of filename strings, full path, to data files to be loaded.
        This input is nominally provided by pysat itself.
    tag : str
        Tag name used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default='')
    inst_id : str
        Instrument ID used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default='')

    Returns
    -------
    data : pds.DataFrame
        A pandas DataFrame with data prepared for the `pysat.Instrument`.
    meta : pysat.Meta
        Metadata formatted for a pysat.Instrument object.

    Note
    ----
    Several variables relating to time stored in different formats are dropped.
    These are redundant and complicate the load procedure.

    """

    # Select which epoch to use, drop the rest.
    if tag == 'b':
        epoch_name = 'mtimeEpoch'
        drop_dims = 'vtimeEpoch'
    elif tag == 'e':
        epoch_name = 'vtimeEpoch'
        drop_dims = 'mtimeEpoch'

    # Load and drop appropriate data.
    data, meta = cdw.load_xarray(fnames, tag=tag, inst_id=inst_id,
                                 epoch_name=epoch_name,
                                 drop_dims=drop_dims)
    # Convert to pandas.
    if hasattr(data, 'to_pandas'):
        data = data.to_pandas()
    else:
        # xarray 0.16 support required for operational server
        data = data.to_dataframe()

    return data, meta


# Set the download routine
download_tags = {'': {'e': 'DE2_62MS_VEFIMAGB',
                      'b': 'DE2_62MS_VEFIMAGB'}}
download = functools.partial(cdw.cdas_download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.cdas_list_remote_files,
                                      supported_tags=download_tags)
