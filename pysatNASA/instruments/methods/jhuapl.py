# -*- coding: utf-8 -*-
"""Module for data sets created by JHU APL."""

import datetime as dt
import numpy as np
import pandas as pds
import xarray as xr

from pysat.utils.io import load_netcdf


def build_dtimes(data, var, epoch=None, epoch_var='time'):
    """Build datetime objects from standard JHU APL time variables.

    Parameters
    ----------
    data : xr.Dataset
        Xarray dataset with time variables
    var : str
        Common string to identify desired year, day of year, and seconds of day
    epoch : dt.datetime or NoneType
        Epoch to subtract from data or NoneType to get seconds of day from
        `data` (default=None)
    epoch_var : str
        Epoch variable containing time data that seconds of day will be
        obtained from if `epoch` != None (default='time')

    Returns
    -------
    dtimes : list-like
        List of datetime objects

    """
    ykey = 'YEAR{:s}'.format(var)
    dkey = 'DOY{:s}'.format(var)
    skey = 'TIME{:s}'.format(var)

    if epoch is None:
        hours = [int(np.floor(sec / 3600.0)) for sec in data[skey].values]
        mins = [int(np.floor((sec - hours[i] * 3600) / 60.0))
                for i, sec in enumerate(data[skey].values)]
        secs = [int(np.floor((sec - hours[i] * 3600 - mins[i] * 60)))
                for i, sec in enumerate(data[skey].values)]
        dtimes = [
            dt.datetime.strptime(
                "{:4d}-{:03d}-{:02d}-{:02d}-{:02d}-{:06.0f}".format(
                    int(data[ykey].values[i]), int(data[dkey].values[i]),
                    hours[i], mins[i], secs[i],
                    (sec - hours[i] * 3600 - mins[i] * 60 - secs[i]) * 1.0e6),
                '%Y-%j-%H-%M-%S-%f')
            for i, sec in enumerate(data[skey].values)]
    else:
        dtimes = [
            dt.datetime.strptime("{:4d}-{:03d}".format(
                int(data[ykey].values[i]), int(data[dkey].values[i])), '%Y-%j')
            + (pds.to_datetime(etime).to_pydatetime() - epoch)
            for i, etime in enumerate(data[epoch_var].values)]

    return dtimes


def expand_coords(data_list, mdata, dims_equal=False):
    """Ensure that dimensions do not vary from file to file.

    Parameters
    ----------
    data_list : list-like
        List of xr.Dataset objects with the same dimensions and variables
    mdata : pysat.Meta
        Metadata for the data in `data_list`
    dims_equal : bool
        Assert that all xr.Dataset objects have the same dimensions if True
        (default=False)

    Returns
    -------
    out_list : list-like
        List of xr.Dataset objects with the same dimensions and variables,
        now with dimensions that all have the same values and data padded
        when needed.

    """
    # Get a list of all the dimensions
    if dims_equal:
        dims = list(data_list[0].dims.keys()) if len(data_list) > 0 else []
    else:
        dims = list()
        for sdata in data_list:
            if len(dims) == 0:
                dims = list(sdata.dims.keys())
            else:
                for dim in list(sdata.dims.keys()):
                    if dim not in dims:
                        dims.append(dim)

    # After loading all the data, determine which dimensions may need to be
    # expanded, as they could differ in dimensions from file to file
    combo_dims = {dim: max([sdata.dims[dim] for sdata in data_list
                            if dim in sdata.dims]) for dim in dims}

    # Expand the data so that all dimensions are the same shape
    out_list = list()
    for i, sdata in enumerate(data_list):
        # Determine which dimensions need to be updated
        fix_dims = [dim for dim in sdata.dims.keys()
                    if sdata.dims[dim] < combo_dims[dim]]

        new_data = {}
        update_new = False
        for dvar in sdata.data_vars.keys():
            # See if any dimensions need to be updated
            update_dims = list(set(sdata[dvar].dims) & set(fix_dims))

            # Save the old data as is, or pad it to have the right dims
            if len(update_dims) > 0:
                update_new = True
                new_shape = list(sdata[dvar].values.shape)
                old_slice = [slice(0, ns) for ns in new_shape]

                for dim in update_dims:
                    idim = list(sdata[dvar].dims).index(dim)
                    new_shape[idim] = combo_dims[dim]

                # Set the new data for output
                new_dat = np.full(shape=new_shape, fill_value=mdata[
                    dvar, mdata.labels.fill_val])
                new_dat[tuple(old_slice)] = sdata[dvar].values
                new_data[dvar] = (sdata[dvar].dims, new_dat)
            else:
                new_data[dvar] = sdata[dvar]

        # Get the updated dataset
        out_list.append(xr.Dataset(new_data) if update_new else sdata)

    return out_list


def load_edr_aurora(fnames, tag='', inst_id='', pandas_format=False,
                    strict_dim_check=True):
    """Load JHU APL EDR Aurora data and meta data.

    Parameters
    ----------
    fnames : array-like
        Iterable of filename strings, full path, to data files to be loaded.
    tag : str
        Tag name used to identify particular data set to be loaded (default='')
    inst_id : str
        Instrument ID name used to identify different instrument carriers
        (default='')
    pandas_format : bool
        False for xarray format, True for pandas (default=False)
    strict_dim_check : bool
        Used for xarray data (`pandas_format` is False). If True, warn the user
        that the desired epoch is not present in `xarray.dims`.  If False,
        no warning is raised. (default=True)

    Returns
    -------
    data : pds.DataFrame or xr.Dataset
        Data to be assigned to the pysat.Instrument.data object.
    mdata : pysat.Meta
        Pysat Meta data for each data variable.

    Note
    ----
    Logger warning 'Epoch label: TIME is not a dimension.' is raised due to
    the data format and pysat file expectations.

    Examples
    --------
    ::

        inst = pysat.Instrument('timed', 'guvi', tag='edr-aur')
        inst.load(2003, 1)

    """
    # Define the input variables
    labels = {'units': ('UNITS', str), 'desc': ('TITLE', str)}

    # CDAWeb stores these files in the NetCDF format instead of the CDF format
    single_data = list()
    for fname in fnames:
        # There are multiple files per day, with time as a variable rather
        # than a dimension or coordinate.  Additionally, no coordinates
        # are assigned.
        sdata, mdata = load_netcdf(fname, epoch_name='TIME', epoch_unit='s',
                                   labels=labels, pandas_format=pandas_format,
                                   strict_dim_check=strict_dim_check)

        # Calculate the time for this data file. The pysat `load_netcdf` routine
        # converts the 'TIME' parameter (seconds of day) into datetime using
        # the UNIX epoch as the date offset
        ftime = dt.datetime.strptime(
            "{:4d}-{:03d}".format(
                sdata['YEAR'].values.astype(int),
                sdata['DOY'].values.astype(int)), '%Y-%j') + (
                    pds.to_datetime(sdata['time'].values).to_pydatetime()
                    - dt.datetime(1970, 1, 1))

        # Assign a datetime variable, making indexing possible
        sdata['time'] = ftime
        sdata = sdata.assign_coords(
            {'time': sdata['time']}).expand_dims(dim='time')

        # Save the data in the file list
        single_data.append(sdata)

    # Update the meta data
    # TODO(https://github.com/pysat/pysat/issues/1078): Update the metadata by
    # removing 'TIME', once possible
    for var in mdata.keys():
        # Update the fill value, using information from the global header
        mdata[var] = {mdata.labels.fill_val: mdata.header.NO_DATA_IN_BIN_VALUE}

    # After loading all the data, determine which dimensions need to be
    # expanded. Pad the data so that all dimensions are the same shape
    single_data = expand_coords(single_data, mdata, dims_equal=True)

    # Combine all the data, indexing along time
    data = xr.combine_by_coords(single_data)

    return data, mdata


def load_sdr_aurora(fnames, tag='', inst_id='', pandas_format=False,
                    combine_times=False):
    """Load JHU APL SDR data and meta data.

    Parameters
    ----------
    fnames : array-like
        Iterable of filename strings, full path, to data files to be loaded.
    tag : str
        Tag name used to identify particular data set to be loaded (default='')
    inst_id : str
        Instrument ID name used to identify different instrument carriers
        (default='')
    pandas_format : bool
        False for xarray format, True for pandas (default=False)
    combine_times : bool
        For SDR data, optionally combine the different datetime coordinates
        into a single time coordinate (default=False)

    Returns
    -------
    data : pds.DataFrame or xr.Dataset
        Data to be assigned to the pysat.Instrument.data object.
    mdata : pysat.Meta
        Pysat Meta data for each data variable.

    Note
    ----
    Logger warning 'Epoch label: TIME is not a dimension.' is raised due to
    the data format and pysat file expectations.

    Examples
    --------
    ::

        inst = pysat.Instrument('timed', 'guvi', tag='edr-aur')
        inst.load(2003, 1)

    """
    # Define the input variables and working variables
    labels = {'units': ('UNITS', str), 'desc': ('TITLE', str)}
    load_time = 'TIME_DAY'
    time_vars = ['YEAR_DAY', 'DOY_DAY', 'TIME_EPOCH_DAY', 'YEAR_NIGHT',
                 'DOY_NIGHT', 'TIME_NIGHT', 'TIME_EPOCH_NIGHT']
    coords = ['PIERCEPOINT_NIGHT_LATITUDE', 'PIERCEPOINT_NIGHT_LONGITUDE',
              'PIERCEPOINT_NIGHT_ALTITUDE', 'PIERCEPOINT_NIGHT_SZA',
              'PIERCEPOINT_DAY_LATITUDE', 'PIERCEPOINT_DAY_LONGITUDE',
              'PIERCEPOINT_DAY_ALTITUDE', 'PIERCEPOINT_DAY_SZA']
    time_dims = ['time']
    rename_dims = {'nAlongDay': 'nAlong', 'nAlongNight': 'nAlong'}

    if tag == 'sdr-imaging':
        time_vars.extend(["YEAR_DAY_AURORAL", "DOY_DAY_AURORAL",
                          "TIME_DAY_AURORAL", "TIME_EPOCH_DAY_AURORAL"])
        coords.extend(['PIERCEPOINT_DAY_LATITUDE_AURORAL',
                       'PIERCEPOINT_DAY_LONGITUDE_AURORAL',
                       'PIERCEPOINT_DAY_ALTITUDE_AURORAL',
                       'PIERCEPOINT_DAY_SZA_AURORAL'])
        time_dims.append('time_auroral')
        rename_dims['nCrossDay'] = 'nCross'
        rename_dims['nCrossNight'] = 'nCross'
        rename_dims['nAlongDayAur'] = 'time_auroral'
    elif tag == 'sdr-spectrograph':
        coords.extend(['PIERCEPOINT_NIGHT_ZENITH_ANGLE',
                       'PIERCEPOINT_NIGHT_SAZIMUTH',
                       'PIERCEPOINT_DAY_ZENITH_ANGLE',
                       'PIERCEPOINT_DAY_SAZIMUTH'])

        if inst_id == 'low_res':
            time_vars.extend(["YEAR_GAIM_DAY", "DOY_GAIM_DAY", "TIME_GAIM_DAY",
                              "TIME_GAIM_NIGHT", "YEAR_GAIM_NIGHT",
                              "DOY_GAIM_NIGHT"])
            time_dims.extend(['time_gaim_day', 'time_gaim_night'])
            rename_dims['nAlongGAIMDay'] = 'time_gaim_day'
            rename_dims['nAlongGAIMNight'] = 'time_gaim_night'

    # CDAWeb stores these files in the NetCDF format instead of the CDF format
    inners = None
    for fname in fnames:
        # There are multiple files per day, with time as a variable rather
        # than a dimension or coordinate.  Additionally, no coordinates
        # are assigned.
        sdata, mdata = load_netcdf(fname, epoch_name=load_time, epoch_unit='s',
                                   labels=labels, pandas_format=pandas_format)

        # Calculate the time for this data file. The pysat `load_netcdf` routine
        # converts the 'TIME' parameter (seconds of day) into datetime using
        # the UNIX epoch as the date offset
        ftime = build_dtimes(sdata, '_DAY', dt.datetime(1970, 1, 1))

        # Ensure identical day and night dimensions
        if sdata.dims['nAlongDay'] != sdata.dims['nAlongNight']:
            raise ValueError('Along-track day and night dimensions differ')

        if 'nCrossDay' in rename_dims.keys():
            if sdata.dims['nCrossDay'] != sdata.dims['nCrossNight']:
                raise ValueError('Cross-track day and night dimensions differ')

        # Combine identical dimensions and rename 'nAlong' to 'time'
        sdata = sdata.rename_dims(rename_dims)

        if tag == 'sdr-imaging':
            sdata = sdata.assign(time_auroral=build_dtimes(sdata,
                                                           '_DAY_AURORAL'))
        elif tag == 'sdr-spectrograph' and inst_id == 'low_res':
            sdata = sdata.assign(time_gaim_day=build_dtimes(
                sdata, '_GAIM_DAY'), time_gaim_night=build_dtimes(
                    sdata, '_GAIM_NIGHT'))

        # Test that day and night times are consistent to the nearest second
        for i, ntime in enumerate(build_dtimes(sdata, '_NIGHT')):
            if abs(ntime - ftime[i]).total_seconds() > 1.0:
                raise ValueError('Day and night times differ')

        # Remove redundant time variables and rname the 'nAlong' dimension
        sdata = sdata.drop_vars(time_vars).swap_dims({'nAlong': 'time'})

        # Assign time as a coordinate for combining files indexing
        sdata['time'] = ftime

        # Separate into inner datasets
        inner_keys = {dim: [key for key in sdata.keys()
                            if dim in sdata[key].dims] for dim in time_dims}
        inner_dat = {dim: sdata.get(inner_keys[dim]) for dim in time_dims}

        # Add 'single_var's into 'time' dataset to keep track
        sv_keys = [val.name for val in sdata.values()
                   if 'single_var' in val.dims]
        singlevar_set = sdata.get(sv_keys)
        inner_dat['time'] = xr.merge([inner_dat['time'], singlevar_set])

        # Concatenate along desired dimension with previous files' data
        if inners is None:
            # No previous data, assign the data separated by dimension
            inners = dict(inner_dat)
        else:
            # Concatenate with existing data
            inners = {dim: xr.concat([inners[dim], inner_dat[dim]], dim=dim)
                      for dim in time_dims}

    # Update the meta data
    # TODO(https://github.com/pysat/pysat/issues/1078): Update the metadata by
    # removing dimensions and time, once possible
    for var in mdata.keys():
        # Update the fill value, using information from the global header
        mdata[var] = {mdata.labels.fill_val: mdata.header.NO_DATA_IN_BIN_VALUE}

    # Combine all time dimensions
    if combine_times:
        data_list = expand_coords([inners[dim] if dim == 'time' else
                                   inners[dim].rename_dims({dim: 'time'})
                                   for dim in time_dims], mdata,
                                  dims_equal=False)
    else:
        data_list = [inners[dim] for dim in time_dims]

    # Combine all the data, indexing along time
    data = xr.merge(data_list)

    # Set additional coordinates
    data = data.set_coords(coords).assign_coords({'time': data['time']})
    if tag == 'sdr-imaging':
        data = data.assign_coords(
            {'nchan': ["121.6nm", "130.4nm", "135.6nm", "LBHshort", "LBHlong"],
             "nchanAur": ["121.6nm", "130.4nm", "135.6nm", "LBHshort",
                          "LBHlong"],
             "nCross": sdata.nCross.data,
             "nCrossDayAur": sdata.nCrossDayAur.data})
    elif tag == 'sdr-spectrograph':
        data = data.assign_coords({"nchan": ["121.6nm", "130.4nm", "135.6nm",
                                             "LBHshort", "LBHlong", "?"]})

    # Ensure the data is ordered correctly
    data = data.sortby('time')

    return data, mdata
