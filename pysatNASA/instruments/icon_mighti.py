# -*- coding: utf-8 -*-
"""Supports the Michelson Interferometer for Global High-resolution
Thermospheric Imaging (MIGHTI) instrument onboard the Ionospheric
CONnection Explorer (ICON) satellite.  Accesses local data in
netCDF format.

Properties
----------
platform
    'icon'
name
    'mighti'
tag
    Supports 'los_wind_green', 'los_wind_red', 'vector_wind_green',
    'vector_wind_red', 'temperature'.  Note that not every data product
    available for every inst_id
inst_id
    'vector', 'a', or 'b'

Warnings
--------
- The cleaning parameters for the instrument are still under development.
- Only supports level-2 data.

Example
-------
::

    import pysat
    mighti = pysat.Instrument('icon', 'mighti', tag='vector_wind_green',
                              inst_id='vector', clean_level='clean')
    mighti.download(dt.datetime(2020, 1, 30), dt.datetime(2020, 1, 31))
    mighti.load(2020, 2)

By default, pysat removes the ICON level tags from variable names, ie,
ICON_L27_Ion_Density becomes Ion_Density.  To retain the original names, use
::

    mighti = pysat.Instrument(platform='icon', name='mighti',
                              tag='vector_wind_green', inst_id='vector',
                              clean_level='clean',
                              keep_original_names=True)

Authors
-------
Originated from EUV support.
Jeff Klenzing, Mar 17, 2018, Goddard Space Flight Center
Russell Stoneback, Mar 23, 2018, University of Texas at Dallas
Conversion to MIGHTI, Oct 8th, 2018, University of Texas at Dallas

Note
----
Currently red and green data products are bundled together in zip files on the
server.  This results in 'double downloading'.  This will be fixed once data is
transfered to SPDF.

"""

import datetime as dt
import functools

import pysat
from pysat import logger
from pysat.instruments.methods import general as mm_gen

from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import icon as mm_icon

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'icon'
name = 'mighti'
tags = {'los_wind_green': 'Line of sight wind data -- Green Line',
        'los_wind_red': 'Line of sight wind data -- Red Line',
        'vector_wind_green': 'Vector wind data -- Green Line',
        'vector_wind_red': 'Vector wind data -- Red Line',
        'temperature': 'Neutral temperature data'}
inst_ids = {'vector': ['vector_wind_green', 'vector_wind_red'],
            'a': ['los_wind_green', 'los_wind_red', 'temperature'],
            'b': ['los_wind_green', 'los_wind_red', 'temperature']}

pandas_format = False

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {jj: {kk: dt.datetime(2020, 1, 2) for kk in inst_ids[jj]}
               for jj in inst_ids.keys()}

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
                               mm_icon.refs['mighti']))

    return


def preprocess(self, keep_original_names=False):
    """Adjusts epoch timestamps to datetimes and removes variable preambles.

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
    """Provides data cleaning based upon clean_level.

    Note
    ----
        Supports 'clean', 'dusty', 'none'

    """

    def _clean_vars(var_list, flag, min_level):
        """Cleans parameters in a list according to standard flags

        Parameters
        ----------
        var_list : list of strings
            List of variables to be cleaned.  Must match variables present in
            the data set.
        flag : string
            The variable name to be used as the quality flag
        min_level : float
            The value at or above where we are confident in the data.  For
            MIGHTI, these are generally 0.5 or 1.0

        """
        for var in var_list:
            self[var] = self[var].where(self[flag] >= min_level)
        return

    if self.clean_level in ['clean', 'dusty']:
        if self.tag.find('los') >= 0:
            # Dealing with LOS winds
            wind_flag = 'Wind_Quality'
            ver_flag = 'VER_Quality'
            wind_vars = ['Line_of_Sight_Wind', 'Line_of_Sight_Wind_Error']
            ver_vars = ['Fringe_Amplitude', 'Fringe_Amplitude_Error',
                        'Relative_VER', 'Relative_VER_Error']
            if wind_flag not in self.variables:
                wind_flag = '_'.join(('ICON_L21', wind_flag))
                ver_flag = '_'.join(('ICON_L21', ver_flag))
                wind_vars = ['ICON_L21_' + var for var in wind_vars]
                ver_vars = ['ICON_L21_' + var for var in ver_vars]
            min_val = {'clean': 1.0, 'dusty': 0.5}

            # Find location with any of the flags set
            _clean_vars(wind_vars, wind_flag, min_val[self.clean_level])
            _clean_vars(ver_vars, ver_flag, min_val[self.clean_level])

        elif self.tag.find('vector') >= 0:
            # Vector winds area
            wind_flag = 'Wind_Quality'
            ver_flag = 'VER_Quality'
            wind_vars = ['Zonal_Wind', 'Zonal_Wind_Error',
                         'Meridional_Wind', 'Meridional_Wind_Error']
            ver_vars = ['Fringe_Amplitude', 'Fringe_Amplitude_Error',
                        'Relative_VER', 'Relative_VER_Error']
            if wind_flag not in self.variables:
                wind_flag = '_'.join(('ICON_L22', wind_flag))
                ver_flag = '_'.join(('ICON_L22', ver_flag))
                wind_vars = ['ICON_L22_' + var for var in wind_vars]
                ver_vars = ['ICON_L22_' + var for var in ver_vars]
            min_val = {'clean': 1.0, 'dusty': 0.5}

            # Find location with any of the flags set
            _clean_vars(wind_vars, wind_flag, min_val[self.clean_level])
            _clean_vars(ver_vars, ver_flag, min_val[self.clean_level])

        elif self.tag.find('temp') >= 0:
            # Neutral temperatures
            var = 'Temperature'
            saa_flag = 'Quality_Flag_South_Atlantic_Anomaly'
            cal_flag = 'Quality_Flag_Bad_Calibration'
            if saa_flag not in self.variables:
                id_str = self.inst_id.upper()
                saa_flag = '_'.join(('ICON_L1_MIGHTI', id_str, saa_flag))
                cal_flag = '_'.join(('ICON_L1_MIGHTI', id_str, cal_flag))
                var = '_'.join(('ICON_L23_MIGHTI', id_str, var))

            # Filter out areas with bad calibration data
            # as well as data marked in the SAA
            self[var] = self[var].where((self[saa_flag] == 0)
                                        & (self[cal_flag] == 0))
            # Filter out negative temperatures
            self[var] = self[var].where(self[var] > 0)

    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the ICON and pysat methods

# Set the list_files routine
datestr = '{year:04d}{month:02d}{day:02d}_v{version:02d}r{revision:03d}'
fname1 = 'icon_l2-1_mighti-{id:s}_los-wind-{color:s}_{date:s}.nc'
fname2 = 'icon_l2-2_mighti_vector-wind-{color:s}_{date:s}.nc'
fname3 = 'icon_l2-3_mighti-{id:s}_temperature_{date:s}.nc'
supported_tags = {'vector': {'vector_wind_green': fname2.format(color='green',
                                                                date=datestr),
                             'vector_wind_red': fname2.format(color='red',
                                                              date=datestr)},
                  'a': {'los_wind_green': fname1.format(id='a', color='green',
                                                        date=datestr),
                        'los_wind_red': fname1.format(id='a', color='red',
                                                      date=datestr),
                        'temperature': fname3.format(id='a', date=datestr)},
                  'b': {'los_wind_green': fname1.format(id='b', color='green',
                                                        date=datestr),
                        'los_wind_red': fname1.format(id='b', color='red',
                                                      date=datestr),
                        'temperature': fname3.format(id='b', date=datestr)}}

list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the download routine
dirstr1 = '/pub/data/icon/l2/l2-1_mighti-{{id:s}}_los-wind-{color:s}/'
dirstr2 = '/pub/data/icon/l2/l2-2_mighti_vector-wind-{color:s}/'
dirstr3 = '/pub/data/icon/l2/l2-3_mighti-{id:s}_temperature/'
dirnames = {'los_wind_green': dirstr1.format(color='green'),
            'los_wind_red': dirstr1.format(color='red'),
            'vector_wind_green': dirstr2.format(color='green'),
            'vector_wind_red': dirstr2.format(color='red'),
            'temperature': dirstr3}

download_tags = {}
for inst_id in supported_tags.keys():
    download_tags[inst_id] = {}
    for tag in supported_tags[inst_id].keys():
        fname = supported_tags[inst_id][tag]

        download_tags[inst_id][tag] = {
            'remote_dir': ''.join((dirnames[tag].format(id=inst_id),
                                   '{year:04d}/')),
            'fname': fname}

download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)


def load(fnames, tag=None, inst_id=None, keep_original_names=False):
    """Loads ICON FUV data using pysat into pandas.

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

    data, meta = pysat.utils.load_netcdf4(fnames, epoch_name='Epoch',
                                          pandas_format=pandas_format,
                                          labels=labels)

    # xarray can't merge if variable and dim names are the same
    if 'Altitude' in data.dims:
        data = data.rename_dims(dims_dict={'Altitude': 'Alt'})

    return data, meta
