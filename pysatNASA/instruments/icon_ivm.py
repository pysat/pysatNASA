# -*- coding: utf-8 -*-

"""Supports the Ion Velocity Meter (IVM)
onboard the Ionospheric Connections (ICON) Explorer.

Properties
----------
platform
    'icon'
name
    'ivm'
tag
    None supported
inst_id
    'a' or 'b'

Example
-------
::

    import pysat
    ivm = pysat.Instrument(platform='icon', name='ivm', inst_id='a')
    ivm.download(dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 31))
    ivm.load(2020, 1)

By default, pysat removes the ICON level tags from variable names, ie,
ICON_L27_Ion_Density becomes Ion_Density.  To retain the original names, use
::

    ivm = pysat.Instrument(platform='icon', name='ivm', inst_id='a',
                           keep_original_names=True)

Author
------
R. A. Stoneback

"""

import datetime as dt
import functools
import numpy as np

import pysat
from pysat import logger
from pysat.instruments.methods import general as mm_gen
from pysatNASA.instruments.methods import icon as mm_icon

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'icon'
name = 'ivm'
tags = {'': 'Level 2 public geophysical data'}

# Note for developers: IVM-A and IVM-B face in opposite directions, and only
# one is expected to have geophysical data at a given time depending on ram
# direction. In general, IVM-A is operational when the remote instruments face
# northward, and IVM-B when the remote instruments face southward. IVM-B data
# is not available as of Jun 26 2020, as this mode has not yet been engaged.
# Bypassing tests and warning checks via the password_req flag
inst_ids = {'a': [''], 'b': ['']}


# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'a': {'': dt.datetime(2020, 1, 1)},
               'b': {'': dt.datetime(2020, 1, 1)}}  # IVM-B not yet engaged
_test_download_travis = {'a': {kk: False for kk in tags.keys()}}
_test_download = {'b': {kk: False for kk in tags.keys()}}
_password_req = {'b': {kk: True for kk in tags.keys()}}

# ----------------------------------------------------------------------------
# Instrument methods


def init(self):
    """Initializes the Instrument object with instrument specific values.

    Runs once upon instantiation.

    Parameters
    -----------
    inst : pysat.Instrument
        Instrument class object

    """

    logger.info(mm_icon.ackn_str)
    self.acknowledgements = mm_icon.ackn_str
    self.references = ''.join((mm_icon.refs['mission'],
                               mm_icon.refs['ivm']))

    return


def preprocess(self, keep_original_names=False):
    """Removes variable preambles.

    Parameters
    ----------
    keep_original_names : boolean
        if True then the names as given in the netCDF ICON file
        will be used as is. If False, a preamble is removed. (default=False)

    """

    if not keep_original_names:
        mm_gen.remove_leading_text(self, target='ICON_L27_')
    return


def clean(self):
    """Provides data cleaning based upon clean_level.

    Note
    ----
        Supports 'clean', 'dusty', 'dirty', 'none'

    """

    # IVM variable groupings
    drift_variables = ['Ion_Velocity_X', 'Ion_Velocity_Zonal',
                       'Ion_Velocity_Meridional',
                       'Ion_Velocity_Field_Aligned']
    cross_drift_variables = ['Ion_Velocity_Z', 'Ion_Velocity_Y']
    rpa_variables = ['Ion_Temperature', 'Ion_Density',
                     'Fractional_Ion_Density_H',
                     'Fractional_Ion_Density_O']
    if 'RPA_Flag' in self.variables:
        rpa_flag = 'RPA_Flag'
        dm_flag = 'DM_Flag'
    else:
        rpa_flag = 'ICON_L27_RPA_Flag'
        dm_flag = 'ICON_L27_DM_Flag'
        drift_variables = ['ICON_L27_' + x for x in drift_variables]
        cross_drift_variables = ['ICON_L27_' + x for x in cross_drift_variables]
        rpa_variables = ['ICON_L27_' + x for x in rpa_variables]

    if self.clean_level in ['clean', 'dusty']:
        # remove drift values impacted by RPA
        idx, = np.where(self[rpa_flag] >= 1)
        for var in drift_variables:
            self[idx, var] = np.nan
        # DM values
        idx, = np.where(self[dm_flag] >= 1)
        for var in cross_drift_variables:
            self[idx, var] = np.nan

    if self.clean_level == 'clean':
        # other RPA parameters
        idx, = np.where(self[rpa_flag] >= 2)
        for var in rpa_variables:
            self[idx, var] = np.nan

    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
aname = ''.join(('ICON_L2-7_IVM-A_{year:04d}-{month:02d}-{day:02d}_',
                 'v{version:02d}r{revision:03d}.NC'))
bname = ''.join(('ICON_L2-7_IVM-B_{year:04d}-{month:02d}-{day:02d}_',
                 'v{version:02d}r{revision:03d}.NC'))
supported_tags = {'a': {'': aname}, 'b': {'': bname}}

list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the download routine
basic_tag_a = {'remote_dir': '/pub/LEVEL.2/IVM-A',
               'remote_fname': ''.join(('ZIP/', aname[:-2], 'ZIP'))}
basic_tag_b = {'remote_dir': '/pub/LEVEL.2/IVM-B',
               'remote_fname': ''.join(('ZIP/', bname[:-2], 'ZIP'))}

download_tags = {'a': {'': basic_tag_a}, 'b': {'': basic_tag_b}}
download = functools.partial(mm_icon.ssl_download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(mm_icon.list_remote_files,
                                      supported_tags=download_tags)


def load(fnames, tag=None, inst_id=None, keep_original_names=False):
    """Loads ICON IVM data using pysat into pandas.

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

        inst = pysat.Instrument('icon', 'ivm', inst_id='a', tag='')
        inst.load(2020, 1)

    """

    return pysat.utils.load_netcdf4(fnames, epoch_name='Epoch',
                                    units_label='Units',
                                    name_label='Long_Name',
                                    notes_label='Var_Notes',
                                    desc_label='CatDesc',
                                    plot_label='FieldNam',
                                    axis_label='LablAxis',
                                    scale_label='ScaleTyp',
                                    min_label='ValidMin',
                                    max_label='ValidMax',
                                    fill_label='FillVal')
