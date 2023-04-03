# -*- coding: utf-8 -*-
"""Provides default routines for NASA CDAWeb instruments into pysat.

Note
----
Adding new CDAWeb datasets should only require mininal user intervention.

"""

import cdflib
import datetime as dt
import numpy as np
import os
import pandas as pds
import requests
import warnings
import xarray as xr

from bs4 import BeautifulSoup
from cdasws import CdasWs

import pysat
from pysat.instruments.methods import general
from pysat import logger
from pysat.utils import files as futils
from pysat.utils import io
from pysatNASA.instruments.methods import CDF as libCDF

try:
    import pysatCDF
    auto_CDF = pysatCDF.CDF
except ImportError:
    auto_CDF = libCDF


def try_inst_dict(inst_id, tag, supported_tags):
    """Check that the inst_id and tag combination is valid.

    Parameters
    ----------
    tag : str
        Data product tag (default='')
    inst_id : str
        Instrument ID (default='')
    supported_tags : dict
        dict of dicts. Keys are supported tag names for download. Value is
        a dict with 'remote_dir', 'fname'. Inteded to be
        pre-set with functools.partial then assigned to new instrument code.
        (default=None)

    Returns
    -------
    inst_dict : dict or str
        dictionary containing file location in spdf archive, or dataset ID for
        cdasws
    """
    try:
        inst_dict = supported_tags[inst_id][tag]
    except KeyError:
        raise ValueError('inst_id / tag combo unknown.')

    return inst_dict


def load(fnames, tag='', inst_id='', file_cadence=dt.timedelta(days=1),
         flatten_twod=True, pandas_format=True, epoch_name='Epoch',
         meta_processor=None, meta_translation=None, drop_meta_labels=None,
         use_cdflib=None):
    """Load NASA CDAWeb CDF files.

    Parameters
    ----------
    fnames : pandas.Series
        Series of filenames
    tag : str
        Data product tag (default='')
    inst_id : str
        Instrument ID (default='')
    file_cadence : dt.timedelta or pds.DateOffset
        pysat assumes a daily file cadence, but some instrument data files
        contain longer periods of time.  This parameter allows the specification
        of regular file cadences greater than or equal to a day (e.g., weekly,
        monthly, or yearly). (default=dt.timedelta(days=1))
    flatted_twod : bool
        Flattens 2D data into different columns of root DataFrame rather
        than produce a Series of DataFrames. (default=True)
    pandas_format : bool
        Flag specifying if data is stored in a pandas DataFrame (True) or
        xarray Dataset (False). (default=True)
    epoch_name : str or NoneType
        Data key for epoch variable.  The epoch variable is expected to be an
        array of integer or float values denoting time elapsed from an origin
        specified by `epoch_origin` with units specified by `epoch_unit`. This
        epoch variable will be converted to a `DatetimeIndex` for consistency
        across pysat instruments.  (default='Epoch')
    meta_processor : function or NoneType
        If not None, a dict containing all of the loaded metadata will be
        passed to `meta_processor` which should return a filtered version
        of the input dict. The returned dict is loaded into a pysat.Meta
        instance and returned as `meta`. (default=None)
    meta_translation : dict or NoneType
        Translation table used to map metadata labels in the file to
        those used by the returned `meta`. Keys are labels from file
        and values are labels in `meta`. Redundant file labels may be
        mapped to a single pysat label. If None, will use
        `default_from_netcdf_translation_table`. This feature
        is maintained for compatibility. To disable all translation,
        input an empty dict. (default={})
    drop_meta_labels : list or NoneType
        List of variable metadata labels that should be dropped. Applied
        to metadata as loaded from the file. (default=None)
    use_cdflib : bool or NoneType
        If True, force use of cdflib for loading. If False, prevent use of
        cdflib for loading. If None, will use pysatCDF if available with
        cdflib as fallback. Only appropriate for `pandas_format=True`.
        (default=None)

    Returns
    -------
    data : pandas.DataFrame
        Object containing satellite data
    meta : pysat.Meta
        Object containing metadata such as column names and units

    Note
    ----
    This routine is intended to be used by pysat instrument modules supporting
    a particular NASA CDAWeb dataset

    """

    if pandas_format:
        data, meta = load_pandas(fnames, tag=tag, inst_id=inst_id,
                                 file_cadence=file_cadence,
                                 flatten_twod=flatten_twod,
                                 use_cdflib=use_cdflib)
    else:
        if not use_cdflib:
            estr = 'The `use_cdflib` option is not currently enabled for xarray'
            warnings.warn(estr)

        data, meta = load_xarray(fnames, tag=tag, inst_id=inst_id,
                                 epoch_name=epoch_name,
                                 file_cadence=file_cadence,
                                 meta_processor=meta_processor,
                                 meta_translation=meta_translation,
                                 drop_meta_labels=drop_meta_labels)
    return data, meta


def load_pandas(fnames, tag='', inst_id='', file_cadence=dt.timedelta(days=1),
                flatten_twod=True, use_cdflib=None):
    """Load NASA CDAWeb CDF files into a pandas DataFrame.

    Parameters
    ----------
    fnames : pandas.Series
        Series of filenames
    tag : str
        Data product tag (default='')
    inst_id : str
        Instrument ID (default='')
    file_cadence : dt.timedelta or pds.DateOffset
        pysat assumes a daily file cadence, but some instrument data files
        contain longer periods of time.  This parameter allows the specification
        of regular file cadences greater than or equal to a day (e.g., weekly,
        monthly, or yearly). (default=dt.timedelta(days=1))
    flatted_twod : bool
        Flattens 2D data into different columns of root DataFrame rather
        than produce a Series of DataFrames. (default=True)
    use_cdflib : bool or NoneType
        If True, force use of cdflib for loading. If False, prevent use of
        cdflib for loading. If None, will use pysatCDF if available with
        cdflib as fallback. (default=None)

    Returns
    -------
    data : pandas.DataFrame
        Object containing satellite data
    meta : pysat.Meta
        Object containing metadata such as column names and units

    Note
    ----
    This routine is intended to be used by pysat instrument modules supporting
    a particular NASA CDAWeb dataset.

    Examples
    --------
    ::

        # within the new instrument module, at the top level define
        # a new variable named load, and set it equal to this load method
        # code below taken from cnofs_ivm.py.

        # support load routine
        # use the default CDAWeb method
        load = cdw.load

    """

    # Load data from any files provided
    if len(fnames) <= 0:
        return pds.DataFrame(None), None
    else:
        if use_cdflib is not None:
            if use_cdflib:
                # Using cdflib wrapper to load the CDF and format data and
                # metadata for pysat using some assumptions.
                CDF = libCDF
            else:
                # Using pysatCDF to load the CDF and format data and
                # metadata for pysat using some assumptions.
                CDF = pysatCDF.CDF
        else:
            CDF = auto_CDF

        ldata = []
        for lfname in fnames:
            if not general.is_daily_file_cadence(file_cadence):
                # Parse out date from filename
                fname = lfname[0:-11]
                date = dt.datetime.strptime(lfname[-10:], '%Y-%m-%d')

                with CDF(fname) as cdf:
                    # Convert data to pysat format. Depending upon
                    # your needs the resulting pandas DataFrame may need
                    # modification.
                    try:
                        tdata, meta = cdf.to_pysat(flatten_twod=flatten_twod)

                        # Select data from multi-day down to daily
                        date2 = date + dt.timedelta(days=1)
                        date2 -= dt.timedelta(microseconds=1)
                        tdata = tdata.loc[date:date2, :]
                        ldata.append(tdata)
                    except ValueError as verr:
                        logger.warn("unable to load {:}: {:}".format(fname,
                                                                     str(verr)))
            else:
                # Basic data return
                with CDF(lfname) as cdf:
                    try:
                        temp_data, meta = cdf.to_pysat(
                            flatten_twod=flatten_twod)
                        ldata.append(temp_data)
                    except ValueError as verr:
                        logger.warn("unable to load {:}: {:}".format(lfname,
                                                                     str(verr)))

        # Combine individual files together
        if len(ldata) > 0:
            data = pds.concat(ldata)

        return data, meta


def load_xarray(fnames, tag='', inst_id='',
                file_cadence=dt.timedelta(days=1),
                labels={'units': ('Units', str), 'name': ('Long_Name', str),
                        'notes': ('Var_Notes', str), 'desc': ('CatDesc', str),
                        'min_val': ('ValidMin', float),
                        'max_val': ('ValidMax', float),
                        'fill_val': ('FillVal', float)},
                epoch_name='Epoch', meta_processor=None,
                meta_translation=None, drop_meta_labels=None):
    """Load NASA CDAWeb CDF files into an xarray Dataset.

    Parameters
    ----------
    fnames : pandas.Series
        Series of filenames
    tag : str
        Data product tag (default='')
    inst_id : str
        Instrument ID (default='')
    file_cadence : dt.timedelta or pds.DateOffset
        pysat assumes a daily file cadence, but some instrument data files
        contain longer periods of time.  This parameter allows the specification
        of regular file cadences greater than or equal to a day (e.g., weekly,
        monthly, or yearly). (default=dt.timedelta(days=1))
    labels : dict
        Dict where keys are the label attribute names and the values are tuples
        that have the label values and value types in that order.
        (default={'units': ('units', str), 'name': ('long_name', str),
        'notes': ('notes', str), 'desc': ('desc', str),
        'min_val': ('value_min', np.float64),
        'max_val': ('value_max', np.float64),
        'fill_val': ('fill', np.float64)})
    epoch_name : str
        Data key for epoch variable.  The epoch variable is expected to be an
        array of integer or float values denoting time elapsed from an origin
        specified by `epoch_origin` with units specified by `epoch_unit`. This
        epoch variable will be converted to a `DatetimeIndex` for consistency
        across pysat instruments.  (default='Epoch')
    meta_processor : function or NoneType
        If not None, a dict containing all of the loaded metadata will be
        passed to `meta_processor` which should return a filtered version
        of the input dict. The returned dict is loaded into a pysat.Meta
        instance and returned as `meta`. (default=None)
    meta_translation : dict or NoneType
        Translation table used to map metadata labels in the file to
        those used by the returned `meta`. Keys are labels from file
        and values are labels in `meta`. Redundant file labels may be
        mapped to a single pysat label. If None, will use
        `default_from_netcdf_translation_table`. This feature
        is maintained for compatibility. To disable all translation,
        input an empty dict. (default=None)
    drop_meta_labels : list or NoneType
        List of variable metadata labels that should be dropped. Applied
        to metadata as loaded from the file. (default=None)

    Returns
    -------
    data : xarray.Dataset
        Class holding file data
    meta : pysat.Meta
        Object containing metadata such as column names and units

    Note
    ----
    This routine is intended to be used by pysat instrument modules supporting
    a particular NASA CDAWeb dataset

    Examples
    --------
    ::

        # Within the new instrument module, at the top level define
        # a new variable named load, and set it equal to this load method.
        # Code below taken from cnofs_ivm.py.

        # support load routine
        # use the default CDAWeb method
        load = functools.partial(cdw.load, pandas_format=False)

    """

    # Load data from any files provided
    if len(fnames) <= 0:
        return xr.Dataset()
    else:
        # Using cdflib wrapper to load the CDF and format data and
        # metadata for pysat using some assumptions. Depending upon your needs
        # the resulting pandas DataFrame may need modification.
        ldata = []

        # Find unique files for monthly / yearly cadence.
        # Arbitrary timestamp needed for comparison.
        t0 = dt.datetime(2009, 1, 1)
        if (t0 + file_cadence) > (t0 + dt.timedelta(days=1)):
            lfnames = list(np.unique([fname[:-11] for fname in fnames]))
        else:
            lfnames = fnames

        for lfname in lfnames:
            temp_data = cdflib.cdf_to_xarray(lfname, to_datetime=True)
            ldata.append(temp_data)

        # Combine individual files together
        if len(ldata) > 0:
            data = xr.combine_by_coords(ldata)

    all_vars = io.xarray_all_vars(data)

    # Convert output epoch name to 'time' for pysat consistency
    if epoch_name != 'time':
        if 'time' not in all_vars:
            if epoch_name in data.dims:
                data = data.rename({epoch_name: 'time'})
            elif epoch_name in all_vars:
                data = data.rename({epoch_name: 'time'})
                wstr = ''.join(['Epoch label: "', epoch_name, '"',
                                ' is not a dimension.'])
                pysat.logger.warning(wstr)
            else:
                estr = ''.join(['Epoch label: "', epoch_name, '"',
                                ' not found in loaded data, ',
                                repr(all_vars)])
                raise ValueError(estr)

        epoch_name = 'time'

    all_vars = io.xarray_all_vars(data)

    meta = pysat.Meta(labels=labels)

    full_mdict = {}

    if meta_translation is None:
        # Assign default translation using `meta`
        meta_translation = {}

    # Drop metadata labels initialization
    if drop_meta_labels is None:
        drop_meta_labels = []
    else:
        drop_meta_labels = pysat.utils.listify(drop_meta_labels)

    for key in all_vars:
        meta_dict = {}
        for nc_key in data[key].attrs.keys():
            meta_dict[nc_key] = data[key].attrs[nc_key]
        full_mdict[key] = meta_dict
        data[key].attrs = {}

    for data_attr in data.attrs.keys():
        setattr(meta.header, data_attr, getattr(data, data_attr))

    # Process the metadata. First, drop labels as requested.
    for var in full_mdict:
        for label in drop_meta_labels:
            if label in full_mdict[var]:
                full_mdict[var].pop(label)

    # Second, remove some items pysat added for netcdf compatibility
    filt_mdict = io.remove_netcdf4_standards_from_meta(full_mdict, epoch_name,
                                                       meta.labels)

    # Translate labels from file to pysat compatible labels using
    # `meta_translation`
    filt_mdict = io.apply_table_translation_from_file(meta_translation,
                                                      filt_mdict)

    # Next, allow processing by developers so they can deal with
    # issues with specific files
    if meta_processor is not None:
        filt_mdict = meta_processor(filt_mdict)

    # Meta cannot take array data, if present save it as seperate meta data
    # labels
    filt_mdict = io.meta_array_expander(filt_mdict)

    # Assign filtered metadata to pysat.Meta instance
    for key in filt_mdict:
        meta[key] = filt_mdict[key]

    # Remove attributes from the data object
    data.attrs = {}

    return data, meta


# TODO(#103): Include support to unzip / untar files after download.
def download(date_array, tag='', inst_id='', supported_tags=None,
             remote_url='https://cdaweb.gsfc.nasa.gov', data_path=None):
    """Download NASA CDAWeb data.

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
    supported_tags : dict
        dict of dicts. Keys are supported tag names for download. Value is
        a dict with 'remote_dir', 'fname'. Inteded to be pre-set with
        functools.partial then assigned to new instrument code.
        (default=None)
    remote_url : str
        Remote site to download data from
        (default='https://cdaweb.gsfc.nasa.gov')
    data_path : str or NoneType
        Path to data directory.  If None is specified, the value previously
        set in Instrument.files.data_path is used.  (default=None)

    Examples
    --------
    ::

        # Download support added to cnofs_vefi.py using code below
        fn = 'cnofs_vefi_bfield_1sec_{year:4d}{month:02d}{day:02d}_v05.cdf'
        dc_b_tag = {'remote_dir': ''.join(('/pub/data/cnofs/vefi/bfield_1sec',
                                            '/{year:4d}/')),
                    'fname': fn}
        supported_tags = {'dc_b': dc_b_tag}

        download = functools.partial(nasa_cdaweb.download,
                                     supported_tags=supported_tags)

    """

    inst_dict = try_inst_dict(inst_id, tag, supported_tags)

    # Naming scheme for files on the CDAWeb server
    remote_dir = inst_dict['remote_dir']

    # Get list of files from server
    remote_files = list_remote_files(tag=tag, inst_id=inst_id,
                                     remote_url=remote_url,
                                     supported_tags=supported_tags,
                                     start=date_array[0],
                                     stop=date_array[-1])

    # Download only requested files that exist remotely
    for date, fname in remote_files.items():
        # Format files for specific dates and download location
        # Year and day found in remote_dir: day is assumed to be day of year
        if 'day' in remote_dir and 'month' not in remote_dir:
            doy = date.timetuple().tm_yday
            formatted_remote_dir = remote_dir.format(year=date.year,
                                                     day=doy,
                                                     hour=date.hour,
                                                     min=date.minute,
                                                     sec=date.second)
        else:
            formatted_remote_dir = remote_dir.format(year=date.year,
                                                     month=date.month,
                                                     day=date.day,
                                                     hour=date.hour,
                                                     min=date.minute,
                                                     sec=date.second)
        remote_path = '/'.join((remote_url.strip('/'),
                                formatted_remote_dir.strip('/'),
                                fname))

        saved_local_fname = os.path.join(data_path, fname)

        # Perform download
        logger.info(' '.join(('Attempting to download file for',
                              date.strftime('%d %B %Y'))))
        try:
            with requests.get(remote_path) as req:
                if req.status_code != 404:
                    with open(saved_local_fname, 'wb') as open_f:
                        open_f.write(req.content)
                    logger.info('Successfully downloaded {:}.'.format(
                        saved_local_fname))
                else:
                    logger.info(' '.join(('File not available for',
                                          date.strftime('%d %B %Y'))))
        except requests.exceptions.RequestException as exception:
            logger.info(' '.join((str(exception), '- File not available for',
                                  date.strftime('%d %B %Y'))))
    return


def cdas_download(date_array, tag='', inst_id='', supported_tags=None,
                  data_path=None):
    """Download NASA CDAWeb CDF data using cdasws.

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
    supported_tags : dict
        dict of dicts. Keys are supported tag names for download. Value is
        a dict with 'remote_dir', 'fname'. Inteded to be pre-set with
        functools.partial then assigned to new instrument code.
        (default=None)
    data_path : str or NoneType
        Path to data directory.  If None is specified, the value previously
        set in Instrument.files.data_path is used.  (default=None)

    Note
    ----
    Supported tags for this function use the cdaweb dataset naming convention.
    You can find the data set names on CDAWeb or you can use cdasws.

    Starting from scratch using cdasws
    ::
        from cdasws import CdasWs
        cdas = CdasWs()

        # Get list of available observatories/platforms.
        cdas.get_observatories()

        # Once your observatory is located, list the available instruments.
        cdas.get_instruments(observatory=‘observatory_name’)

        # Now list the available data sets for one instrument.
        cdas.get_datasets(observatory=‘observatory_name’,
                          instrument=‘instrument_name’)

        # You can also list all of the datasets for an observatory.
        cdas.get_datasets(observatory=‘observatory_name’)

    Alternatively
    ::
        Visit https://cdaweb.gsfc.nasa.gov/
        Select the observatory you want from the list and press submit.
        The following page will have a list of the data sets.
        The bolded names are in the format that cdasws uses.

    Examples
    --------
    ::
        # Download support added to cnofs_vefi.py using code below
        download_tags = {'': {'dc_b': 'CNOFS_VEFI_BFIELD_1SEC'}}
        download = functools.partial(cdw.cdas_download,
                                     supported_tags=download_tags)

    """

    start = date_array[0]
    stop = date_array[-1]
    remote_files = cdas_list_remote_files(tag=tag, inst_id=inst_id,
                                          start=start, stop=stop,
                                          supported_tags=supported_tags,
                                          series_out=False)

    for file in remote_files:

        fname = file.split('/')[-1]
        saved_local_fname = os.path.join(data_path, fname)

        # Perform download
        logger.info(' '.join(('Attempting to download file: ',
                              file)))
        try:
            with requests.get(file) as req:
                if req.status_code != 404:
                    with open(saved_local_fname, 'wb') as open_f:
                        open_f.write(req.content)
                    logger.info('Successfully downloaded {:}.'.format(
                        saved_local_fname))
                else:
                    logger.info(' '.join(('File: "', file,
                                          '" is not available')))
        except requests.exceptions.RequestException as exception:
            logger.info(' '.join((str(exception), '- File: "', file,
                                  '" Is not available')))
    return


def list_remote_files(tag='', inst_id='', start=None, stop=None,
                      remote_url='https://cdaweb.gsfc.nasa.gov',
                      supported_tags=None, two_digit_year_break=None,
                      delimiter=None):
    """Return a Pandas Series of every file for chosen remote data.

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
        file found.
        (default=None)
    stop : dt.datetime or NoneType
        Ending time for the file list.  A None value will stop with the last
        file found.
        (default=None)
    remote_url : str
        Remote site to download data from
        (default='https://cdaweb.gsfc.nasa.gov')
    supported_tags : dict
        dict of dicts. Keys are supported tag names for download. Value is
        a dict with 'remote_dir', 'fname'. Inteded to be
        pre-set with functools.partial then assigned to new instrument code.
        (default=None)
    two_digit_year_break : int or NoneType
        If filenames only store two digits for the year, then
        '1900' will be added for years >= two_digit_year_break
        and '2000' will be added for years < two_digit_year_break.
        (default=None)
    delimiter : str or NoneType
        If filename is delimited, then provide delimiter alone e.g. '_'
        (default=None)

    Returns
    -------
    pysat.Files.from_os : (pysat._files.Files)
        A class containing the verified available files

    Examples
    --------
    ::

        fname = 'cnofs_vefi_bfield_1sec_{year:04d}{month:02d}{day:02d}_v05.cdf'
        supported_tags = {'dc_b': fname}
        list_remote_files = \
            functools.partial(nasa_cdaweb.list_remote_files,
                              supported_tags=supported_tags)

        fname = 'cnofs_cindi_ivm_500ms_{year:4d}{month:02d}{day:02d}_v01.cdf'
        supported_tags = {'': fname}
        list_remote_files = \
            functools.partial(cdw.list_remote_files,
                              supported_tags=supported_tags)

    """

    inst_dict = try_inst_dict(inst_id, tag, supported_tags)

    # Naming scheme for files on the CDAWeb server
    format_str = '/'.join((inst_dict['remote_dir'].strip('/'),
                           inst_dict['fname']))

    # Break string format into path and filename
    dir_split = os.path.split(format_str)

    # Parse the path to find the number of levels to search
    format_dir = dir_split[0]
    search_dir = futils.construct_searchstring_from_format(format_dir)
    n_layers = len(search_dir['keys'])

    # Only keep file portion of format
    format_str = dir_split[-1]
    # Generate list of targets to identify files
    search_dict = futils.construct_searchstring_from_format(format_str)
    targets = [x.strip('?') for x in search_dict['string_blocks'] if len(x) > 0]

    # Remove any additional '?' characters that the user may have supplied
    new_targets = []
    for target in targets:
        tstrs = target.split('?')
        for tstr in tstrs:
            if tstr != '':
                new_targets.append(tstr)
    targets = new_targets

    remote_dirs = []
    for level in range(n_layers + 1):
        remote_dirs.append([])
    remote_dirs[0] = ['']

    # Build a list of files using each filename target as a goal
    full_files = []

    if start is None and stop is None:
        # Use the topmost directory without variables
        url_list = ['/'.join((remote_url,
                              search_dir['string_blocks'][0]))]
    elif start is not None:
        stop = dt.datetime.now() if (stop is None) else stop

        if 'year' in search_dir['keys']:
            url_list = []
            if 'month' in search_dir['keys']:
                search_times = pds.date_range(start,
                                              stop + pds.DateOffset(months=1),
                                              freq='M')
                for time in search_times:
                    subdir = format_dir.format(year=time.year, month=time.month)
                    url_list.append('/'.join((remote_url, subdir)))
            else:
                if 'day' in search_dir['keys']:
                    search_times = pds.date_range(start, stop
                                                  + pds.DateOffset(days=1),
                                                  freq='D')
                else:
                    search_times = pds.date_range(start, stop
                                                  + pds.DateOffset(years=1),
                                                  freq='Y')
                for time in search_times:
                    doy = int(time.strftime('%j'))
                    subdir = format_dir.format(year=time.year, day=doy)
                    url_list.append('/'.join((remote_url, subdir)))
    try:
        for top_url in url_list:
            for level in range(n_layers + 1):
                for directory in remote_dirs[level]:
                    temp_url = '/'.join((top_url.strip('/'), directory))
                    soup = BeautifulSoup(requests.get(temp_url).content,
                                         "lxml")
                    links = soup.find_all('a', href=True)
                    for link in links:
                        # If there is room to go down, look for directories
                        if link['href'].count('/') == 1:
                            remote_dirs[level + 1].append(link['href'])
                        else:
                            # If at the endpoint, add matching files to list
                            add_file = True
                            for target in targets:
                                if link['href'].count(target) == 0:
                                    add_file = False
                            if add_file:
                                full_files.append(link['href'])
    except requests.exceptions.ConnectionError as merr:
        raise type(merr)(' '.join((str(merr), 'pysat -> Request potentially',
                                   'exceeds the server limit. Please try',
                                   'again using a smaller data range.')))

    # Parse remote filenames to get date information
    if delimiter is None:
        stored = futils.parse_fixed_width_filenames(full_files, format_str)
    else:
        stored = futils.parse_delimited_filenames(full_files, format_str,
                                                  delimiter)
    # Process the parsed filenames and return a properly formatted Series
    stored_list = futils.process_parsed_filenames(stored, two_digit_year_break)

    # Downselect to user-specified dates, if needed
    if start is not None:
        mask = (stored_list.index >= start)
        if stop is not None:
            stop_point = (stop + pds.DateOffset(days=1))
            mask = mask & (stored_list.index < stop_point)
        stored_list = stored_list[mask]

    return stored_list


def cdas_list_remote_files(tag='', inst_id='', start=None, stop=None,
                           supported_tags=None, series_out=True):
    """Return a list of every file for chosen remote data.

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
        file found.
        (default=None)
    stop : dt.datetime or NoneType
        Ending time for the file list.  A None value will stop with the last
        file found.
        (default=None)
    supported_tags : dict
        dict of dicts. Keys are supported tag names for download. Value is
        a dict with 'remote_dir', 'fname'. Inteded to be
        pre-set with functools.partial then assigned to new instrument code.
        (default=None)
    series_out : bool
        boolean to determine output type. True for pandas series of file names,
        and False for a list of the full web address.

    Returns
    -------
    file_list : list
        A list containing the verified available files

    Note
    ----
    Supported tags for this function use the cdaweb dataset naming convention.
    You can find the dataset names on cdaweb or you can use cdasws.

    Examples
    --------
    ::
        download_tags = {'': {'dc_b': 'CNOFS_VEFI_BFIELD_1SEC'}}
        list_remote_files = functools.partial(cdw.cdas_list_remote_files,
                                              supported_tags=download_tags)

        download_tags = {'': {'': 'CNOFS_CINDI_IVM_500MS'}}
        list_remote_files = functools.partial(cdw.cdas_list_remote_files,
                                              supported_tags=download_tags)
    """
    cdas = CdasWs()
    dataset = try_inst_dict(inst_id, tag, supported_tags)

    if start is None and stop is None:
        # Use the topmost directory without variables
        start = cdas.get_inventory(identifier=dataset)[0].start
        stop = cdas.get_inventory(identifier=dataset)[-1].end
    elif stop is None:
        stop = start + dt.timedelta(days=1)
    elif start == stop:
        stop = start + dt.timedelta(days=1)

    if isinstance(start, pds._libs.tslibs.timestamps.Timestamp):
        start = start.tz_localize('utc')
        stop = stop.tz_localize('utc')

    og_files = cdas.get_original_files(dataset=dataset, start=start, end=stop)

    if series_out:
        name_list = [os.path.basename(f['Name']) for f in og_files[1]]
        t_stamp = [pds.Timestamp(f['StartTime'][:10]) for f in og_files[1]]
        file_list = pds.Series(data=name_list, index=t_stamp)
    else:
        file_list = [f['Name'] for f in og_files[1]]

    return file_list
