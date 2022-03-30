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
- no tag required

Warnings
--------
- Currently no cleaning routine.


Example
-------
::

    import pysat
    guvi = pysat.Instrument(platform='timed', name='guvi')
    guvi.download(dt.datetime(2005, 6, 20), dt.datetime(2005, 6, 21))
    guvi.load(yr=2005,doy=171)

Author
------
L. A. Navarro (luis.navarro@colorado.edu)

"""

import datetime as dt
import functools
import pandas as pds
import warnings
import pysat

from pysat import logger
from pysat.instruments.methods import general as mm_gen

from pysatNASA.instruments.methods import cdaweb as cdw

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'timed'
name = 'guvi'
tags = {'': ''}
inst_ids = {'': [tag for tag in tags.keys()]}

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'': dt.datetime(2005, 6, 20)}}

# ----------------------------------------------------------------------------
# Instrument methods


def init(self):
    """Initializes the Instrument object with instrument specific values.

    Runs once upon instantiation.

    """

    rules_url = 'http://guvitimed.jhuapl.edu/home_guvi-datausage'
    ackn_str = ' '.join(('Please see the Rules of the Road at', rules_url))
    logger.info(ackn_str)
    self.acknowledgements = ackn_str
    self.references = ' '.join(('Paxton,L. J., Christensen, A. B., Humm, D. C., Ogorzalek,',
                                'B. S., Pardoe, C. T., Monison, D., Weiss, M. B., Cram, W.,',
                                'Lew, P. H., Mabry, D. J., Goldstena, J. O., Gary, A.,', 
                                'Persons, D. F., Harold, M. J., Alvarez, E. B., ErcoF, C. J.,',
                                'Strickland, D. J., Meng, C.-I.',
                                'Global ultraviolet imager (GUVI): Measuring composition and',
                                'energy inputs for the NASA Thermosphere Ionosphere Mesosphere',
                                'Energetics and Dynamics (TIMED) mission.',
                                'Optical spectroscopic techniques and instrumentation for atmospheric',
                                'and space research III. Vol. 3756. International Society for Optics',
                                'and Photonics, 1999.'))

    return


def clean(self):
    """Routine to return TIMED GUVI data cleaned to the specified level

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
basic_tag = {'remote_dir': ''.join(('/pub/data/timed/guvi/levels_v13/level1c/imaging/',
                                    '/{year:4d}/{day:03d}/')),
             'fname': fname}
download_tags = {'': {'': basic_tag}}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files, supported_tags=download_tags)

# Set the load routine
# load = cdw.load
# load = functools.partial(cdw.load, flatten_twod=False,file_cadence=dt.timedelta(hours=1))
def load(fnames, tag=None, inst_id=None):
    """Load ICON IVM data into `pandas.DataFrame` and `pysat.Meta` objects.

    This routine is called as needed by pysat. It is not intended
    for direct user interaction.

    Parameters
    ----------
    fnames : array-like
        iterable of filename strings, full path, to data files to be loaded.
        This input is nominally provided by pysat itself.
    tag : string
        tag name used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself.
    inst_id : string
        Satellite ID used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself.
    keep_original_names : boolean
        if True then the names as given in the netCDF ICON file
        will be used as is. If False, a preamble is removed.

    Returns
    -------
    data : pds.DataFrame
        A pandas DataFrame with data prepared for the pysat.Instrument
    meta : pysat.Meta
        Metadata formatted for a pysat.Instrument object.

    Note
    ----
    Any additional keyword arguments passed to pysat.Instrument
    upon instantiation are passed along to this routine.

    Examples
    --------
    ::

        inst = pysat.Instrument('icon', 'ivm', inst_id='a', tag='')
        inst.load(2020, 1)

    """

    labels = {'units': ('Units', str), 'name': ('Long_Name', str),
              'notes': ('Var_Notes', str), 'desc': ('CatDesc', str),
              'min_val': ('ValidMin', float),
              'max_val': ('ValidMax', float), 'fill_val': ('FillVal', float)}

    data, meta = pysat.utils.load_netcdf4(fnames, epoch_name='Epoch',file_format='netcdf4',
                                          labels=labels)

    return data, meta

