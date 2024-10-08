#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3986131
#
# DISTRIBUTION STATEMENT A: Approved for public release. Distribution is
# unlimited.
# ----------------------------------------------------------------------------
"""Module for data sets created by JHU APL."""

import datetime as dt
import numpy as np
import pandas as pds
import xarray as xr

import pysat
from pysat.utils.coords import expand_xarray_dims
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
        hours = np.array([int(np.floor(sec / 3600.0))
                          for sec in data[skey].values])
        mins = [int(np.floor((sec - hours[i] * 3600) / 60.0))
                for i, sec in enumerate(data[skey].values)]
        secs = [int(np.floor((sec - hours[i] * 3600 - mins[i] * 60)))
                for i, sec in enumerate(data[skey].values)]
        microsecs = [int(np.floor((sec - hours[i] * 3600 - mins[i] * 60
                                   - secs[i]) * 1.0e6))
                     for i, sec in enumerate(data[skey].values)]
        days = np.array([int(dval) for dval in data[dkey].values])

        # Ensure hours are within a realistic range. Datetime can handle day of
        # roll-over for non-leap years.
        days[hours >= 24] += 1
        hours[hours >= 24] -= 24

        dtimes = [
            dt.datetime.strptime(
                "{:4d}-{:03d}-{:02d}-{:02d}-{:02d}-{:06d}".format(
                    int(data[ykey].values[i]), days[i], hours[i], mins[i],
                    secs[i], microsec), '%Y-%j-%H-%M-%S-%f')
            for i, microsec in enumerate(microsecs)]
    else:
        dtimes = [
            dt.datetime.strptime("{:4d}-{:03d}".format(
                int(data[ykey].values[i]), int(data[dkey].values[i])), '%Y-%j')
            + (pds.to_datetime(etime).to_pydatetime() - epoch)
            for i, etime in enumerate(data[epoch_var].values)]

    return dtimes


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
        that the desired epoch, 'TIME', is not present as a dimension in the
        NetCDF file.  If False, no warning is raised. (default=True)

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
    # Initialize the output
    mdata = pysat.Meta()
    data = xr.Dataset()

    # Define the input variables
    labels = {mdata.labels.units: ('UNITS', str),
              mdata.labels.desc: ('TITLE', str)}

    # CDAWeb stores these files in the NetCDF format instead of the CDF format
    single_data = list()
    for fname in fnames:
        # There are multiple files per day, with time as a variable rather
        # than a dimension or coordinate.  Additionally, no coordinates
        # are assigned.
        sdata, mdata = load_netcdf(fname, epoch_name='TIME', epoch_unit='s',
                                   meta_kwargs={'labels': labels},
                                   pandas_format=pandas_format,
                                   decode_times=False,
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

    if len(single_data) > 0:
        # After loading all the data, determine which dimensions need to be
        # expanded. Pad the data so that all dimensions are the same shape.
        single_data = expand_xarray_dims(single_data, mdata, dims_equal=False)

        # Combine all the data, indexing along time
        data = xr.combine_by_coords(single_data)

    return data, mdata


def load_sdr_aurora(fnames, name='', tag='', inst_id='', pandas_format=False,
                    strict_dim_check=True, combine_times=False):
    """Load JHU APL SDR data and meta data.

    Parameters
    ----------
    fnames : array-like
        Iterable of filename strings, full path, to data files to be loaded.
    name : str
        Instrument name used to identify the data set to be loaded (default='')
    tag : str
        Tag name used to identify particular data set to be loaded (default='')
    inst_id : str
        Instrument ID name used to identify different instrument carriers
        (default='')
    pandas_format : bool
        False for xarray format, True for pandas (default=False)
    strict_dim_check : bool
        Used for xarray data (`pandas_format` is False). If True, warn the user
        that the desired epoch, 'TIME_DAY', is not present as a dimension in the
        NetCDF file.  If False, no warning is raised. (default=True)
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

    """
    # Initialize the output
    mdata = pysat.Meta()
    data = xr.Dataset()

    # Define the input variables and working variables
    labels = {mdata.labels.units: ('UNITS', str),
              mdata.labels.desc: ('TITLE', str)}
    load_time = 'TIME_DAY'
    time_vars = ['YEAR_DAY', 'DOY_DAY', 'TIME_EPOCH_DAY', 'YEAR_NIGHT',
                 'DOY_NIGHT', 'TIME_NIGHT', 'TIME_EPOCH_NIGHT']
    coords = ['PIERCEPOINT_NIGHT_LATITUDE', 'PIERCEPOINT_NIGHT_LONGITUDE',
              'PIERCEPOINT_NIGHT_ALTITUDE', 'PIERCEPOINT_NIGHT_SZA',
              'PIERCEPOINT_DAY_LATITUDE', 'PIERCEPOINT_DAY_LONGITUDE',
              'PIERCEPOINT_DAY_ALTITUDE', 'PIERCEPOINT_DAY_SZA']
    time_dims = ['time']
    if name == 'guvi':
        rename_dims = {'nAlongDay': 'nAlong', 'nAlongNight': 'nAlong'}
        swap_dims = {'nAlong': 'time'}
    else:
        rename_dims = {}
        swap_dims = {'nAlongDay': 'time'}

    if tag in ['sdr-imaging', 'sdr-disk', 'sdr2-disk']:
        time_vars.extend(["YEAR_DAY_AURORAL", "DOY_DAY_AURORAL",
                          "TIME_DAY_AURORAL", "TIME_EPOCH_DAY_AURORAL"])
        coords.extend(['PIERCEPOINT_DAY_LATITUDE_AURORAL',
                       'PIERCEPOINT_DAY_LONGITUDE_AURORAL',
                       'PIERCEPOINT_DAY_ALTITUDE_AURORAL',
                       'PIERCEPOINT_DAY_SZA_AURORAL'])
        time_dims.append('time_auroral')
        rename_dims['nAlongDayAur'] = 'time_auroral'
        if name == 'guvi':
            rename_dims['nCrossDay'] = 'nCross'
            rename_dims['nCrossNight'] = 'nCross'
        else:
            time_dims.append('time_night')
            rename_dims['nAlongNight'] = 'time_night'
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
                                   meta_kwargs={'labels': labels},
                                   pandas_format=pandas_format,
                                   decode_times=False,
                                   strict_dim_check=strict_dim_check)

        # Calculate the time for this data file. The pysat `load_netcdf` routine
        # converts the 'TIME' parameter (seconds of day) into datetime using
        # the UNIX epoch as the date offset
        ftime = build_dtimes(sdata, '_DAY', dt.datetime(1970, 1, 1))

        # Ensure identical day and night dimensions for GUVI
        if name == 'guvi':
            if sdata.sizes['nAlongDay'] != sdata.sizes['nAlongNight']:
                raise ValueError('Along-track day and night dimensions differ')

            if 'nCrossDay' in rename_dims.keys():
                if sdata.sizes['nCrossDay'] != sdata.sizes['nCrossNight']:
                    raise ValueError(''.join([
                        'Cross-track day and night dimensions differ ',
                        '{:} != {:}'.format(sdata.sizes['nCrossDay'],
                                            sdata.sizes['nCrossNight'])]))

        # Combine identical dimensions and rename some time dimensions
        sdata = sdata.rename_dims(rename_dims)

        if tag in ['sdr-imaging', 'sdr-disk', 'sdr2-disk']:
            sdata = sdata.assign(time_auroral=build_dtimes(sdata,
                                                           '_DAY_AURORAL'))
        elif tag == 'sdr-spectrograph' and inst_id == 'low_res':
            sdata = sdata.assign(time_gaim_day=build_dtimes(
                sdata, '_GAIM_DAY'), time_gaim_night=build_dtimes(
                    sdata, '_GAIM_NIGHT'))

        # Test that day and night times are consistent
        if name == 'guvi':
            max_diff = 1.0
            for i, ntime in enumerate(build_dtimes(sdata, '_NIGHT')):
                diff_sec = abs(ntime - ftime[i]).total_seconds()
                if diff_sec > max_diff:
                    raise ValueError(''.join(['Day and night times differ by ',
                                              '{:.3f} s >= {:.3f} s'.format(
                                                  diff_sec, max_diff)]))

        # Remove redundant time variables and rname the 'nAlong' dimension
        sdata = sdata.drop_vars(time_vars).swap_dims(swap_dims)

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

    # Add metadata for 'time_auroral' and 'nCross' variables
    mdata['time_auroral'] = {'desc': 'Auroral time index'}
    mdata['nCross'] = {'desc': 'Number of cross-track observations'}

    # Combine all time dimensions
    if inners is not None:
        if combine_times:
            data_list = expand_xarray_dims(
                [inners[dim] if dim == 'time' else
                 inners[dim].rename_dims({dim: 'time'})
                 for dim in time_dims], mdata, dims_equal=False)
        else:
            data_list = [inners[dim] for dim in time_dims]

        # Combine all the data, indexing along time
        data = xr.merge(data_list)

        if name == 'ssusi':
            # Data may not contain both day and night values
            bad_coords = [coord for coord in coords
                          if coord not in data.data_vars.keys()]

            if len(bad_coords) == 4:
                # Ensure the time of day is consisent
                tod = bad_coords[0].split("_")[1]
                if np.any([coord.find(tod) < 0 for coord in bad_coords]):
                    raise ValueError('Some {:} coordinates are missing'.format(
                        tod))

                coords = [coord for coord in coords if coord not in bad_coords]
            elif len(bad_coords) == len(coords):
                raise ValueError('All coordiantes are missing from data')
            elif len(bad_coords) > 0:
                raise ValueError(''.join(['Unexpected amount of coordinates ',
                                          'missing from data: {:}'.format(
                                              bad_coords)]))

        # Set additional coordinates
        data = data.set_coords(coords).assign_coords({'time': data['time']})
        if tag in ['sdr-imaging', 'sdr-disk', 'sdr2-disk']:
            # Get the additional coordinates to assign
            add_coords = {'nchan': ["121.6nm", "130.4nm", "135.6nm", "LBHshort",
                                    "LBHlong"],
                          "nchanAur": ["121.6nm", "130.4nm", "135.6nm",
                                       "LBHshort", "LBHlong"]}
            for dvar in sdata.data_vars.keys():
                if dvar.find('nCross') == 0:
                    # Identify all cross-track variables
                    add_coords[dvar] = sdata[dvar].data

            # Assign the additional coordinates
            data = data.assign_coords(add_coords)
        elif tag == 'sdr-spectrograph':
            data = data.assign_coords({"nchan": ["121.6nm", "130.4nm",
                                                 "135.6nm", "LBHshort",
                                                 "LBHlong", "?"]})

        # Ensure the data is ordered correctly
        data = data.sortby('time')

    return data, mdata


def clean_by_dqi(inst):
    """Clean JHU APL data using the DQI flags to different levels using the DQI.

    Parameters
    ----------
    inst : pysat.Instrument
        Object containing a JHU APL Instrument with data

    Note
    ----
        0: MeV noise in pixel, (allowed at clean)
        1: SAA, (allowed at dusty/dirty)
        2: unknown mirror/bit position (allowed at none)
        3: LBH Thresh exceeded (allowed at none)

    """
    # Find the flag variables
    dqi_vars = [var for var in inst.variables if var.find('DQI') == 0]

    # Find the variables affected by each flag
    dat_vars = dict()
    for dqi in dqi_vars:
        dqi_dims = inst.data[dqi].dims
        dat_vars[dqi] = [var for var in inst.variables
                         if dqi_dims == inst.data[var].dims[:len(dqi_dims)]
                         and var not in inst.data.coords.keys()
                         and var.find("IN_SAA") < 0 and var not in dqi_vars]

    for dqi in dqi_vars:
        if inst.clean_level == 'clean':
            # For clean, require DQI of zero (MeV noise only)
            dqi_bad = inst.data[dqi].values > 0
        elif inst.clean_level in ['dusty', 'dirty']:
            # For dusty and dirty, allow the SAA region as well
            dqi_bad = inst.data[dqi].values > 1
        else:
            # For none, allow all to pass
            dqi_bad = np.full(inst.data[dqi].values.shape, False)

        # Apply the DQI mask to the data, replacing bad values with
        # appropriate fill values if there are bad values
        if dqi_bad.any():
            for dat_var in dat_vars[dqi]:
                fill_val = inst.meta[dat_var, inst.meta.labels.fill_val]
                try:
                    inst.data[dat_var].values[dqi_bad] = fill_val
                except ValueError:
                    # Try again with NaN, a bad fill value was set
                    inst.data[dat_var].values[dqi_bad] = np.nan
                    inst.meta[dat_var] = {inst.meta.labels.fill_val: np.nan}
    return


def concat_data(inst, time_dims, new_data, combine_times=False, **kwargs):
    """Concatonate data to inst.data for JHU APL SDR data.

    Parameters
    ----------
    inst : pysat.Instrument
        Object containing a JHU APL Instrument with data
    time_dims : list
        List of the time dimensions
    new_data : xarray.Dataset or list of such objects
        New data objects to be concatonated
    combine_times : bool
        For SDR data, optionally combine the different datetime coordinates
        into a single time coordinate (default=False)
    **kwargs : dict
        Optional keyword arguments passed to xr.concat

    Note
    ----
    For xarray, `dim=Instrument.index.name` is passed along to xarray.concat
    except if the user includes a value for dim as a keyword argument.

    """
    # Concatonate using the appropriate method for the number of time
    # dimensions
    if len(time_dims) == 1:
        # There is only one time dimensions, but other dimensions may
        # need to be adjusted
        new_data = pysat.utils.coords.expand_xarray_dims(
            new_data, inst.meta, exclude_dims=time_dims)

        # Combine the data
        inst.data = xr.combine_by_coords(new_data, **kwargs)
    else:
        inners = None
        for ndata in new_data:
            # Separate into inner datasets
            inner_keys = {dim: [key for key in ndata.keys()
                                if dim in ndata[key].dims] for dim in time_dims}
            inner_dat = {dim: ndata.get(inner_keys[dim]) for dim in time_dims}

            # Add 'single_var's into 'time' dataset to keep track
            sv_keys = [val.name for val in ndata.values()
                       if 'single_var' in val.dims]
            singlevar_set = ndata.get(sv_keys)
            inner_dat[inst.index.name] = xr.merge([inner_dat[inst.index.name],
                                                   singlevar_set])

            # Concatenate along desired dimension with previous data
            if inners is None:
                # No previous data, assign the data separated by dimension
                inners = dict(inner_dat)
            else:
                # Concatenate with existing data
                inners = {dim: xr.concat([inners[dim], inner_dat[dim]],
                                         dim=dim) for dim in time_dims}

        # Combine all time dimensions
        if inners is not None:
            if combine_times:
                data_list = pysat.utils.coords.expand_xarray_dims(
                    [inners[dim] if dim == inst.index.name else
                     inners[dim].rename_dims({dim: inst.index.name})
                     for dim in time_dims if len(inners[dim].dims) > 0],
                    inst.meta, dims_equal=False)
            else:
                data_list = [inners[dim] for dim in time_dims]

            # Combine all the data, indexing along time
            inst.data = xr.merge(data_list)
    return
