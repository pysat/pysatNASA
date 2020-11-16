"""Supports the Nmax data product from the Global Observations of the Limb and
Disk (GOLD) satellite.  Accesses data in netCDF format.

Properties
----------
platform
    'gold'
name
    'nmax'
tag
    None supported

Warnings
--------
- The cleaning parameters for the instrument are still under development.
- strict_time_flag must be set to False


Examples
--------
::

    import datetime as dt
    import pysat
    nmax = pysat.Instrument(platform='gold', name='nmax',
                            strict_time_flag=False)
    nmax.download(dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 31))
    nmax.load(2020, 1)


Authors
---------
Jeff Klenzing, Oct 06, 2020, Goddard Space Flight Center

"""

import datetime as dt
import functools
import warnings

import pysat
from pysat.instruments.methods import general as ps_gen
from pysatNASA.instruments.methods import gold as mm_gold
from pysatNASA.instruments.methods import cdaweb as cdw

platform = 'gold'
name = 'nmax'

tags = {'': 'Nmax data for the GOLD instrument'}
inst_ids = {'': ['']}
_test_dates = {'': {'': dt.datetime(2020, 1, 1)}}

fname = ''.join(('gold_l2_nmax_{year:04d}_{day:03d}_v{version:02d}',
                 '_r{revision:02d}_c{cycle:02d}.nc'))
supported_tags = {'': {'': fname}}
pandas_format = False

# use the CDAWeb methods list files routine
list_files = functools.partial(ps_gen.list_files,
                               supported_tags=supported_tags)

# support download routine
basic_tag = {'remote_dir': '/pub/data/gold/level2/nmax/{year:4d}/',
             'fname': fname}
download_tags = {'': {'': basic_tag}}
download = functools.partial(cdw.download, supported_tags=download_tags)

# support listing files currently on CDAWeb
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)


def init(self):
    """Initializes the Instrument object with instrument specific values.

    Runs once upon instantiation.

    Parameters
    -----------
    inst : pysat.Instrument
        Instrument class object

    """

    pysat.logger.info(mm_gold.ack_str)
    self.acknowledgements = mm_gold.ack_str
    self.references = mm_gold.ref_str

    pass


# Custom load routine for netcdf files
def load(fnames, tag=None, inst_id=None):
    """Loads GOLD NMAX data using pysat into xarray

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
    data, metadata
        Data and Metadata are formatted for pysat. Data is a pandas
        DataFrame while metadata is a pysat.Meta instance.

    Note
    ----
    Any additional keyword arguments passed to pysat.Instrument
    upon instantiation are passed along to this routine.

    Examples
    --------
    ::

        inst = pysat.Instrument('gold', 'nmax')
        inst.load(2019, 1)

    """

    data, mdata = pysat.utils.load_netcdf4(fnames, pandas_format=pandas_format)
    data['time'] = [dt.datetime.strptime(str(val), "b'%Y-%m-%dT%H:%M:%SZ'")
                    for val in data['scan_start_time'].values]

    return data, mdata


def clean(self):
    """Provides data cleaning based upon clean_level.

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
