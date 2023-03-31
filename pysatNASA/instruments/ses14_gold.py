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

"""

import datetime as dt
import functools
import numpy as np

from pysat.instruments.methods import general as ps_gen
from pysat import logger
from pysat.utils.io import load_netcdf

from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import general as mm_nasa
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


# No cleaning, use standard warning function instead
clean = mm_nasa.clean_warn


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
download_tags = {'': {'nmax': 'GOLD_L2_NMAX'}}
download = functools.partial(cdw.cdas_download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.cdas_list_remote_files,
                                      supported_tags=download_tags)


def load(fnames, tag='', inst_id=''):
    """Load GOLD NMAX data into `xarray.Dataset` and `pysat.Meta` objects.

    This routine is called as needed by pysat. It is not intended
    for direct user interaction.

    Parameters
    ----------
    fnames : array-like
        iterable of filename strings, full path, to data files to be loaded.
        This input is nominally provided by pysat itself.
    tag : str
        Tag name used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default='')
    inst_id : str
        Instrument ID used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default='')
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

        inst = pysat.Instrument('ses14', 'gold', tag='nmax')
        inst.load(2019, 1)

    """

    labels = {'units': ('Units', str), 'name': ('Long_Name', str),
              'notes': ('Var_Notes', str), 'desc': ('CatDesc', str),
              'plot': ('plot', str), 'axis': ('axis', str),
              'scale': ('scale', str),
              'min_val': ('Valid_Min', np.float64),
              'max_val': ('Valid_Max', np.float64),
              'fill_val': ('fill', np.float64)}

    # Generate custom meta translation table. When left unspecified the default
    # table handles the multiple values for fill. We must recreate that
    # functionality in our table. The targets for meta_translation should
    # map to values in `labels` above.
    meta_translation = {'FIELDNAM': 'plot', 'LABLAXIS': 'axis',
                        'ScaleTyp': 'scale', 'VALIDMIN': 'Valid_Min',
                        'Valid_Min': 'Valid_Min', 'VALIDMAX': 'Valid_Max',
                        'Valid_Max': 'Valid_Max', '_FillValue': 'fill',
                        'FillVal': 'fill', 'TIME_BASE': 'time_base'}

    data, meta = load_netcdf(fnames, pandas_format=pandas_format,
                             epoch_name='nscans', labels=labels,
                             meta_translation=meta_translation,
                             drop_meta_labels='FILLVAL')

    if tag == 'nmax':
        # Add time coordinate from scan_start_time
        data['time'] = [dt.datetime.strptime(str(val), "b'%Y-%m-%dT%H:%M:%SZ'")
                        for val in data['scan_start_time'].values]
        data = data.sortby('time')

        # Update coordinates with dimensional data
        data = data.assign_coords({'nlats': data['nlats'],
                                   'nlons': data['nlons'],
                                   'nmask': data['nmask'],
                                   'channel': data['channel'],
                                   'hemisphere': data['hemisphere']})
        meta['time'] = {meta.labels.notes: 'Converted from scan_start_time'}
        meta['nlats'] = {meta.labels.notes: 'Index for latitude values'}
        meta['nlons'] = {meta.labels.notes: 'Index for longitude values'}
        meta['nmask'] = {meta.labels.notes: 'Index for mask values'}

    return data, meta
