# -*- coding: utf-8 -*-
"""Module for the DMSP SSUSI instrument.

Supports the Special Sensor Ultraviolet Spectrographic Imager (SSUSI)
instrument on Defense Meteorological Satellite Program (DMSP).

From JHU APL:

SSUSI was designed for the DMSP Block 5D-3 satellites. These satellites are
placed into nearly polar, sun-synchronous orbits at an altitude of about 850 km.
SSUSI is a remote-sensing instrument which measures ultraviolet (UV) emissions
in five different wavelength bands from the Earth's upper atmosphere. SSUSI is
mounted on a nadir-looking panel of the satellite. The multicolor images from
SSUSI cover the visible Earth disk from horizon to horizon and the anti-sunward
limb up to an altitude of approximately 520 km.

The UV images and the derived environmental data provide the Air Force Weather
Agency (Offutt Air Force Base, Bellevue, NE) with near real-time information
that can be utilized in a number of applications, such as maintenance of high
frequency (HF) communication links and related systems and assessment of the
environmental hazard to astronauts on the Space Station.

References
----------
Larry J. Paxton, Daniel Morrison, Yongliang Zhang, Hyosub Kil, Brian Wolven,
Bernard S. Ogorzalek, David C. Humm, and Ching-I. Meng "Validation of remote
sensing products produced by the Special Sensor Ultraviolet Scanning Imager
(SSUSI): a far UV-imaging spectrograph on DMSP F-16", Proc. SPIE 4485, Optical
Spectroscopic Techniques, Remote Sensing, and Instrumentation for Atmospheric
and Space Research IV, (30 January 2002); doi:10.1117/12.454268

Properties
----------
platform
    'dmsp'
name
    'ssusi'
tag
    'edr-aurora'
inst_id
    'f16', 'f17', 'f18', 'f19'


Warnings
--------
- Currently no cleaning routine.


"""

import datetime as dt
import functools
import numpy as np
import pandas as pds
import xarray as xr

from pysat.instruments.methods import general as mm_gen
from pysat.utils.io import load_netcdf

from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import dmsp as mm_dmsp
from pysatNASA.instruments.methods import general as mm_nasa

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'dmsp'
name = 'ssusi'
tags = {'edr-aurora': ''.join(['Electron energy flux and mean energy, auroral',
                               ' boundaries, identified discrete auroral arcs,',
                               ' hemispheric power, and magnetic field lines ',
                               'traced to 4 Earth radii'])}
inst_ids = {sat_id: list(tags.keys())
            for sat_id in ['f16', 'f17', 'f18', 'f19']}

pandas_format = False
multi_file_day = True

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {inst_id: {tag: dt.datetime(2015, 1, 1) for tag in tags.keys()}
               for inst_id in inst_ids.keys()}

# ----------------------------------------------------------------------------
# Instrument methods


# Use standard init routine
init = functools.partial(mm_nasa.init, module=mm_dmsp, name=name)

# No cleaning, use standard warning function instead
clean = mm_nasa.clean_warn

# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
fname = ''.join(['dmsp{inst_id:s}_ssusi_{tag:s}_{{year:04d}}{{day:03d}}T',
                 '{{hour:02d}}{{minute:02d}}{{second:02d}}-???????T??????-REV',
                 '?????_vA{{version:1d}}.?.?r{{cycle:03d}}.nc'])
supported_tags = {sat_id: {tag: fname.format(tag=tag, inst_id=sat_id)
                           for tag in tags.keys()}
                  for sat_id in inst_ids.keys()}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)


# Set the load routine
def load(fnames, tag='', inst_id=''):
    """Load DMSP SSUSI data and meta data.

    Parameters
    ----------
    fnames : array-like
        Iterable of filename strings, full path, to data files to be loaded.
    tag : str
        Tag name used to identify particular data set to be loaded (default='')
    inst_id : str
        DMSP satellite ID (default='')

    Returns
    -------
    data : pds.DataFrame or xr.Dataset
        Data to be assigned to the pysat.Instrument.data object.
    mdata : pysat.Meta
        Pysat Meta data for each data variable.

    Examples
    --------
    ::

        inst = pysat.Instrument('dmsp', 'ssusi', tag='edr-aurora',
                                inst_id='f16')
        inst.load(2006, 1)

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

        # Calculate the time for this data file
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


# Set the download routine
basic_tag = {'remote_dir': ''.join(('/pub/data/dmsp/dmsp{inst_id:s}/ssusi/',
                                    '/data/{tag:s}/{{year:4d}}/{{day:03d}}/')),
             'fname': fname}
download_tags = {
    sat_id: {tag: {btag: basic_tag[btag].format(tag=tag, inst_id=sat_id)
                   for btag in basic_tag.keys()} for tag in tags.keys()}
    for sat_id in inst_ids.keys()}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)
