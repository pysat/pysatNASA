# -*- coding: utf-8 -*-
"""Module for the TIMED TIDI instrument.

Supports the TIMED Doppler Interferometer (TIDI) instrument on the Thermosphere
Ionosphere Mesosphere Energetics Dynamics (TIMED) satellite data from the
NASA Coordinated Data Analysis Web (CDAWeb).

Properties
----------
platform
    'timed'
name
    'tidi'
tag
    ['profile','los','vector',]
inst_id
    ''
    'ncar'

Warnings
--------
- The cleaning parameters for the instrument are still under development.

Example
-------
::

    import pysat
    tidi = pysat.Instrument('timed', 'tidi', tag='vecetor',
                              inst_id='', clean_level='None')
    tidi.download(dt.datetime(2020, 1, 30), dt.datetime(2020, 1, 31))
    tidi.load(2020, 2)

::

"""

import datetime as dt
import functools
import numpy as np
import xarray as xr

from pysat.instruments.methods import general as mm_gen
from pysat.utils.io import load_netcdf

from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import general as mm_nasa
from pysatNASA.instruments.methods import timed as mm_timed

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'timed'
name = 'tidi'
tags = {'profile': 'Level 1 TIDI data',
        'los': 'Level 2 TIDI data',
        'vector': 'Level 3 TIDI data'}
inst_ids = {'': ['los', 'profile', 'vector'],
            'ncar': ['vector']}

pandas_format = False

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {jj: {kk: dt.datetime(2019, 1, 1) for kk in inst_ids[jj]}
               for jj in inst_ids.keys()}

# ----------------------------------------------------------------------------
# Instrument methods


# Use standard init routine
def init(self, module=mm_timed, name=name):
    """Initialization function to set parameters upon first import."""
    mm_nasa.init(self, module=module, name=name)

    # Same timing cold/warm for Michigan files.
    self.strict_time_flag = False
    # Set multi_file_day flag as needed
    if self.tag == 'vector':
        self.multi_file_day = True

    return

# No cleaning, use standard warning function instead
clean = mm_nasa.clean_warn

# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
fname = ''.join(('TIDI_PB_{{year:04d}}{{day:03d}}_P????_S????_',
                 'D{{version:03d}}_R{{revision:02d}}.{ext:s}{gz:s}'))
fname_ext = {'vector': 'VEC',
             'los': 'LOS',
             'profile': 'PRF'}
fname_ncar = ''.join(('timed_windvectorsncar_tidi_',
                      '{year:04d}{month:02d}{day:02d}',
                      '????_v??.cdf'))
supported_tags = {'': {tag: fname.format(ext=fname_ext[tag], gz='')
                       for tag in tags},
                  'ncar': {'vector': fname_ncar}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags,)


# Set the load routine
def load(fnames, tag='', inst_id=''):
    """Load TIMED TIDI data into `xarray.DataSet` and `pysat.Meta` objects.

    This routine is called as needed by pysat. It is not intended
    for direct user interaction.

    Parameters
    ----------
    fnames : array-like
        iterable of filename strings, full path, to data files to be loaded.
        This input is nominally provided by pysat itself.
    tag : str
        tag name used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself.
    inst_id : str
        Satellite ID used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself.

    Returns
    -------
    data : xr.DataSet
        A xarray DataSet with data prepared for the pysat.Instrument
    meta : pysat.Meta
        Metadata formatted for a pysat.Instrument object.

    Raises
    ------
    ValueError
        If temporal dimensions are not consistent

    Note
    ----
    Any additional keyword arguments passed to pysat.Instrument
    upon instantiation are passed along to this routine.

    Examples
    --------
    ::

        inst = pysat.Instrument('timed', 'tidi',
                                inst_id='', tag='vector')
        inst.load(2005, 179)

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
    if inst_id == 'ncar':
        if tag == 'vector':
            data, meta = cdw.load(fnames, tag, inst_id,
                                  pandas_format=True)
            data = data.to_xarray()
            data = data.rename(index='time')

    elif inst_id == '':
        data = []
        for fname in fnames:
            idata, meta = load_netcdf(fname, pandas_format=pandas_format,
                                      epoch_name='time', epoch_unit='s',
                                      epoch_origin='1980-01-06 00:00:00',
                                      meta_kwargs={'labels': labels},
                                      meta_translation=meta_translation,
                                      drop_meta_labels='FILLVAL',
                                      )
            data.append(idata)

        if tag in ['vector', 'profile']:
            _dim = 'nvec' if tag == 'vector' else 'nprofs'
            alt_retrieved = data[0].alt_retrieved
            for i, idata in enumerate(data):
                idata = idata.drop_vars('alt_retrieved')
                idata = idata.assign_coords(time=idata.time)
                data[i] = idata.rename({_dim: 'time'})
            data = xr.concat(data, 'time')
            data = data.assign_coords(alt=('nalts', alt_retrieved.data))
            data = data.rename(nalts='alt')
            data = data.sortby('time')

        elif tag == 'los':
            for i, idata in enumerate(data):
                idata = idata.assign_coords(time=idata.time)
                data[i] = idata.rename(nlos='time')

            hh = [t.drop_dims(['time', 'nrecs_size']) for t in data]
            names2avoid = list(hh[0].data_vars.keys())
            ff = [t.drop_dims(['time']).drop_vars(names2avoid) for t in data]
            ff = xr.concat(ff, 'nrecs_size')
            ee = [t.drop_dims(['nrecs_size']).drop_vars(names2avoid)
                    for t in data]
            ee = xr.concat(ee, 'time')
            data = xr.merge([ff, ee, hh[0]])

    return data, meta


# Set download tags.  Note that tlimb uses the general implementation, while
# other tags use the cdasws implementation.
url = '/pub/data/timed/tidi/{tag:s}/{{year:04d}}/'
download_tags = {'': {tag: {'remote_dir': url.format(tag=tag),
                            'zip_method': 'gz',
                            'fname': fname.format(ext=fname_ext[tag],
                                                  gz='.gz')}
                      for tag in tags.keys()},
                 'ncar': {'vector': 'TIMED_WINDVECTORSNCAR_TIDI'}}


# Set the download routine
def download(date_array, tag='', inst_id='', data_path=None):
    """Download NASA TIMED/TIDI data.

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

    if inst_id in ['ncar',]:
        cdw.cdas_download(date_array, tag=tag, inst_id=inst_id,
                          supported_tags=download_tags, data_path=data_path)
    else:
        cdw.download(date_array, tag=tag, inst_id=inst_id,
                     supported_tags=download_tags, data_path=data_path)


# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.cdas_list_remote_files,
                                      supported_tags=download_tags)
