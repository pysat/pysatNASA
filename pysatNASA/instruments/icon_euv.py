#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3986131
#
# DISTRIBUTION STATEMENT A: Approved for public release. Distribution is
# unlimited.
# ----------------------------------------------------------------------------
# -*- coding: utf-8 -*-

"""Module for the ICON EUV instrument.

Supports the Extreme Ultraviolet (EUV) imager onboard the Ionospheric
CONnection Explorer (ICON) satellite.  Accesses local data in
netCDF format.

Properties
----------
platform
    'icon'
name
    'euv'
tag
    None supported
inst_id
    None Supported

Warnings
--------
- The cleaning parameters for the instrument are still under development.
- Only supports level-2 data.


Examples
--------
::

    import pysat
    euv = pysat.Instrument(platform='icon', name='euv')
    euv.download(dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 31))
    euv.load(2020, 1)

By default, pysat removes the ICON level tags from variable names, ie,
ICON_L27_Ion_Density becomes Ion_Density.  To retain the original names, use
::

    euv = pysat.Instrument(platform='icon', name='euv',
                           keep_original_names=True)

"""

import datetime as dt
import functools
import numpy as np

import pysat
from pysat.instruments.methods import general as mm_gen

from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import general as mm_nasa
from pysatNASA.instruments.methods import icon as mm_icon

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'icon'
name = 'euv'
tags = {'': 'Level 2 public geophysical data'}
inst_ids = {'': ['']}

pandas_format = False

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'': dt.datetime(2020, 1, 1)}}
# TODO(#218, #222): Remove when compliant with multi-day load tests
_new_tests = {'': {'': False}}
_test_load_opt = {'': {'': {'keep_original_names': True}}}

# ----------------------------------------------------------------------------
# Instrument methods


# Use standard init routine
init = functools.partial(mm_nasa.init, module=mm_icon, name=name)


def preprocess(self, keep_original_names=False):
    """Adjust epoch timestamps to datetimes and remove variable preambles.

    Parameters
    ----------
    keep_original_names : bool
        if True then the names as given in the netCDF ICON file
        will be used as is. If False, a preamble is removed. (default=False)

    """

    if not keep_original_names:
        mm_gen.remove_leading_text(self, target='ICON_L26_')
    return


def clean(self):
    """Clean ICON EUV data to the specified level.

    Note
    ----
        Supports 'clean', 'dusty', 'dirty', 'none'. Method is
        not called by pysat if clean_level is None or 'none'.

    """

    vars = ['HmF2', 'NmF2', 'Oplus']
    if 'Flag' in self.variables:
        icon_flag = 'Flag'
    else:
        icon_flag = 'ICON_L26_Flag'
        vars = ['ICON_L26_' + x for x in vars]

    max_val = {'clean': 1.0, 'dusty': 2.0}
    if self.clean_level in ['clean', 'dusty']:
        for var in vars:
            self[var] = self[var].where(self[icon_flag]
                                        <= max_val[self.clean_level])
    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the ICON and pysat methods

# Set the list_files routine
fname = ''.join(('icon_l2-6_euv_{year:04d}{month:02d}{day:02d}_',
                 'v{version:02d}r{revision:03d}.nc'))
supported_tags = {'': {'': fname}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the download routine
download_tags = {'': {'': 'ICON_L2-6_EUV'}}
download = functools.partial(cdw.cdas_download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.cdas_list_remote_files,
                                      supported_tags=download_tags)


def filter_metadata(meta_dict):
    """Filter EUV metadata to remove warnings during loading.

    Parameters
    ----------
    meta_dict : dict
        Dictionary of metadata from file

    Returns
    -------
    meta_dict : dict
        Filtered EUV metadata

    """
    vars = ['ICON_L26_Ancillary_Filename', 'ICON_L26_Flag_Details',
            'ICON_L26_Input_Filename', 'ICON_L26_Processing_Date',
            'ICON_L26_UTC_Time']

    for var in vars:
        if var in meta_dict:
            meta_dict[var]['FillVal'] = np.nan

    # Deal with string arrays
    for var in meta_dict.keys():
        if 'Var_Notes' in meta_dict[var]:
            meta_dict[var]['Var_Notes'] = ' '.join(pysat.utils.listify(
                meta_dict[var]['Var_Notes']))

    return meta_dict


def load(fnames, tag='', inst_id='', keep_original_names=False):
    """Load ICON EUV data into `xarray.Dataset` object and `pysat.Meta` objects.

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
    keep_original_names : bool
        If True then the names as given in the netCDF ICON file
        will be used as is. If False, a preamble is removed. (default=False)

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

    The 'Altitude' dimension is renamed as 'Alt' to avoid confusion with the
    'Altitude' variable when performing xarray operations

    Examples
    --------
    ::

        inst = pysat.Instrument('icon', 'euv', tag='', inst_id='a')
        inst.load(2020, 1)

    """
    labels = {'units': ('Units', str), 'name': ('Long_Name', str),
              'notes': ('Var_Notes', str), 'desc': ('CatDesc', str),
              'min_val': ('ValidMin', (int, float)),
              'max_val': ('ValidMax', (int, float)),
              'fill_val': ('FillVal', (int, float))}

    meta_translation = {'FieldNam': 'plot'}

    data, meta = pysat.utils.io.load_netcdf(fnames, epoch_name='Epoch',
                                            pandas_format=pandas_format,
                                            meta_kwargs={'labels': labels},
                                            meta_processor=filter_metadata,
                                            meta_translation=meta_translation,
                                            drop_meta_labels=['Valid_Max',
                                                              'Valid_Min',
                                                              '_FillValue'],
                                            decode_times=False)

    # xarray can't merge if variable and dim names are the same
    if 'Altitude' in data.dims:
        data = data.rename_dims(dims_dict={'Altitude': 'Alt'})
    return data, meta
