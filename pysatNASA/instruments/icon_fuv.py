# -*- coding: utf-8 -*-
"""Module for the ICON FUV instrument.

Supports the Far Ultraviolet (FUV) imager onboard the Ionospheric
CONnection Explorer (ICON) satellite.  Accesses local data in
netCDF format.

Properties
----------
platform
    'icon'
name
    'fuv'
tag
    None supported

Warnings
--------
- The cleaning parameters for the instrument are still under development.
- Only supports level-2 data.

Example
-------
::

    import pysat
    fuv = pysat.Instrument(platform='icon', name='fuv', tag='day')
    fuv.download(dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 31))
    fuv.load(2020, 1)

By default, pysat removes the ICON level tags from variable names, ie,
ICON_L27_Ion_Density becomes Ion_Density.  To retain the original names, use
::

    fuv = pysat.Instrument(platform='icon', name='fuv', tag=day',
                           keep_original_names=True)

"""

import datetime as dt
import functools
import numpy as np
import warnings

import pysat
from pysat.instruments.methods import general as mm_gen

from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import icon as mm_icon

logger = pysat.logger

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'icon'
name = 'fuv'
tags = {'day': 'Level 2 daytime O/N2',
        'night': 'Level 2 nighttime O profile'}
inst_ids = {'': ['day', 'night']}

pandas_format = False

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {kk: dt.datetime(2020, 1, 1) for kk in tags.keys()}}

# ----------------------------------------------------------------------------
# Instrument methods


def init(self):
    """Initialize the Instrument object with instrument specific values.

    Runs once upon instantiation.

    Parameters
    -----------
    inst : pysat.Instrument
        Instrument class object

    """

    logger.info(mm_icon.ackn_str)
    self.acknowledgements = mm_icon.ackn_str
    self.references = ''.join((mm_icon.refs['mission'],
                               mm_icon.refs['fuv']))

    return


def preprocess(self, keep_original_names=False):
    """Adjust epoch timestamps to datetimes and remove variable preambles.

    Parameters
    ----------
    keep_original_names : boolean
        if True then the names as given in the netCDF ICON file
        will be used as is. If False, a preamble is removed. (default=False)

    """

    mm_gen.convert_timestamp_to_datetime(self, sec_mult=1.0e-3)
    if not keep_original_names:
        mm_icon.remove_preamble(self)
    return


def clean(self):
    """Clean ICON FUV data to the specified level.

    Note
    ----
        Supports 'clean', 'dusty', 'dirty', 'none'

    """

    logger.warning("Cleaning actions for ICON FUV are not yet defined.")
    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the ICON and pysat methods

# Set the list_files routine
fname24 = ''.join(('icon_l2-4_fuv_day_{year:04d}{month:02d}{day:02d}_',
                   'v{version:02d}r{revision:03d}.nc'))
fname25 = ''.join(('icon_l2-5_fuv_night_{year:04d}{month:02d}{day:02d}_',
                   'v{version:02d}r{revision:03d}.nc'))
supported_tags = {'': {'day': fname24, 'night': fname25}}

list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the download routine
basic_tag24 = {'remote_dir': '/pub/data/icon/l2/l2-4_fuv_day/{year:04d}/',
               'fname': fname24}
basic_tag25 = {'remote_dir': '/pub/data/icon/l2/l2-5_fuv_night/{year:04d}/',
               'fname': fname25}
download_tags = {'': {'day': basic_tag24, 'night': basic_tag25}}

download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)


def filter_metadata(meta_dict):
    """Filter FUV metadata to remove warnings during loading.

    Parameters
    ----------
    meta_dict : dict
        Dictionary of metadata from file.

    Returns
    -------
    dict
        Filtered FUV metadata.

    """

    vars = ['ICON_L24_UTC_Time', 'ICON_L25_Inversion_Method']
    for var in vars:
        if var in meta_dict:
            meta_dict[var]['FillVal'] = np.nan

    vars = ['ICON_L25_Start_Times', 'ICON_L25_Stop_Times', 'ICON_L25_UTC_Time']
    for var in vars:
        if var in meta_dict:
            meta_dict[var]['FillVal'] = np.nan
            meta_dict[var]['ValidMin'] = np.nan
            meta_dict[var]['ValidMax'] = np.nan

    # Deal with string arrays
    for var in meta_dict.keys():
        if 'Var_Notes' in meta_dict[var]:
            meta_dict[var]['Var_Notes'] = ' '.join(pysat.utils.listify(
                meta_dict[var]['Var_Notes']))

    return meta_dict


def load(fnames, tag=None, inst_id=None, keep_original_names=False):
    """Load ICON FUV data into xarray.Dataset object and pysat.Meta objects.

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
    keep_original_names : boolean
        if True then the names as given in the netCDF ICON file
        will be used as is. If False, a preamble is removed.

    Returns
    -------
    data : xr.Dataset
        An xarray Dataset with data prepared for the pysat.Instrument
    meta : pysat.Meta
        Metadata formatted for a pysat.Instrument object.

    Note
    ----
    Any additional keyword arguments passed to pysat.Instrument
    upon instantiation are passed along to this routine.

    Examples
    --------
    ::

        inst = pysat.Instrument('icon', 'fuv')
        inst.load(2020, 1)

    """
    labels = {'units': ('Units', str), 'name': ('Long_Name', str),
              'notes': ('Var_Notes', str), 'desc': ('CatDesc', str),
              'min_val': ('ValidMin', float),
              'max_val': ('ValidMax', float), 'fill_val': ('FillVal', float)}

    meta_translation = {'FieldNam': 'plot', 'LablAxis': 'axis',
                        'FIELDNAM': 'plot', 'LABLAXIS': 'axis',
                        'Bin_Location': 'bin_loc'}

    drop_labels = ['Valid_Max', 'Valid_Min', 'Valid_Range', 'SCALETYP',
                   'TYPE', 'CONTENT']

    data, meta = pysat.utils.io.load_netcdf(fnames, epoch_name='Epoch',
                                            pandas_format=pandas_format,
                                            labels=labels,
                                            meta_processor=filter_metadata,
                                            meta_translation=meta_translation,
                                            drop_meta_labels=drop_labels)
    return data, meta
