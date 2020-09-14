""" Supports the Nmax data product from the GOLD spacecraft

"""
import datetime as dt
import functools
import warnings

import pysat
from pysat.instruments.methods import general as ps_gen
from pysatNASA.instruments.methods import cdaweb as cdw

platform = 'gold'
name = 'nmax'

tags = {'': 'Nmax data for the GOLD instrument'}
sat_ids = {'': ['']}
_test_dates = {'': {'': dt.datetime(2020, 1, 1)}}

fname = 'gold_l2_nmax_{year:04d}_{day:03d}_v01_r01_c01.nc'
supported_tags = {'': {'': fname}}
pandas_format = False

# use the CDAWeb methods list files routine
list_files = functools.partial(ps_gen.list_files,
                               supported_tags=supported_tags)

# support download routine
basic_tag = {'dir': '/pub/data/gold/level2/nmax',
             'remote_fname': '{year:4d}/' + fname,
             'local_fname': fname}
supported_tags = {'': {'': basic_tag}}
download = functools.partial(cdw.download, supported_tags)

# support listing files currently on CDAWeb
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=supported_tags)


def init(self):
    """Initializes the Instrument object with instrument specific values.

    Runs once upon instantiation.

    Parameters
    -----------
    inst : pysat.Instrument
        Instrument class object

    """
    ack_str = ' '.join(('This is a data product from the NASA Global-scale',
                        'Observations of the Limb and Disk (GOLD) mission, an',
                        'Heliophysics Explorer mission of opportunity launched',
                        'in January 2018.\n Responsibility of the mission',
                        'science falls to the Principal Investigator, Dr.',
                        'Richard Eastes at University of Colorado/LASP.\n',
                        'Validation of the L1B data products falls to the',
                        'instrument lead investigators/scientists.\n* EUV',
                        'Dr. Bill McClintock\nValidation of the L2 data',
                        'products falls to Computational Physics, Inc.\n* Dr.',
                        'Jerry Lumpe\n (https://gold.cs.ucf.edu/).\nOverall',
                        'validation of the products is overseen by the GOLD',
                        'Project Scientist Dr. Alan Burns.\nUsers of these',
                        'data should contact and acknowledge the Principal',
                        'Investigator Dr. Richard Eastes and the party',
                        'directly responsible for the data product and the',
                        'NASA Explorers Project Office.'))
    ref_str = ' '.join(('Eastes, R.W., McClintock, W.E., Burns, A.G. et al.',
                        'The Global-Scale Observations of the Limb and Disk',
                        '(GOLD) Mission. Space Sci Rev 212, 383–408 (2017).',
                        'https://doi.org/10.1007/s11214-017-0392-2'))
    pysat.logger.info(ack_str)
    self.meta.acknowledgements = ack_str
    self.meta.references = ref_str

    pass


# Custom load routine for netcdf files
def load(fnames, tag=None, sat_id=None):
    """Loads GOLD NMAX data using pysat into xarray

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
    sat_id : string
        Satellite ID used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself.
    **kwargs : extra keywords
        Passthrough for additional keyword arguments specified when
        instantiating an Instrument object. These additional keywords
        are passed through to this routine by pysat.

    Returns
    -------
    data, metadata
        Data and Metadata are formatted for pysat. Data is a pandas
        DataFrame while metadata is a pysat.Meta instance.

    Note
    ----
    Any additional keyword arguments passed to pysat.Instrument
    upon instantiation are passed along to this routine.

    Examples
    --------
    ::

        inst = pysat.Instrument('gold', 'nmax')
        inst.load(2019, 1)

    """

    data, mdata = pysat.utils.load_netcdf4(fnames, pandas_format=pandas_format)
    data['time'] = [dt.datetime.strptime(str(val), "b'%Y-%m-%dT%H:%M:%SZ'")
                    for val in data['scan_start_time'].values]

    return data, mdata


def clean(inst):
    """Provides data cleaning based upon clean_level.

    Routine is called by pysat, and not by the end user directly.

    Parameters
    -----------
    inst : pysat.Instrument
        Instrument class object, whose attribute clean_level is used to return
        the desired level of data selectivity.

    Note
    ----
        Supports 'clean', 'dusty', 'dirty', 'none'

    """

    warnings.warn("Cleaning actions for GOLD Nmax are not yet implemented.")
    return
