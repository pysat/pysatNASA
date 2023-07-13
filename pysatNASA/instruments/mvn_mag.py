# -*- coding: utf-8 -*-
"""Module for the MAVEN mag instrument.
Created by: Teresa Esman, NPP at GSFC
Last editted: Jul 13, 2023
    May 24, 2023
    May 12, 2023 

Supports the Magnetometer (MAG) onboard the Mars Atmosphere and Volatile Evolution (MAVEN) satellite.  
Accesses local data in CDF format.
Downloads from CDAWeb. 

Properties
----------
platform
    'mvn'
name
    'mag'
tag
    None supported

Warnings
--------

- Only supports level-2 sunstate 1 second data.


Examples
--------
::

    import pysat
    from pysat.utils import registry
    registry.register_by_module(pysatNASA.instruments)
    
    
    mag = pysat.Instrument(platform='MAVEN', name='mag')
    mag.download(dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 31))
    mag.load(2020, 1, use_header = True)
"""

import datetime as dt
import functools
import numpy as np
import cdflib
import pysat
from pysat.instruments.methods import general as mm_gen
from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import general as mm_nasa
from pysatNASA.instruments.methods import mvn as mm_mvn

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'mvn'
name = 'mag'
tags = {'': 'l2'}
inst_ids = {'': ['']}

pandas_format = False

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'': dt.datetime(2020, 1, 1)}}
_test_load_opt = {'': {'': {'keep_original_names': True}}}

# ----------------------------------------------------------------------------
# Instrument methods


# Use standard init routine
init = functools.partial(mm_nasa.init, module=mm_mvn, name=name)


def preprocess(self, keep_original_names=False):
    """Adjust epoch timestamps to datetimes and remove variable preambles.

    Parameters
    ----------
    keep_original_names : bool
        if True then the names as given in the netCDF MAVEN file
        will be used as is. If False, a preamble is removed. (default=False)

    """

    if not keep_original_names:
        mm_gen.remove_leading_text(self, target='MAVEN_')
    return


def clean(self):
    """Clean MAVEN mag data to the specified level.

    Note
    ----
        Supports 'clean', 'dusty', 'dirty', 'none'. Method is
        not called by pysat if clean_level is None or 'none'.
        

    """

    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the CDAWeb and pysat methods

# Set the list_files routine
fname = ''.join(('mvn_mag_l2-sunstate-1sec_{year:04d}{month:02d}{day:02d}_',
                 'v{version:02d}_r{revision:02d}.cdf'))
supported_tags = {'': {'': fname}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the download routine
basic_tag = {'remote_dir': '/pub/data/maven/mag/l2/sunstate-1sec/cdfs/{year:04d}/{month:02d}',
             'fname': fname}
download_tags = {'': {'': basic_tag}}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)


def filter_metadata(meta_dict):
    """Filter mag metadata to remove warnings during loading.

    Parameters
    ----------
    meta_dict : dict
        Dictionary of metadata from file

    Returns
    -------
    meta_dict : dict
        Filtered mag metadata

    """
    vars = ['time', 'DDAY', 'OB_B_x', 'OB_B_y','OB_B_z', 'OB_B_range', 
            'POSN_x','POSN_y','POSN_z', 'OB_BDPL_x','OB_BDPL_y','OB_BDPL_z',
            'OB_BDPL_range']

    for var in vars:
        if var in meta_dict:
            meta_dict[var]['FillVal'] = np.nan

    # Deal with string arrays
    for var in meta_dict.keys():
        if 'Var_Notes' in meta_dict[var]:
            meta_dict[var]['Var_Notes'] = ' '.join(pysat.utils.listify(
                meta_dict[var]['Var_Notes']))

    return meta_dict

def init(self):
    """Initialize the Instrument object with instrument specific values.
    Runs once upon instantiation.
    Parameters
    -----------
    self : pysat.Instrument
        Instrument class object
    """

    pysat.logger.info(mm_mvn.ackn_str)
    self.acknowledgements = mm_mvn.ackn_str
    self.references = mm_mvn.references

    return

def load(fnames, tag='', inst_id='', keep_original_names=False):
    """Load MAVEN mag data into `xarray.Dataset` object and `pysat.Meta` objects.

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
        If True then the names as given in the netCDF MAVEN file
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


    Examples
    --------
    ::

        inst = pysat.Instrument('mvn', 'mag')
        inst.load(2020, 1)

    """
          
          
    data = cdflib.cdf_to_xarray(fnames[0])      

    meta = []
    
    xdata = mm_mvn.scrub_mvn_mag(data)
    # mm_mvn.scrub_mvn_mag switches the type to xarray

    # Add meta here
    header_data = mm_mvn.generate_header(data)
    meta = mm_mvn.generate_metadata(header_data,data)
    
    data = xdata

    return data,meta
