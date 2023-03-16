# -*- coding: utf-8 -*-
"""Module for the TIMED GUVI instrument.

Supports the Global UltraViolet Imager (GUVI) instrument on the Thermosphere
Ionosphere Mesosphere Energetics Dynamics (TIMED) satellite data from the
NASA Coordinated Data Analysis Web (CDAWeb).

From JHU APL (L2 Data):

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
import numpy as np
import warnings
import xarray as xr

import pysat
from pysat.instruments.methods import general as mm_gen
from pysat import logger

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
multi_file_day = True  # This is only true for EDR-AUR

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {iid: {tag: dt.datetime(2005, 6, 28) for tag in inst_ids[iid]
               for iid in inst_ids.keys()}

# ----------------------------------------------------------------------------
# Instrument methods

# Use standard init routine
init = functools.partial(mm_nasa.init, module=mm_timed, name=name)

# No cleaning, use standard warning function instead
clean = mm_nasa.clean_warn

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
url_mode = {tag: 'imaging' if tag == 'edr-aur' else tag.split('-')[1]
            for tag in tags.keys()}
download_tags = {
    sat_id: {tag: {'remote_dir': url.format(lvl=url_lvl[tag], url_mode[tag])
                   'fname': fname.format(lvl=file_lvl[sat_id], mode=mode[tag])}
             for tag in tags.keys()} for sat_id in inst_ids.keys()}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)


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

        inst = pysat.Instrument('timed', 'guvi',
                                inst_id='high_res', tag='sdr-imaging')
        inst.load(2005, 179)

    """
    if tag == 'edr-aur':
        data, meta = jhuapl.load_edr_aurora(fnames, tag, inst_id,
                                            pandas_format=pandas_format)
    else:
        meta = pysat.Meta()

        def get_dt_objects(dataset, tag):
            dts = []
            for i, year in enumerate(dataset['YEAR_%s' % tag].data):
                idt = dt.datetime(year, 1, 1) + dt.timedelta(
                    days=float(dataset['DOY_%s' % tag].data[i] - 1),
                    seconds=float(dataset['TIME_%s' % tag].data[i]))
                dts.append(idt)
            return dts

        # Dimensions for time variables
        # night/day along, cross and time variables are within
        #    imaging low_res/high_res and spectrograph high_res/low_res
        # imaging high_res also has dims DayAur
        # spectrograph low_res also has dims GAIMDay, GAIMNight
        dims = ['time']
        if 'sdr-imag' in tag:
            dims = dims + ['time_auroral']
        elif 'sdr-spect' in tag:
            if 'low' in inst_id:
                dims = dims + ['time_gaim_day', 'time_gaim_night']

        # Separate and concatenate into datasets
        inners = {dim: None for dim in dims}

        for path in fnames:
            data = xr.open_dataset(path, chunks='auto')

            # Collect datetime objects
            day_dts = np.array(get_dt_objects(data, "DAY"))
            night_dts = np.array(get_dt_objects(data, "NIGHT"))
            if 'sdr-imag' in tag:
                aur_dts = get_dt_objects(data, "DAY_AURORAL")
            elif 'sdr-spect' in tag:
                if 'low' in inst_id:
                    gaimday_dts = get_dt_objects(data, "GAIM_DAY")
                    gaimnight_dts = get_dt_objects(data, "GAIM_NIGHT")

            # Drop out redundant time variables
            data = data.drop_vars(["YEAR_DAY", "DOY_DAY", "TIME_DAY",
                                   "TIME_EPOCH_DAY", "YEAR_NIGHT", "DOY_NIGHT",
                                   "TIME_NIGHT", "TIME_EPOCH_NIGHT"])
            if 'sdr-imag' in tag:
                data = data.drop_vars(["YEAR_DAY_AURORAL", "DOY_DAY_AURORAL",
                                       "TIME_DAY_AURORAL",
                                       "TIME_EPOCH_DAY_AURORAL"])
            elif 'sdr-spect' in tag:
                if 'low' in inst_id:
                    data = data.drop_vars(["YEAR_GAIM_DAY", "DOY_GAIM_DAY",
                                           "TIME_GAIM_DAY", "TIME_GAIM_NIGHT",
                                           "YEAR_GAIM_NIGHT", "DOY_GAIM_NIGHT"])

            if day_dts.size != night_dts.size:
                raise Exception("nAlongDay & nAlongNight have different dimensions")

            if np.any(day_dts != night_dts):
                raise Exception("time along day and night are different")

            # Renaming along/cross dimensions
            data = data.rename_dims({"nAlongDay": "nAlong",
                                     "nAlongNight": "nAlong"})

            # 'nCross' dimension only in imaging
            if 'sdr-imag' in tag:

                if data.nCrossDay.size != data.nCrossNight.size:
                    raise Exception("nCrossDay/Night have different dimensions")

                data = data.rename_dims({"nCrossDay": "nCross",
                                         "nCrossNight": "nCross"})

            # 'nAlong' will be renamed as 'time' to follow pysat standards
            data = data.swap_dims({"nAlong": "time"})
            if 'sdr-imag' in tag:
                data = data.swap_dims({"nAlongDayAur": "time_auroral"})
            elif 'sdr-spect' in tag:
                if 'low' in inst_id:
                    data = data.swap_dims({"nAlongGAIMDay": "time_gaim_day",
                                           "nAlongGAIMNight": "time_gaim_night"})

            # Update time variables
            # night_dts and day_dts are the same temporal array
            data = data.assign(time=night_dts)
            if 'sdr-imag' in tag:
                data = data.assign(time_auroral=aur_dts)
            elif 'sdr-spect' in tag:
                if 'low' in inst_id:
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
                inners = {dim: xr.concat([inners[dim], jnners[dim]], dim=dim)
                         for dim in dims}

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

        if 'sdr-imag' in tag:
            coords = coords + ['PIERCEPOINT_DAY_LATITUDE_AURORAL',
                               'PIERCEPOINT_DAY_LONGITUDE_AURORAL',
                               'PIERCEPOINT_DAY_ALTITUDE_AURORAL',
                               'PIERCEPOINT_DAY_SZA_AURORAL']
        elif 'sdr-spect' in tag:
            coords = coords + ['PIERCEPOINT_NIGHT_ZENITH_ANGLE',
                               'PIERCEPOINT_NIGHT_SAZIMUTH',
                               'PIERCEPOINT_DAY_ZENITH_ANGLE',
                               'PIERCEPOINT_DAY_SAZIMUTH']

        data = data.set_coords(coords)

        # Set 'nchan' and 'nCross' as coordinates
        if 'sdr-imag' in tag:
            coords = {"nchan": ["121.6nm", "130.4nm", "135.6nm",
                                "LBHshort", "LBHlong"],
                      "nchanAur": ["121.6nm", "130.4nm", "135.6nm",
                                   "LBHshort", "LBHlong"],
                      "nCross": data.nCross.data,
                      "nCrossDayAur": data.nCrossDayAur.data}
        elif 'sdr-spect' in tag:
            coords = {"nchan": ["121.6nm", "130.4nm", "135.6nm",
                                "LBHshort", "LBHlong", "?"]}

        data = data.assign_coords(coords=coords)

        # Sort
        data = data.sortby("time")

    return data, meta
