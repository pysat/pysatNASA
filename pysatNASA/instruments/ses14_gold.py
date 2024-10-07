#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3986131
#
# DISTRIBUTION STATEMENT A: Approved for public release. Distribution is
# unlimited.
# ----------------------------------------------------------------------------
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
    'tlimb'
    'tdisk'
    'o2den'
inst_id
    None Supported

Warnings
--------
- The cleaning parameters for the instrument are still under development.
- Loading multiple days of data requires a bugfix in pysat 3.1.0 or higher.

Note
----
In roughly 0.3% of daily files, Channel A and Channel B scans begin at the same
time.  One microsecond is added to Channel B to ensure uniqueness in the xarray
index.  The nominal scan rate for each channel is every 30 minutes.

Examples
--------
::

    import datetime as dt
    import pysat
    nmax = pysat.Instrument(platform='ses14', name='gold', tag='nmax')
    nmax.download(dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 31))
    nmax.load(2020, 1)

"""

import datetime as dt
import functools
import numpy as np

from pysat.instruments.methods import general as ps_gen
from pysat.utils.io import load_netcdf

from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import general as mm_nasa
from pysatNASA.instruments.methods import ses14 as mm_gold

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'ses14'
name = 'gold'
tags = {'nmax': 'Level 2 max dens data for the GOLD instrument',
        'tlimb': 'Level 2 limb temp data for the GOLD instrument',
        'tdisk': 'Level 2 disk temp data for the GOLD instrument',
        'o2den': 'Level 2 O2 dens data for the GOLD instrument'}
inst_ids = {'': [tag for tag in tags.keys()]}

pandas_format = False

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {tag: dt.datetime(2020, 1, 1) for tag in tags.keys()}}
_clean_warn = {inst_id: {tag: mm_nasa.clean_warnings
                         for tag in inst_ids[inst_id]}
               for inst_id in inst_ids.keys()}

# ----------------------------------------------------------------------------
# Instrument methods

init = functools.partial(mm_nasa.init, module=mm_gold, name=name)

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

# Set download tags.  Note that tlimb uses the general implementation, while
# other tags use the cdasws implementation.
download_tags = {'': {'tlimb': {'remote_dir': ''.join(('/pub/data/gold/',
                                                       'level2/tlimb',
                                                       '/{year:4d}/')),
                                'fname': supported_tags['']['tlimb']},
                      'nmax': 'GOLD_L2_NMAX',
                      'o2den': 'GOLD_L2_O2DEN',
                      'tdisk': 'GOLD_L2_TDISK'}}


# Set the download routine
def download(date_array, tag='', inst_id='', data_path=None):
    """Download NASA GOLD data.

    This routine is intended to be used by pysat instrument modules supporting
    a particular NASA CDAWeb dataset.

    Parameters
    ----------
    date_array : array-like
        Array of datetimes to download data for. Provided by pysat.
    tag : str
        Data product tag (default='')
    inst_id : str
        Instrument ID (default='')
    data_path : str or NoneType
        Path to data directory.  If None is specified, the value previously
        set in Instrument.files.data_path is used.  (default=None)

    """

    if tag == 'tlimb':
        cdw.download(date_array, tag=tag, inst_id=inst_id,
                     supported_tags=download_tags, data_path=data_path)
    else:
        cdw.cdas_download(date_array, tag=tag, inst_id=inst_id,
                          supported_tags=download_tags, data_path=data_path)


# Set the list_remote_files routine
def list_remote_files(tag='', inst_id='', start=None, stop=None,
                      series_out=True):
    """List every file for remote GOLD data.

    This routine is intended to be used by pysat instrument modules supporting
    a particular NASA CDAWeb dataset.

    Parameters
    ----------
    tag : str
        Data product tag (default='')
    inst_id : str
        Instrument ID (default='')
    start : dt.datetime or NoneType
        Starting time for file list. A None value will start with the first
        file found. (default=None)
    stop : dt.datetime or NoneType
        Ending time for the file list.  A None value will stop with the last
        file found. (default=None)
    series_out : bool
        Boolean to determine output type. True for pandas series of file names,
        and False for a list of the full web address. (default=True)

    Returns
    -------
    file_list : pds.Series or list
        A Series or list (if tag is not 'tlimb' and `series_out` is False)
        containing the verified available files

    """

    if tag == 'tlimb':
        file_list = cdw.list_remote_files(tag=tag, inst_id=inst_id,
                                          start=start, stop=stop,
                                          supported_tags=download_tags)
    else:
        file_list = cdw.cdas_list_remote_files(tag=tag, inst_id=inst_id,
                                               start=start, stop=stop,
                                               supported_tags=download_tags,
                                               series_out=series_out)
    return file_list


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

    if tag in ['nmax', 'tdisk', 'tlimb']:
        epoch_name = 'nscans'

    elif tag == 'o2den':
        epoch_name = 'nevents'

    data, meta = load_netcdf(fnames, pandas_format=pandas_format,
                             epoch_name=epoch_name,
                             meta_kwargs={'labels': labels},
                             meta_translation=meta_translation,
                             combine_by_coords=False,
                             drop_meta_labels='FILLVAL',
                             decode_times=False)

    if tag in ['nmax', 'tdisk', 'tlimb']:
        # Add time coordinate from scan_start_time
        time = [dt.datetime.strptime(str(val), "b'%Y-%m-%dT%H:%M:%SZ'")
                for val in data['scan_start_time'].values]

        # Add a delta of 1 microsecond for channel B.
        delta_time = [1 if ch == b'CHB' else 0 for ch in data['channel'].values]
        data['time'] = [time[i] + dt.timedelta(microseconds=delta_time[i])
                        for i in range(0, len(time))]

        # Sort times to ensure monotonic increase.
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

    elif tag == 'o2den':

        # Removing extra variables
        if len(data['zret'].dims) > 1:
            data['zret'] = data['zret'].isel(time=0)
            data['zdat'] = data['zdat'].isel(time=0)

        # Add time coordinate from utc_time
        data['time'] = [dt.datetime.strptime(str(val),
                        "b'%Y-%m-%dT%H:%M:%S.%fZ'")
                        for val in data['time_utc'].values]

        # Add retrieval altitude values and data tangent altitude values
        data = data.swap_dims({"nzret": "zret", "nzdat": "zdat"})

        # Update coordinates with dimensional data
        data = data.assign_coords({'zret': data['zret'],
                                   'zdat': data['zdat'],
                                   'n_wavelength': data['n_wavelength'],
                                   'channel': data['channel']})
        meta['time'] = {meta.labels.notes: 'Converted from time_utc'}
        meta['zret'] = {meta.labels.notes: ''.join(('Index for retrieval',
                                                    ' altitude values'))}
        meta['zdat'] = {meta.labels.notes: ''.join(('Index for data tangent',
                                                    ' altitude values'))}

    return data, meta
