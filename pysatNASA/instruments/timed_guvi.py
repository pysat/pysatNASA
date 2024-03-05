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

_test_dates = {iid: {tag: dt.datetime(2005, 6, 28) for tag in inst_ids[iid]}
               for iid in inst_ids.keys()}
_test_load_opt = {iid: {tag: {'combine_times': True}
                        for tag in inst_ids[iid]}
                  for iid in ['high_res', 'low_res']}
# TODO(#218): Remove when compliant with multi-day load tests
_new_tests = {iid: {tag: False for tag in inst_ids[iid]}
              for iid in ['high_res', 'low_res']}
_clean_warn = {inst_id: {tag: mm_nasa.clean_warnings
                         for tag in inst_ids[inst_id]}
               for inst_id in inst_ids.keys()}

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
