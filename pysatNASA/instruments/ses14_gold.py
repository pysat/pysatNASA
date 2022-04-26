"""Module for the SES14 GOLD instrument.

Supports the Nmax data product from the Global Observations of the Limb and
Disk (GOLD) satellite.  Accesses data in netCDF format.

Properties
----------
platform
    'ses14'
name
    'gold'
tag
    'nmax'

Warnings
--------
- The cleaning parameters for the instrument are still under development.
- strict_time_flag must be set to False


Examples
--------
::

    import datetime as dt
    import pysat
    nmax = pysat.Instrument(platform='ses14', name='gold', tag='nmax'
                            strict_time_flag=False)
    nmax.download(dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 31))
    nmax.load(2020, 1)


Authors
---------
Jeff Klenzing, Oct 06, 2020, Goddard Space Flight Center

"""

import datetime as dt
import functools
import pysat
import warnings
import xarray as xr

from pysat.instruments.methods import general as ps_gen
from pysat import logger
from pysat.utils import load_netcdf4

from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import gold as mm_gold

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'ses14'
name = 'gold'
tags = {'nmax': 'Level 2 Nmax data for the GOLD instrument'}
inst_ids = {'': ['nmax']}

pandas_format = False

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'nmax': dt.datetime(2020, 1, 1)}}

# ----------------------------------------------------------------------------
# Instrument methods


def init(self):
    """Initialize the Instrument object with instrument specific values.

    Runs once upon instantiation.

    Parameters
    -----------
    self : pysat.Instrument
        Instrument class object

    """

    logger.info(mm_gold.ack_str)
    logger.warning(' '.join(('Time stamps may be non-unique because Channel A',
                             'and B are different instruments.  An upgrade to',
                             'the pysat.Constellation object is required to',
                             'solve this issue. See pysat issue #614 for more',
                             'info.')))
    self.acknowledgements = mm_gold.ack_str
    self.references = mm_gold.ref_str

    return


def clean(self):
    """Clean SES14 GOLD data to the specified level.

    Routine is called by pysat, and not by the end user directly.

    Parameters
    -----------
    self : pysat.Instrument
        Instrument class object, whose attribute clean_level is used to return
        the desired level of data selectivity.

    Note
    ----
        Supports 'clean', 'dusty', 'dirty', 'none'

    """

    warnings.warn("Cleaning actions for GOLD Nmax are not yet implemented.")
    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the pysat and CDAWeb methods

# Set the list_files routine
fname = ''.join(('gold_l2_{tag:s}_{{year:04d}}_{{day:03d}}_v{{version:02d}}',
                 '_r{{revision:02d}}_c{{cycle:02d}}.nc'))
supported_tags = {inst_id: {tag: fname.format(tag=tag) for tag in tags.keys()}
                  for inst_id in inst_ids.keys()}
list_files = functools.partial(ps_gen.list_files,
                               supported_tags=supported_tags)

# Set the download routine
download_tags = {inst_id:
                 {tag: {'remote_dir': ''.join(('/pub/data/gold/level2/', tag,
                                               '/{year:4d}/')),
                        'fname': supported_tags[''][tag]}
                  for tag in tags.keys()} for inst_id in inst_ids.keys()}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)


def load(fnames, tag=None, inst_id=None):
    """Load GOLD NMAX data into `xarray.Dataset` and `pysat.Meta` objects.

    This routine is called as needed by pysat. It is not intended
    for direct user interaction.

    Parameters
    ----------
    fnames : array-like
        iterable of filename strings, full path, to data files to be loaded.
        This input is nominally provided by pysat itself.
    tag : string
        tag name used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself.
    inst_id : string
        Satellite ID used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself.
    **kwargs : extra keywords
        Passthrough for additional keyword arguments specified when
        instantiating an Instrument object. These additional keywords
        are passed through to this routine by pysat.

    Returns
    -------
    data : xr.Dataset
        An xarray Dataset with data prepared for the pysat.Instrument
    meta : pysat.Meta
        Metadata formatted for a pysat.Instrument object.

    Note
    ----
    - Any additional keyword arguments passed to pysat.Instrument
      upon instantiation are passed along to this routine.
    - Using scan_start_time as time dimesion for pysat compatibility, renames
      ``nscans`` dimension as ``time``.

    Examples
    --------
    ::

        inst = pysat.Instrument('gold', 'nmax')
        inst.load(2019, 1)

    """
    labels = {'units': ('units', str), 'name': ('long_name', str),
              'notes': ('notes', str), 'desc': ('desc', str),
              'plot': ('plot_label', str), 'axis': ('axis', str),
              'scale': ('scale', str),
              'min_val': ('value_min', float),
              'max_val': ('value_max', float),
              'fill_val': ('fill', float)}
    meta = pysat.Meta(labels=labels)

    data = []

    for path in fnames:

        idata = xr.load_dataset(path)

        if tag == 'nmax':
            # Add time coordinate from scan_start_time
            idata['time'] = ('nscans',
                            [dt.datetime.strptime(str(val), "b'%Y-%m-%dT%H:%M:%SZ'")
                             for val in idata['scan_start_time'].values])
            idata = idata.swap_dims({'nscans': 'time'})
            idata = idata.assign_coords({'nlats': idata['nlats'],
                                       'nlons': idata['nlons'],
                                       'nmask': idata['nmask'],
                                       'channel': idata['channel'],
                                       'hemisphere': idata['hemisphere']})

            data.append(idata)

    data = xr.concat(data, dim='time')

    return data, meta
