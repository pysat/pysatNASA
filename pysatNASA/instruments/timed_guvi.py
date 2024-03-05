# -*- coding: utf-8 -*-
"""Module for the TIMED GUVI instrument.

Supports the Global UltraViolet Imager (GUVI) instrument on the Thermosphere
Ionosphere Mesosphere Energetics Dynamics (TIMED) satellite data from the
NASA Coordinated Data Analysis Web (CDAWeb).

From JHU APL:

The Global Ultraviolet Imager (GUVI) is one of four instruments that constitute
the TIMED spacecraft, the first mission of the NASA Solar Connections program.
The TIMED spacecraft is being built by Johns Hopkins University Applied Physics
Laboratory and GUVI is a joint collaboration between JHU/APL and the Aerospace
Corporation. TIMED will be used to study the energetics and dynamics of the
Mesosphere and lower Thermosphere between an altitude of approximately 60 to 180
kilometers.

References
----------
Larry J. Paxton, Andrew B. Christensen, David C. Humm, Bernard S. Ogorzalek, C.
Thompson Pardoe, Daniel Morrison, Michele B. Weiss, W. Crain, Patricia H. Lew,
Dan J. Mabry, John O. Goldsten, Stephen A. Gary, David F. Persons, Mark J.
Harold, E. Brian Alvarez, Carl J. Ercol, Douglas J. Strickland, and Ching-I.
Meng "Global ultraviolet imager (GUVI): measuring composition and energy inputs
for the NASA Thermosphere Ionosphere Mesosphere Energetics and Dynamics (TIMED)
mission", Proc. SPIE 3756, Optical Spectroscopic Techniques and Instrumentation
for Atmospheric and Space Research III, (20 October 1999);
https://doi.org/10.1117/12.366380

Properties
----------
platform
    'timed'
name
    'guvi'
tag
    'edr-aur'
    'sdr-imaging'
    'sdr-spectrograph'
inst_id
    ''
    'high_res'
    'low_res'

Warnings
--------
- Currently no cleaning routine.

Example
-------
::

    import pysat
    guvi = pysat.Instrument(platform='timed', name='guvi',
                            inst_id='sdr-imaging', tag='low_res')
    guvi.download(dt.datetime(2005, 6, 28), dt.datetime(2005, 6, 29))
    guvi.load(date=dt.datetime(2005, 6, 28))

"""

import datetime as dt
import functools
import xarray as xr

import pysat
from pysat.instruments.methods import general as mm_gen

from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import general as mm_nasa
from pysatNASA.instruments.methods import jhuapl
from pysatNASA.instruments.methods import timed as mm_timed

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'timed'
name = 'guvi'
tags = {'edr-aur': 'Level 2 Auroral disk imaging mode',
        'sdr-imaging': 'Level 1C imaging data',
        'sdr-spectrograph': 'Level 1C spectrograph data'}
inst_ids = {'': ['edr-aur'],
            'high_res': ['sdr-imaging', 'sdr-spectrograph'],
            'low_res': ['sdr-imaging', 'sdr-spectrograph']}

pandas_format = False
multi_file_day = True

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {
    iid: {tag: dt.datetime(2007 if tag.find('spectrograph') > 0 else 2005, 12,
                           13) for tag in inst_ids[iid]}
    for iid in inst_ids.keys()}
_test_load_opt = {iid: {tag: {'combine_times': True}
                        for tag in inst_ids[iid]}
                  for iid in ['high_res', 'low_res']}
_clean_warn = {inst_id: {tag: mm_nasa.clean_warnings
                         for tag in inst_ids[inst_id] if tag != 'sdr-imaging'}
               for inst_id in inst_ids.keys()}
for inst_id in ['high_res', 'low_res']:
    _clean_warn[inst_id]['sdr-imaging'] = {'dirty': mm_nasa.clean_warnings[
        'dirty']}

# ----------------------------------------------------------------------------
# Instrument methods

# Use standard init routine
init = functools.partial(mm_nasa.init, module=mm_timed, name=name)


def clean(self):
    """Clean TIMED GUVI imaging data.

    Note
    ----
        Supports 'clean', 'dusty', 'dirty', 'none'. Method is
        not called by pysat if clean_level is None or 'none'.

    """
    if self.tag == "sdr-imaging" and self.clean_level in ['clean', 'dusty']:
        # Find the flag variables
        dqi_vars = [var for var in self.variables if var.find('DQI') == 0]

        # Find the variables affected by each flag
        dat_vars = {dqi: [var for var in self.variables if var.find(dqi) > 0]
                    if dqi.find('AURORAL') >= 0 else
                    [var for var in self.variables if var.find('AURORAL') < 0
                     and var.find(dqi) > 0] for dqi in dqi_vars}

        for dqi in dqi_vars:
            if self.clean_level == 'clean':
                # For clean, require DQI of zero (MeV noise only)
                dqi_bad = self.data[dqi].values > 0
            else:
                # For dusty, allow the SAA region as well
                dqi_bad = self.data[dqi].values > 1

            # Apply the DQI mask to the data, replacing bad values with
            # appropriate fill values
            for dat_var in dat_vars[dqi]:
                if self.data[dat_var].shape == dqi_bad.shape or self.data[
                        dat_var].shape[:-1] == dqi_bad.shape:
                    # Only apply to data with the correct dimensions
                    fill_val = self.meta[dat_var, self.meta.labels.fill_val]
                    self.data[dat_var].values[dqi_bad] = fill_val
    else:
        # Follow the same warning format as the general clean warning, but
        # with additional information.
        pysat.logger.warning(' '.join(['No cleaning routines available for',
                                       self.platform, self.name, self.tag,
                                       self.inst_id, 'at clean level',
                                       self.clean_level]))
    return


def concat_data(self, new_data, combine_times=False, **kwargs):
    """Concatonate data to self.data for TIMED GUVI data.

    Parameters
    ----------
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
    # Establish the time dimensions by data type
    time_dims = [self.index.name]

    if self.tag == 'sdr-imaging':
        time_dims.append('time_auroral')
    elif self.tag == 'sdr-spectrograph':
        time_dims.extend(['time_gaim_day', 'time_gaim_night'])

    # Concatonate using the appropriate method for the number of time
    # dimensions
    if len(time_dims) == 1:
        # There is only one time dimensions, but other dimensions may
        # need to be adjusted
        new_data = pysat.utils.coords.expand_xarray_dims(
            new_data, self.meta, exclude_dims=time_dims)

        # Combine the data
        self.data = xr.combine_by_coords(new_data, **kwargs)
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
            inner_dat[self.index.name] = xr.merge([inner_dat[self.index.name],
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
                    [inners[dim] if dim == self.index.name else
                     inners[dim].rename_dims({dim: self.index.name})
                     for dim in time_dims if len(inners[dim].dims) > 0],
                    self.meta, dims_equal=False)
            else:
                data_list = [inners[dim] for dim in time_dims]

            # Combine all the data, indexing along time
            self.data = xr.merge(data_list)
    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
fname = ''.join(('TIMED_GUVI_{lvl:s}{mode:s}_{{year:04d}}{{day:03d}}',
                 '{{hour:02d}}{{minute:02d}}{{second:02d}}-?????????????_REV',
                 '??????_Av{{version:02d}}-??r{{revision:03d}}.nc'))
file_lvl = {'low_res': 'L1C-2-disk', 'high_res': 'L1C-disk', '': 'L2B'}
mode = {'sdr-imaging': '-IMG', 'sdr-spectrograph': '-SPECT',
        'edr-aur': '-edr-aur-IMG'}
supported_tags = {inst_id: {tag: fname.format(lvl=file_lvl[inst_id],
                                              mode=mode[tag])
                            for tag in tags.keys()}
                  for inst_id in inst_ids.keys()}
list_files = functools.partial(mm_gen.list_files, supported_tags=supported_tags)

# Set the download routine
url = ''.join(('/pub/data/timed/guvi/levels_v13/{lvl:s}/{mode:s}/',
               '{{year:4d}}/{{day:03d}}/'))
url_lvl = {'sdr-imaging': 'level1c', 'sdr-spectrograph': 'level1c',
           'edr-aur': 'level2b'}
url_mode = {tag: 'imaging/edr-aur' if tag == 'edr-aur' else tag.split('-')[1]
            for tag in tags.keys()}
download_tags = {iid: {tag: {'remote_dir': url.format(lvl=url_lvl[tag],
                                                      mode=url_mode[tag]),
                             'fname': fname.format(lvl=file_lvl[iid],
                                                   mode=mode[tag])}
                       for tag in tags.keys()} for iid in inst_ids.keys()}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)


# Set the load routine
def load(fnames, tag='', inst_id='', combine_times=False):
    """Load TIMED GUVI data into `xarray.DataSet` and `pysat.Meta` objects.

    This routine is called as needed by pysat. It is not intended
    for direct user interaction.

    Parameters
    ----------
    fnames : array-like
        iterable of filename strings, full path, to data files to be loaded.
        This input is nominally provided by pysat itself.
    tag : str
        tag name used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself.
    inst_id : str
        Satellite ID used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself.
    combine_times : bool
        For SDR data, optionally combine the different datetime coordinates
        into a single time coordinate (default=False)

    Returns
    -------
    data : xr.DataSet
        A xarray DataSet with data prepared for the pysat.Instrument
    meta : pysat.Meta
        Metadata formatted for a pysat.Instrument object.

    Raises
    ------
    ValueError
        If temporal dimensions are not consistent

    Note
    ----
    Any additional keyword arguments passed to pysat.Instrument
    upon instantiation are passed along to this routine.

    Examples
    --------
    ::

        inst = pysat.Instrument('timed', 'guvi',
                                inst_id='high_res', tag='sdr-imaging')
        inst.load(2005, 179)

    """
    if tag == 'edr-aur':
        data, meta = jhuapl.load_edr_aurora(fnames, tag, inst_id,
                                            pandas_format=pandas_format,
                                            strict_dim_check=False)
    else:
        data, meta = jhuapl.load_sdr_aurora(fnames, tag, inst_id,
                                            pandas_format=pandas_format,
                                            strict_dim_check=False,
                                            combine_times=combine_times)

    return data, meta
