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
    'low'
    'high'
inst_id
    'imaging'
    'spectrograph'

Note
----

Warnings
--------
Currently no cleaning routine.

Example
-------
::

    import pysat
    guvi = pysat.Instrument(platform='timed', name='guvi', inst_id='imaging', 
                            tag='low')
    guvi.download(dt.datetime(2005, 6, 28), dt.datetime(2005, 6, 29))
    guvi.load(yr=2005, doy=171)

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
tags = {'high': 'Level 1C high resolution data',
        'low': 'Level 1C low resolution data'}
inst_ids = {'imaging': list(tags.keys()),
            'spectrograph': list(tags.keys())}

pandas_format = False

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'imaging': {tag: dt.datetime(2005, 6, 28) for tag in tags.keys()},
               'spectrograph': {tag: dt.datetime(2005, 6, 28) for tag in tags.keys()}}

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

fname = ''.join(('TIMED_GUVI_L1C{res:s}-disk-{mode:s}_{{year:04d}}{{day:03d}}',
                 '{{hour:02d}}{{minute:02d}}{{second:02d}}',
                 '-?????????????_REV??????_',
                 'Av{{version:02d}}-??r{{revision:03d}}.nc'))

supported_tags = {inst: {tag: fname.format(res = "-2" if 'low' in tag else "",
                                           mode = "IMG" if 'imag' in inst else "SPECT")
                        for tag in tags.keys()}
                 for inst in inst_ids}

list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags,)

# Set the download routine
url = ''.join(('/pub/data/timed/guvi/levels_v13/level1c/{mode:s}/',
               '{{year:4d}}/{{day:03d}}/'))

supported_urls = {inst: {tag: url.format(mode=inst)
                        for tag in tags.keys()}
                 for inst in inst_ids}

download_tags = {inst: {tag: {'remote_dir': supported_urls[inst][tag],
                              'fname': supported_tags[inst][tag]}
                       for tag in tags.keys()}
                for inst in inst_ids.keys()}

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

        inst = pysat.Instrument('timed', 'guvi', inst_id='imaging', tag='high')
        inst.load(2005, 179)

    """
    labels = {'units': ('units', str), 'name': ('long_name', str),
              'notes': ('notes', str), 'desc': ('desc', str),
              'plot': ('plot_label', str), 'axis': ('axis', str),
              'scale': ('scale', str),
              'min_val': ('value_min', float),
              'max_val': ('value_max', float),
              'fill_val': ('fill', float)}
    meta = pysat.Meta(labels=labels)

    def get_dt_objects(dataset, tag):
        dts = []
        for i, year in enumerate(dataset['YEAR_%s' % tag].data):
            idt = dt.datetime(year, 1, 1) + dt.timedelta(
                days=float(dataset['DOY_%s' % tag].data[i] - 1),
                seconds=float(dataset['TIME_%s' % tag].data[i]))
            dts.append(idt)
        return dts

    # Dimensions for time variables
    # night/day along, cross and time are the same imaging low, high, spectrograph low, high
    # imaging high possess extra dims DayAur
    # spectrograph low possess extra dims GAIMDay, GAIMNight
    dims = ['time']
    if 'imag' in inst_id:
        dims = dims + ['time_auroral']
    elif 'spect' in inst_id:
        if 'low' in tag:
            dims = dims + ['time_gaim_day', 'time_gaim_night']

    # Separate and concatenate into datasets
    inners = {dim: None for dim in dims}

    for path in fnames:
        data = xr.open_dataset(path, chunks='auto')

        # Collect datetime objects
        day_dts = np.array(get_dt_objects(data, "DAY"))
        night_dts = np.array(get_dt_objects(data, "NIGHT"))
        if 'imag' in inst_id:
            aur_dts = get_dt_objects(data, "DAY_AURORAL")
        elif 'spect' in inst_id:
            if 'low' in tag:
                gaimday_dts = get_dt_objects(data, "GAIM_DAY")
                gaimnight_dts = get_dt_objects(data, "GAIM_NIGHT")

        # Drop out redundant time variables
        data = data.drop_vars(["YEAR_DAY", "DOY_DAY", "TIME_DAY", "TIME_EPOCH_DAY",
                               "YEAR_NIGHT", "DOY_NIGHT",
                               "TIME_NIGHT", "TIME_EPOCH_NIGHT"])
        if 'imag' in inst_id:
            data = data.drop_vars(["YEAR_DAY_AURORAL", "DOY_DAY_AURORAL",
                                   "TIME_DAY_AURORAL", "TIME_EPOCH_DAY_AURORAL"])
        elif 'spect' in inst_id:
            if 'low' in tag:
                data = data.drop_vars(["YEAR_GAIM_DAY", "DOY_GAIM_DAY",
                                       "TIME_GAIM_DAY", "TIME_GAIM_NIGHT",
                                       "YEAR_GAIM_NIGHT", "DOY_GAIM_NIGHT"])

        if day_dts.size != night_dts.size:
            raise Exception("nAlongDay & nAlongNight have different dimensions")

        if np.any(day_dts != night_dts):
            raise Exception("time along day and night are different")

        # Renaming along/cross dimensions
        data = data.rename_dims({"nAlongDay":"nAlong", "nAlongNight":"nAlong"})

        # 'nCross' dimension only in imaging 
        if 'imag' in inst_id:

            if data.nCrossDay.size != data.nCrossNight.size:
                raise Exception("nCrossDay/Night have different dimensions")

            data = data.rename_dims({"nCrossDay":"nCross",
                                     "nCrossNight":"nCross"})

        # 'nAlong' will be renamed as 'time' to follow pysat standards
        data = data.swap_dims({"nAlong": "time"})
        if 'imag' in inst_id:
            data = data.swap_dims({"nAlongDayAur": "time_auroral"})
        elif 'spect' in inst_id:
            if 'low' in tag:
                data = data.swap_dims({"nAlongGAIMDay": "time_gaim_day",
                                       "nAlongGAIMNight": "time_gaim_night"})

        # Update time variables
        # night_dts and day_dts are the same temporal array 
        data = data.assign(time=night_dts)
        if 'imag' in inst_id:
            data = data.assign(time_auroral=aur_dts)
        elif 'spect' in inst_id:
            if 'low' in tag:
                data = data.assign(time_gaim_day=gaimday_dts,
                                   time_gaim_night=gaimnight_dts)

        # Separate into inner datasets
        inner_keys = {dim: [] for dim in dims}

        for dim in dims:
            for key in data.keys():
                if dim in data[key].dims:
                    inner_keys[dim].append(key)

        jnners = {dim: data.get(inner_keys[dim]) for dim in dims}

        # Add 'single_var's into 'time' dataset to keep track
        sv_keys = [v.name for v in data.values() if 'single_var' in v.dims]
        singlevar_set = data.get(sv_keys)
        jnners['time'] = xr.merge([jnners['time'], singlevar_set])

        # Concatenate along corresponding dimension
        if inners['time'] is None:
            inners = jnners
        else:
            inners = {dim : xr.concat([inners[dim], jnners[dim]], dim=dim)
                      for dim in dims }

    data = xr.merge([inners[dim] for dim in dims])

    # Set up coordinates
    coords = ['PIERCEPOINT_NIGHT_LATITUDE',
              'PIERCEPOINT_NIGHT_LONGITUDE',
              'PIERCEPOINT_NIGHT_ALTITUDE',
              'PIERCEPOINT_NIGHT_SZA',
              'PIERCEPOINT_DAY_LATITUDE',
              'PIERCEPOINT_DAY_LONGITUDE',
              'PIERCEPOINT_DAY_ALTITUDE',
              'PIERCEPOINT_DAY_SZA']

    if 'imag' in inst_id:
        coords = coords + ['PIERCEPOINT_DAY_LATITUDE_AURORAL',
                           'PIERCEPOINT_DAY_LONGITUDE_AURORAL',
                           'PIERCEPOINT_DAY_ALTITUDE_AURORAL',
                           'PIERCEPOINT_DAY_SZA_AURORAL']
    elif 'spect' in inst_id:
        coords = coords + ['PIERCEPOINT_NIGHT_ZENITH_ANGLE',
                           'PIERCEPOINT_NIGHT_SAZIMUTH',
                           'PIERCEPOINT_DAY_ZENITH_ANGLE',
                           'PIERCEPOINT_DAY_SAZIMUTH']

    data = data.set_coords(coords)

    # Set 'nchan' and 'nCross' as coordinates
    if 'imag' in inst_id:
        coords = {"nchan": ["121.6nm", "130.4nm", "135.6nm",
                            "LBHshort", "LBHlong"],
                  "nchanAur": ["121.6nm", "130.4nm", "135.6nm",
                               "LBHshort", "LBHlong"],
                  "nCross": data.nCross.data,
                  "nCrossDayAur": data.nCrossDayAur.data}
    elif 'spect' in inst_id:
        coords = {"nchan": ["121.6nm", "130.4nm", "135.6nm",
                            "LBHshort", "LBHlong","?"]}

    data = data.assign_coords(coords=coords)

    # Sort
    data = data.sortby("time")

    return data, meta
