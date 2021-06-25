# -*- coding: utf-8 -*-
"""Provides default routines for integrating NASA CDAWeb instruments into
pysat. Adding new CDAWeb datasets should only require mininal user
intervention.

"""

import datetime as dt
import os
import pandas as pds
import requests

from bs4 import BeautifulSoup

from pysat import logger
from pysat.utils import files as futils
from pysat.instruments.methods import general
from pysatNASA.instruments.methods import CDF


def load(fnames, tag=None, inst_id=None, file_cadence=dt.timedelta(days=1),
         flatten_twod=True):
    """Load NASA CDAWeb CDF files.

    Parameters
    ----------
    fnames : pandas.Series
        Series of filenames
    tag : str or NoneType
        tag or None (default=None)
    inst_id : str or NoneType
        satellite id or None (default=None)
    file_cadence : dt.timedelta or pds.DateOffset
        pysat assumes a daily file cadence, but some instrument data files
        contain longer periods of time.  This parameter allows the specification
        of regular file cadences greater than or equal to a day (e.g., weekly,
        monthly, or yearly). (default=dt.timedelta(days=1))
    flatted_twod : bool
        Flattens 2D data into different columns of root DataFrame rather
        than produce a Series of DataFrames. (default=True)

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
        # Using cdflib wrapper to load the CDF and format data and
        # metadata for pysat using some assumptions. Depending upon your needs
        # the resulting pandas DataFrame may need modification
        ldata = []
        for lfname in fnames:
            if not general.is_daily_file_cadence(file_cadence):
                # Parse out date from filename
                fname = lfname[0:-11]
                date = dt.datetime.strptime(lfname[-10:], '%Y-%m-%d')

                with CDF(fname) as cdf:
                    # Convert data to pysat format
                    try:
                        temp_data, meta = cdf.to_pysat(
                            flatten_twod=flatten_twod)

                        # Select data from multi-day down to daily
                        temp_data = temp_data.loc[
                            date:date + dt.timedelta(days=1)
                            - dt.timedelta(microseconds=1), :]
                        ldata.append(temp_data)
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


def download(date_array, tag=None, inst_id=None, supported_tags=None,
             remote_url='https://cdaweb.gsfc.nasa.gov', data_path=None):
    """Routine to download NASA CDAWeb CDF data.

    This routine is intended to be used by pysat instrument modules supporting
    a particular NASA CDAWeb dataset.

    Parameters
    ----------
    date_array : array_like
        Array of datetimes to download data for. Provided by pysat.
    tag : str or NoneType
        tag or None (default=None)
    inst_id : str or NoneType
        satellite id or None (default=None)
    supported_tags : dict
        dict of dicts. Keys are supported tag names for download. Value is
        a dict with 'remote_dir', 'fname'. Inteded to be pre-set with
        functools.partial then assigned to new instrument code.
        (default=None)
    remote_url : string or NoneType
        Remote site to download data from
        (default='https://cdaweb.gsfc.nasa.gov')
    data_path : string or NoneType
        Path to data directory.  If None is specified, the value previously
        set in Instrument.files.data_path is used.  (default=None)

    Examples
    --------
    ::

        # download support added to cnofs_vefi.py using code below
        fn = 'cnofs_vefi_bfield_1sec_{year:4d}{month:02d}{day:02d}_v05.cdf'
        dc_b_tag = {'remote_dir': ''.join(('/pub/data/cnofs/vefi/bfield_1sec',
                                            '/{year:4d}/')),
                    'fname': fn}
        supported_tags = {'dc_b': dc_b_tag}

        download = functools.partial(nasa_cdaweb.download,
                                     supported_tags=supported_tags)

    """

    if tag is None:
        tag = ''
    if inst_id is None:
        inst_id = ''
    try:
        inst_dict = supported_tags[inst_id][tag]
    except KeyError:
        raise ValueError('inst_id / tag combo unknown.')

    # Naming scheme for files on the CDAWeb server
    remote_dir = inst_dict['remote_dir']

    # Get list of files from server
    remote_files = list_remote_files(tag=tag, inst_id=inst_id,
                                     remote_url=remote_url,
                                     supported_tags=supported_tags,
                                     start=date_array[0],
                                     stop=date_array[-1])

    # Download only requested files that exist remotely
    for date, fname in remote_files.iteritems():
        # Format files for specific dates and download location
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
            logger.info(' '.join((exception, '- File not available for',
                                  date.strftime('%d %B %Y'))))
    return


def list_remote_files(tag=None, inst_id=None, start=None, stop=None,
                      remote_url='https://cdaweb.gsfc.nasa.gov',
                      supported_tags=None, two_digit_year_break=None,
                      delimiter=None):
    """Return a Pandas Series of every file for chosen remote data.

    This routine is intended to be used by pysat instrument modules supporting
    a particular NASA CDAWeb dataset.

    Parameters
    ----------
    tag : string or NoneType
        Denotes type of file to load.  Accepted types are <tag strings>.
        (default=None)
    inst_id : string or NoneType
        Specifies the satellite ID for a constellation.
        (default=None)
    start : dt.datetime or NoneType
        Starting time for file list. A None value will start with the first
        file found.
        (default=None)
    stop : dt.datetime or NoneType
        Ending time for the file list.  A None value will stop with the last
        file found.
        (default=None)
    remote_url : string or NoneType
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
    delimiter : string or NoneType
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

    if tag is None:
        tag = ''
    if inst_id is None:
        inst_id = ''
    try:
        inst_dict = supported_tags[inst_id][tag]
    except KeyError:
        raise ValueError('inst_id / tag combo unknown.')

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
            if 'month' in search_dir['keys']:
                search_times = pds.date_range(start,
                                              stop + pds.DateOffset(months=1),
                                              freq='M')
            else:
                search_times = pds.date_range(start,
                                              stop + pds.DateOffset(years=1),
                                              freq='Y')
            url_list = []
            for time in search_times:
                subdir = format_dir.format(year=time.year, month=time.month)
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
