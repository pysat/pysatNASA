# -*- coding: utf-8 -*-
"""Module for data sets created by JHU APL."""

import datetime as dt
import numpy as np
import pandas as pds
import xarray as xr

from pysat.utils.io import load_netcdf


def load_edr_aurora(fnames, tag='', inst_id='', pandas_format=False):
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
        subday_data, mdata = load_netcdf(fname, epoch_name='TIME',
                                         epoch_unit='s', labels=labels,
                                         pandas_format=pandas_format)
        single_data.append(subday_data)

    # After loading all the data, determine which dimensions need to be expanded
    combo_dims = {dim: max([sdata.dims[dim] for sdata in single_data])
                  for dim in subday_data.dims.keys()}

    # Expand the data so that all dimensions are the same shape
    for i, sdata in enumerate(single_data):
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

        # Calculate the time for this data file. The pysat `load_netcdf` routine
        # converts the 'TIME' parameter (seconds of day) into datetime using
        # the UNIX epoch as the date offset
        ftime = dt.datetime.strptime(
            "{:4d}-{:03d}".format(
                sdata['YEAR'].values.astype(int),
                sdata['DOY'].values.astype(int)), '%Y-%j') + (
                    pds.to_datetime(sdata['time'].values).to_pydatetime()
                    - dt.datetime(1970, 1, 1))

        # Get the updated dataset
        ndata = xr.Dataset(new_data) if update_new else sdata
        ndata['time'] = ftime

        # Assign a datetime variable, making indexing possible
        single_data[i] = ndata.assign_coords(
            {'time': ndata['time']}).expand_dims(dim='time')

    # Combine all the data, indexing along time
    data = xr.combine_by_coords(single_data)

    # TODO(https://github.com/pysat/pysat/issues/1078): Update the metadata by
    # removing 'TIME', once possible

    return data, mdata
