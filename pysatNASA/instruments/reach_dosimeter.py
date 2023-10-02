# -*- coding: utf-8 -*-
"""The REACH dosimeter instrument.

Supports the dosimeter instrument on the Responsive Environmental Assessment
Commercially Hosted (REACH) mission.

The Responsive Environmental Assessment Commercially Hosted (REACH)
constellation is collection of 32 small sensors hosted on six orbital planes of
the Iridium-Next space vehicles in low earth orbit. Each sensor contains two
micro-dosimeters sensitive to the passage of charged particles from the Earth's
radiation belts. There are six distinct dosimeter types spread among the 64
individual sensors, which are unique in shielding and electronic threshold.
When taken together, this effectively enables a high time-cadence measurement
of protons and electrons in six integral energy channels over the entire globe.

Properties
----------
platform
    'reach'
name
    'dosimeter'
tag
    None Supported
inst_id
    '101', '102', '105', '108', '113', '114', '115', '116', '133', '134', '135',
    '136', '137', '138', '139', '140', '148', '149', '162', '163', '164', '165',
    '166', '169', '170', '171', '172', '173', '175', '176', '180', '181'


"""

import datetime as dt
import functools

from pysat.instruments.methods import general as mm_gen
from pysat.utils.io import load_netcdf

from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import general as mm_nasa
from pysatNASA.instruments.methods import reach as mm_reach

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'reach'
name = 'dosimeter'
tags = {'': 'Dosimeter data from the REACH mission'}
iids = ['101', '102', '105', '108', '113', '114', '115', '116', '133', '134',
        '135', '136', '137', '138', '139', '140', '148', '149', '162', '163',
        '164', '165', '166', '169', '170', '171', '172', '173', '175', '176',
        '180', '181']
inst_ids = {iid: [tag for tag in tags.keys()] for iid in iids}

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {iid: {tag: dt.datetime(2019, 12, 1) for tag in tags.keys()}
               for iid in inst_ids.keys()}

# ----------------------------------------------------------------------------
# Instrument methods


# Use standard init routine
init = functools.partial(mm_nasa.init, module=mm_reach, name=name)

# Use default clean
clean = mm_nasa.clean


def preprocess(self):
    """Update acknowledgement with info from file."""

    self.acknowledgements = self.meta.header.Acknowledgement

    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
datestr = '{year:04d}{month:02d}{day:02d}'
fname = 'reach-vid-{inst_id}_dosimeter-l1c_{datestr}_v{{version:01d}}.nc'
supported_tags = {iid: {'': fname.format(inst_id=iid, datestr=datestr)}
                  for iid in inst_ids.keys()}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)


def load(fnames, tag=None, inst_id=None):
    """Load REACH data into `pandas.DataFrame` and `pysat.Meta` objects.

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

    # Use standard netcdf interface
    labels = {'units': ('UNITS', str), 'name': ('LONG_NAME', str),
              'notes': ('VAR_NOTES', str), 'desc': ('CATDESC', str),
              'min_val': ('VALIDMIN', (int, float)),
              'max_val': ('VALIDMAX', (int, float)),
              'fill_val': ('_FillValue', (int, float))}
    data, meta = load_netcdf(fnames, epoch_name='Epoch',
                             meta_kwargs={'labels': labels})

    return data, meta


# Support download routine
download_tags = {iid: {'': 'REACH-VID-{iid}_DOSIMETER-L1C'.format(iid=iid)}
                 for iid in inst_ids.keys()}
download = functools.partial(cdw.cdas_download, supported_tags=download_tags)

# Support listing files currently on CDAWeb
list_remote_files = functools.partial(cdw.cdas_list_remote_files,
                                      supported_tags=download_tags)
