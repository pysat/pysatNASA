#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3986131
#
# DISTRIBUTION STATEMENT A: Approved for public release. Distribution is
# unlimited.
# ----------------------------------------------------------------------------
"""Module for the DE2 VEFI instrument.

.. deprecated:: 0.0.6
    The '' tag is deprecated. This data set is replaced by the de2_vefimagb
    instrument. The '' tag will be removed in 0.1.0+ to reduce redundancy.

From CDAWeb (adpated):
This directory gathers data for the VEFI instrument that flew on the DE 2
spacecraft which was launched on 3 August 1981 into an elliptical orbit with
an altitude range of 300 km to 1000 km and re-entered the atmosphere on
19 February 1983.

dca   (NSSDC ID: 81-070B-02C)

This data set contains the averaged (2 samples per second) DC electric fields in
spacecraft coordinates and orbit information in ASCII format.

ac   (NSSDC ID: 81-070B-02E)

This data set contains the averaged AC electric field data (1 or 2 points per
second) and orbit information.

References
----------
Maynard, N. C., E. A. Bielecki, H. G. Burdick, Instrumentation for vector
electric field measurements from DE-B, Space Sci. Instrum., 5, 523, 1981.

Properties
----------
platform
    'de2'
name
    'vefi'
tag
    '', 'dca', 'ac'
inst_id
    none supported


Warnings
--------
- Currently no cleaning routine.


"""

import datetime as dt
import functools
import warnings

import pysat
from pysat.instruments.methods import general as mm_gen
from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import de2 as mm_de2
from pysatNASA.instruments.methods import general as mm_nasa

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'de2'
name = 'vefi'
tags = {'': '62 ms combination of Electric Field and Magnetometer',
        'dca': '500 ms cadence DC Averaged Electric Field data',
        'ac': '500 ms cadence AC Electric Field data'}
inst_ids = {'': [tag for tag in tags.keys()]}

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {tag: dt.datetime(1983, 1, 1) for tag in tags.keys()}}


# ----------------------------------------------------------------------------
# Instrument methods

def init(self):
    """Initialize the Instrument object with instrument specific values."""

    if self.tag == '':
        warnings.warn(" ".join(["The '' tag for `de2_vefi` has been",
                                "deprecated and will be removed in 0.1.0+."]),
                      DeprecationWarning, stacklevel=2)

    mm_nasa.init(self, module=mm_de2, name=self.name)

    return


# Use default clean
clean = mm_nasa.clean

# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
datestr = '{year:04d}{month:02d}{day:02d}_v{version:02d}'
fid = {'': '62ms_vefimagb',
       'ac': 'ac500ms_vefi',
       'dca': 'dca500ms_vefi'}
fname = 'de2_{fid:s}_{datestr:s}.cdf'
supported_tags = {'': {tag: fname.format(fid=fid[tag], datestr=datestr)
                       for tag in tags.keys()}}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)


# Set the load routine
def load(fnames, tag='', inst_id='', **kwargs):
    """Load DE2 VEFI data.

    This routine is called as needed by pysat. It is not intended
    for direct user interaction.

    Parameters
    ----------
    fnames : array-like
        Iterable of filename strings, full path, to data files to be loaded.
        This input is nominally provided by pysat itself.
    tag : str
        Tag name used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default='')
    inst_id : str
        Instrument ID used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default='')

    Returns
    -------
    data : pds.DataFrame
        A pandas DataFrame with data prepared for the `pysat.Instrument`.
    meta : pysat.Meta
        Metadata formatted for a pysat.Instrument object.

    Note
    ----
    Several variables relating to time stored in different formats are dropped.
    These are redundant and complicate the load procedure.

    """

    if tag == '':
        # Warn user that e-field data is dropped.
        estr = 'E-field data dropped'
        pysat.logger.warning(estr)

        # Drop E-field data
        if 'use_cdflib' in kwargs.keys():
            kwargs.pop('use_cdflib')
        data, meta = cdw.load_xarray(fnames, tag=tag, inst_id=inst_id,
                                     epoch_name='mtimeEpoch',
                                     drop_dims='vtimeEpoch', **kwargs)
        if hasattr(data, 'to_pandas'):
            data = data.to_pandas()
        else:
            # xarray 0.16 support required for operational server
            data = data.to_dataframe()
    else:
        data, meta = cdw.load_pandas(fnames, tag=tag, inst_id=inst_id, **kwargs)

    return data, meta


# Set the download routine
download_tags = {'': {'': 'DE2_62MS_VEFIMAGB',
                      'ac': 'DE2_AC500MS_VEFI',
                      'dca': 'DE2_DCA500MS_VEFI'}}
download = functools.partial(cdw.cdas_download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.cdas_list_remote_files,
                                      supported_tags=download_tags)
