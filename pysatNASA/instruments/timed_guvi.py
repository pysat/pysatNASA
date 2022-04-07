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
tags = {'': ''}
inst_ids = {'': [tag for tag in tags.keys()]}

pandas_format = False

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'': dt.datetime(2005, 6, 20)}}

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
fname = 'TIMED_GUVI_L1C-2-disk-IMG_{year:04d}{day:03d}'\
        '{hour:02d}{minute:02d}{second:02d}-{end:13d}_'\
        'REV{rev:06d}_Av{version:02d}-{versionb:02d}r{revision:03d}.nc'
supported_tags = {'': {'': fname}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags,)

# Set the download routine
basic_tag = {'remote_dir': ''.join(('/pub/data/timed/guvi/levels_v13/level1c/',
                                    'imaging/{year:4d}/{day:03d}/')),
             'fname': fname}
download_tags = {'': {'': basic_tag}}
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

        inst = pysat.Instrument('timed', 'guvi')
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

    dayset, nightset, aurset = None, None, None
    for path in fnames:
        dataset = xr.load_dataset(path)

        # Separate into day, night and auroral datasets
        auroralkeys, nightkeys, daykeys, otherkeys = [], [], [], []
        for key in dataset.keys():
            if "_NIGHT" in key:
                nightkeys.append(key)
            elif "_AURORAL" in key:
                auroralkeys.append(key)
            elif "_DAY" in key:
                daykeys.append(key)
            else:
                otherkeys.append(key)

        i_dayset = dataset.drop_vars(auroralkeys + nightkeys)
        i_nightset = dataset.drop_vars(auroralkeys + daykeys + otherkeys)
        i_auroralset = dataset.drop_vars(daykeys + nightkeys + otherkeys)

        # Concatenate along corresponding dimension
        if dayset is None:
            dayset = i_dayset
            nightset = i_nightset
            aurset = i_auroralset
        else:
            dayset = xr.concat([dayset, i_dayset], dim='nAlongDay')
            nightset = xr.concat([nightset, i_nightset], dim='nAlongNight')
            aurset = xr.concat([aurset, i_auroralset], dim='nAlongDayAur')

    data = dayset
    data = data.merge(nightset)
    data = data.merge(aurset)

    def get_dt_objects(dataset, tag):
        dts = []
        for i, year in enumerate(dataset['YEAR_%s' % tag].data):
            idt = dt.datetime(year, 1, 1) + dt.timedelta(
                days=float(dataset['DOY_%s' % tag].data[i] - 1),
                seconds=float(dataset['TIME_%s' % tag].data[i]))
            dts.append(idt)
        return dts

    # Dimension 'nCross' is the same regardless of day, night or auroral
    data = data.swap_dims({"nCrossDay": "nCross",
                           "nCrossNight": "nCross",
                           "nCrossDayAur": "nCross", })

    # Collecting datetime objects
    day_dts = np.array(get_dt_objects(data, "DAY"))
    night_dts = np.array(get_dt_objects(data, "NIGHT"))
    aur_dts = get_dt_objects(data, "DAY_AURORAL")

    # Drop redundant time variables
    data = data.drop_vars(["YEAR_DAY", "DOY_DAY",
                           "TIME_DAY", "TIME_EPOCH_DAY",
                           "YEAR_NIGHT", "DOY_NIGHT",
                           "TIME_NIGHT", "TIME_EPOCH_NIGHT",
                           "YEAR_DAY_AURORAL", "DOY_DAY_AURORAL",
                           "TIME_DAY_AURORAL",
                           "TIME_EPOCH_DAY_AURORAL"])

    # Dimension 'nAlong' should be the same for day and night.
    # It will be renamed as 'time' to follow pysat standards.
    if np.all(np.equal(day_dts, night_dts)):
        data = data.swap_dims({"nAlongDay": "time",
                               "nAlongNight": "time"})
    else:
        data = data.swap_dims({"nAlongDay": "time"})

        warnings.warn(' '.join('time dimension for night and day should',
                               'be the same. nAlongDay will be used as time.',
                               ))
    data = data.swap_dims({"nAlongDayAur": "timeDayAur"})

    # Updating time variables
    data = data.assign(time=day_dts)
    if 'nAlongNight' in data.dims:
        data = data.assign(timeNight=night_dts)
    data = data.assign(timeDayAur=aur_dts)

    # Setting up coordinates
    coords = ['PIERCEPOINT_NIGHT_LATITUDE',
              'PIERCEPOINT_NIGHT_LONGITUDE',
              'PIERCEPOINT_NIGHT_ALTITUDE',
              'PIERCEPOINT_NIGHT_SZA',
              'PIERCEPOINT_DAY_LATITUDE',
              'PIERCEPOINT_DAY_LONGITUDE',
              'PIERCEPOINT_DAY_ALTITUDE',
              'PIERCEPOINT_DAY_SZA',
              'PIERCEPOINT_DAY_LATITUDE_AURORAL',
              'PIERCEPOINT_DAY_LONGITUDE_AURORAL',
              'PIERCEPOINT_DAY_ALTITUDE_AURORAL',
              'PIERCEPOINT_DAY_SZA_AURORAL']
    data = data.set_coords(coords)

    # Set 'nchan' as coordinate
    coords = {"nchan": ["121.6nm", "130.4nm", "135.6nm", "LBHshort", "LBHlong"],
              "nCross": range(13)}
    data = data.assign_coords(coords=coords)

    return data, meta
