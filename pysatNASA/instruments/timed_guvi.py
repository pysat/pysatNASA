# -*- coding: utf-8 -*-
"""Supports the GUVI instrument on TIMED.

Downloads data from the NASA Coordinated Data
Analysis Web (CDAWeb).

Supports two options for loading that may be
specified at instantiation.

Properties
----------
platform
    'timed'
name
    'guvi'
tag
    None
inst_id
    None supported

Note
----
No `tag` or `inst_id` required.

Warnings
--------
Currently no cleaning routine.


Example
-------
::

    import pysat
    guvi = pysat.Instrument(platform='timed', name='guvi')
    guvi.download(dt.datetime(2005, 6, 20), dt.datetime(2005, 6, 21))
    guvi.load(yr=2005, doy=171)

Author
------
L. A. Navarro (luis.navarro@colorado.edu)

"""

import datetime as dt
import functools
import numpy as np
import warnings
import xarray as xr

import pysat
from pysat.instruments.methods import general as mm_gen
from pysat import logger

from pysatNASA.instruments.methods import cdaweb as cdw

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'timed'
name = 'guvi'
tags = {'l1c_img': 'Level 1C imaging disk high resolution data',
        'l1c2_img': 'Level 1C imaging disk low resolution data',
        'l1c_spect': 'Level 1C spectrograh disk high resolution data',
        'l1c2_spect': 'Level 1C spectrograph disk low resolution data'}
inst_ids = {'': [tag for tag in tags.keys()]}

pandas_format = False

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {tag: dt.datetime(2005, 6, 28) for tag in tags}}

# ----------------------------------------------------------------------------
# Instrument methods

def init(self):
    """Initialize the Instrument object with references and acknowledgements."""

    rules_url = 'http://guvitimed.jhuapl.edu/home_guvi-datausage'
    ackn_str = ' '.join(('Please see the Rules of the Road at', rules_url))
    logger.info(ackn_str)
    self.acknowledgements = ackn_str
    self.references = ' '.join(('Paxton,L. J., Christensen, A. B., Humm,',
                                'D. C., Ogorzalek, B. S., Pardoe, C. T.,',
                                'Monison, D., Weiss, M. B., Cram, W.,',
                                'Lew, P. H., Mabry, D. J., Goldstena,',
                                'J. O., Gary, A., Persons, D. F., Harold,',
                                'M. J., Alvarez, E. B., ErcoF, C. J.,',
                                'Strickland, D. J., Meng, C.-I.',
                                'Global ultraviolet imager (GUVI): Measuring',
                                'composition and energy inputs for the NASA',
                                'Thermosphere Ionosphere Mesosphere Energetics',
                                'and Dynamics (TIMED) mission.',
                                'Optical spectroscopic techniques and',
                                'instrumentation for atmospheric and',
                                'space research III. Vol. 3756.',
                                'International Society for Optics',
                                'and Photonics, 1999.'))

    return


def clean(self):
    """Routine to return TIMED GUVI data cleaned to the specified level.

    Note
    ----
    No cleaning currently available.

    """
    warnings.warn('no cleaning routines available for TIMED GUVI data')

    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods
# Set the list_files routine
fname = ''.join(('TIMED_GUVI_{res:s}-disk-{mode:s}_{{year:04d}}{{day:03d}}',
                 '{{hour:02d}}{{minute:02d}}{{second:02d}}',
                 '-?????????????_REV??????_',
                 'Av{{version:02d}}-??r{{revision:03d}}.nc'))

tags_fmt = { tag: fname.format(res=tag.split('_')[0].replace("2","-2").upper(),
                               mode=tag[4:].replace("_","").upper())
                               for tag in tags}
supported_tags = {"": tags_fmt}

list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags,)

# Set the download routine
url = ''.join(('/pub/data/timed/guvi/levels_v13/level1c/{mode:s}/',
               '{{year:4d}}/{{day:03d}}/'))

tags_url = { tag: url.format(mode='imaging') if 'img' in tag else 
            url.format(mode='spectrograph') for tag in tags}
supported_urls = {"": tags_url}

download_tags = {inst_id:
                 {tag: {'remote_dir': supported_urls[''][tag],
                        'fname': supported_tags[''][tag]}
                  for tag in tags.keys()} for inst_id in inst_ids.keys()}

download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(
    cdw.list_remote_files, supported_tags=download_tags)


# Set the load routine
def load(fnames, tag='', inst_id=''):
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

    Returns
    -------
    data : xr.DataSet
        A xarray DataSet with data prepared for the pysat.Instrument
    meta : pysat.Meta
        Metadata formatted for a pysat.Instrument object.

    Note
    ----
    Any additional keyword arguments passed to pysat.Instrument
    upon instantiation are passed along to this routine.

    Examples
    --------
    ::

        inst = pysat.Instrument('timed', 'guvi', tag='l1c2_img')
        inst.load(2005, 171)

    """
    labels = {'units': ('units', str), 'name': ('long_name', str),
              'notes': ('notes', str), 'desc': ('desc', str),
              'plot': ('plot_label', str), 'axis': ('axis', str),
              'scale': ('scale', str),
              'min_val': ('value_min', float),
              'max_val': ('value_max', float),
              'fill_val': ('fill', float)}
    meta = pysat.Meta(labels=labels)

    # Dimensions for time variables
    if 'img' in tag:
        dims = ['nAlongDay', 'nAlongNight', 'nAlongDayAur', 'single_var']
    elif 'spect' in tag:
        dims = ['nAlongDay', 'nAlongNight', 'nAlongGAIMDay', 'nAlongGAIMNight',
                'single_var']

    # Separate and concatenate into datasets
    inners = {dim: None for dim in dims}

    for path in fnames:
        dataset = xr.load_dataset(path)
        print(path)

        # Separate into inner datasets
        _keys = {dim: [] for dim in dims}

        for dim in dims:
            for key in dataset.keys():
                if dim in dataset[key].dims:
                    _keys[dim].append(key)

        jnners = {dim: dataset.get(_keys[dim]) for dim in dims}

        # Concatenate along corresponding dimension
        if inners['nAlongDay'] is None:
            inners = jnners
        else:
            inners = { dim : xr.concat([inners[dim], jnners[dim]], dim=dim)
                       for dim in dims }

    data = xr.merge([inners[dim] for dim in dims])

    def get_dt_objects(dataset, tag):
        dts = []
        for i, year in enumerate(dataset['YEAR_%s' % tag].data):
            idt = dt.datetime(year, 1, 1) + dt.timedelta(
                days=float(dataset['DOY_%s' % tag].data[i] - 1),
                seconds=float(dataset['TIME_%s' % tag].data[i]))
            dts.append(idt)
        return dts

    # Collect datetime objects
    day_dts = np.array(get_dt_objects(data, "DAY"))
    night_dts = np.array(get_dt_objects(data, "NIGHT"))
    if 'img' in tag:
        aur_dts = get_dt_objects(data, "DAY_AURORAL")
    elif 'spect' in tag:
        gaimday_dts = get_dt_objects(data, "GAIM_DAY")
        gaimnight_dts = get_dt_objects(data, "GAIM_NIGHT")

    # Drop out redundant time variables
    data = data.drop_vars(["YEAR_DAY", "DOY_DAY", "TIME_DAY", "TIME_EPOCH_DAY",
                           "YEAR_NIGHT", "DOY_NIGHT",
                           "TIME_NIGHT", "TIME_EPOCH_NIGHT"])
    if 'img' in tag:
        data = data.drop_vars(["YEAR_DAY_AURORAL", "DOY_DAY_AURORAL",
                               "TIME_DAY_AURORAL", "TIME_EPOCH_DAY_AURORAL"])
    elif 'spect' in tag:
        data = data.drop_vars(["YEAR_GAIM_DAY", "DOY_GAIM_DAY", 
                               "TIME_GAIM_DAY", "TIME_GAIM_NIGHT",
                               "YEAR_GAIM_NIGHT", "DOY_GAIM_NIGHT"])

    # 'nAlongNight' will be renamed as 'time' to follow pysat standards
    data = data.swap_dims({"nAlongNight": "time"})

    # Update time variables
    # 'time_night' will be renamed as 'time' to follow pysat standard 
    data = data.assign(time_day=xr.DataArray(day_dts, dims=('nAlongDay')),
                       time=night_dts)
    if 'img' in tag:
        dt_aur=xr.DataArray(aur_dts, dims=('nAlongDayAur'))
        data = data.assign(time_auroral=dt_aur)
    elif 'spect' in tag:
        day_gaim = xr.DataArray(gaimday_dts, dims=('nAlongGAIMDay'))
        night_gaim = xr.DataArray(gaimnight_dts, dims=('nAlongGAIMNight'))
        data = data.assign(time_gaim_day=day_gaim, time_gaim_night=night_gaim)

    # Set up coordinates
    coords = ['PIERCEPOINT_NIGHT_LATITUDE',
              'PIERCEPOINT_NIGHT_LONGITUDE',
              'PIERCEPOINT_NIGHT_ALTITUDE',
              'PIERCEPOINT_NIGHT_SZA',
              'PIERCEPOINT_DAY_LATITUDE',
              'PIERCEPOINT_DAY_LONGITUDE',
              'PIERCEPOINT_DAY_ALTITUDE',
              'PIERCEPOINT_DAY_SZA']

    if 'img' in tag:
        coords = coords + ['PIERCEPOINT_DAY_LATITUDE_AURORAL',
                           'PIERCEPOINT_DAY_LONGITUDE_AURORAL',
                           'PIERCEPOINT_DAY_ALTITUDE_AURORAL',
                           'PIERCEPOINT_DAY_SZA_AURORAL']
    elif 'spect' in tag:
        coords = coords + ['PIERCEPOINT_NIGHT_ZENITH_ANGLE',
                           'PIERCEPOINT_NIGHT_SAZIMUTH',
                           'PIERCEPOINT_DAY_ZENITH_ANGLE',
                           'PIERCEPOINT_DAY_SAZIMUTH']

    data = data.set_coords(coords)

    # Set 'nchan' and 'nCross' as coordinates
    if 'img' in tag:
        coords = {"nchan": ["121.6nm", "130.4nm", "135.6nm",
                            "LBHshort", "LBHlong"],
                  "nchanAur": ["121.6nm", "130.4nm", "135.6nm",
                               "LBHshort", "LBHlong"],
                  "nCrossDay": range(13),
                  "nCrossNight": range(13),
                  "nCrossDayAur": range(13)}
    elif 'spect' in tag:
        coords = {"nchan": ["121.6nm", "130.4nm", "135.6nm",
                            "LBHshort", "LBHlong","extra"]}
    data = data.assign_coords(coords=coords)

    # Sort
    data = data.sortby("time")
    
    return data, meta
