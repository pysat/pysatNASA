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
import xarray as xr
import warnings
import pysat
from datetime import datetime,timedelta

from pysat import logger
from pysat.instruments.methods import general as mm_gen

from pysatNASA.instruments.methods import cdaweb as cdw
from h5py._hl import dataset

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
    self.pandas_format=False

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
basic_tag = {'remote_dir': ''.join(('/pub/data/timed/guvi/levels_v13/level1c/imaging',
                                    '/{year:4d}/{day:03d}/')),
             'fname': fname}
download_tags = {'': {'': basic_tag}}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files, supported_tags=download_tags)

# Set the load routine
def load(fnames, tag=None, inst_id=None):
    """Load TIMED GUVI data into `xarray.DataSet` and `pysat.Meta` objects.
 
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
    labels = {  'units': ('units', str), 'name': ('long_name', str),
                'notes': ('notes', str), 'desc': ('desc', str),
                'plot': ('plot_label', str), 'axis': ('axis', str),
                'scale': ('scale', str),
                'min_val': ('value_min', float),
                'max_val': ('value_max', float),
                'fill_val': ('fill', float)}
    meta = pysat.Meta(labels=labels)

    daysubset,nightsubset,auroralsubset=None,None,None
    for path in fnames:
        dataset=xr.load_dataset(path)
        
        #separate into auroral, night and day datasets
        auroralkeys=list(filter(lambda k:"_AURORAL" in k[-8:],dataset.keys()))
        nightkeys=list(filter(lambda k:"_NIGHT" in k,dataset.keys()))
        daykeys=list(filter(lambda k:"_DAY" in k and "_AURORAL" not in k,dataset.keys()))
        otherkeys=list( filter( lambda k:k not in (daykeys+nightkeys+auroralkeys),dataset.keys() ) )
        
        ith_daysubset=dataset.drop_vars(auroralkeys+nightkeys)
        ith_nightsubset=dataset.drop_vars(auroralkeys+daykeys+otherkeys)
        ith_auroralsubset=dataset.drop_vars(daykeys+nightkeys+otherkeys)
        
        #Updating epoch time variables, and dropping redundant time variables year, doy, day
        dts=[datetime(year,1,1)+timedelta(days=float(ith_daysubset.DOY_DAY.data[i]-1),seconds=ith_daysubset.TIME_DAY.data[i]) for i,year in enumerate(ith_daysubset.YEAR_DAY.data)]
        ith_daysubset=ith_daysubset.drop_vars(["YEAR_DAY","DOY_DAY","TIME_DAY","TIME_EPOCH_DAY"])
        ith_daysubset=ith_daysubset.assign( { 'TIME_EPOCH_DAY': xr.DataArray(data=dts,dims=('nAlongDay')) } )
        
        dts=[datetime(year,1,1)+timedelta(days=float(ith_nightsubset.DOY_NIGHT.data[i]-1),seconds=ith_nightsubset.TIME_NIGHT.data[i]) for i,year in enumerate(ith_nightsubset.YEAR_NIGHT.data)]
        ith_nightsubset=ith_nightsubset.drop_vars(["YEAR_NIGHT","DOY_NIGHT","TIME_NIGHT",'TIME_EPOCH_NIGHT'])
        ith_nightsubset=ith_nightsubset.assign( { 'TIME_EPOCH_NIGHT': xr.DataArray(data=dts,dims=('nAlongNight')) } )
        
        dts=[datetime(year,1,1)+timedelta(days=float(ith_auroralsubset.DOY_DAY_AURORAL.data[i]-1),seconds=ith_auroralsubset.TIME_DAY_AURORAL.data[i]) for i,year in enumerate(ith_auroralsubset.YEAR_DAY_AURORAL.data)]
        ith_auroralsubset=ith_auroralsubset.drop_vars(["YEAR_DAY_AURORAL","DOY_DAY_AURORAL","TIME_DAY_AURORAL","TIME_EPOCH_DAY_AURORAL"])
        ith_auroralsubset=ith_auroralsubset.assign( { 'TIME_EPOCH_DAY_AURORAL': xr.DataArray(data=dts,dims=('nAlongDayAur')) } )
        
        #concatenate along corresponding dimension
        if daysubset is None:
            daysubset=ith_daysubset
            nightsubset=ith_nightsubset
            auroralsubset=ith_auroralsubset
        else:
            daysubset=xr.concat([daysubset,ith_daysubset],dim='nAlongDay')
            nightsubset=xr.concat([nightsubset,ith_nightsubset],dim='nAlongNight')
            auroralsubset=xr.concat([auroralsubset,ith_auroralsubset],dim='nAlongDayAur')
    
    #merge all datasets
    data=daysubset
    data=data.merge(nightsubset)
    data=data.merge(auroralsubset)

    return data, meta




