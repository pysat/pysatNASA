#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3986131
#
# DISTRIBUTION STATEMENT A: Approved for public release. Distribution is
# unlimited.
# ----------------------------------------------------------------------------
"""Module for the DMSP SSUSI instrument.

Supports the Special Sensor Ultraviolet Spectrographic Imager (SSUSI)
instrument on Defense Meteorological Satellite Program (DMSP).

From JHU APL:

SSUSI was designed for the DMSP Block 5D-3 satellites. These satellites are
placed into nearly polar, sun-synchronous orbits at an altitude of about 850 km.
SSUSI is a remote-sensing instrument which measures ultraviolet (UV) emissions
in five different wavelength bands from the Earth's upper atmosphere. SSUSI is
mounted on a nadir-looking panel of the satellite. The multicolor images from
SSUSI cover the visible Earth disk from horizon to horizon and the anti-sunward
limb up to an altitude of approximately 520 km.

The UV images and the derived environmental data provide the Air Force Weather
Agency (Offutt Air Force Base, Bellevue, NE) with near real-time information
that can be utilized in a number of applications, such as maintenance of high
frequency (HF) communication links and related systems and assessment of the
environmental hazard to astronauts on the Space Station.


Properties
----------
platform
    'dmsp'
name
    'ssusi'
tag
    'edr-aurora'
    'sdr-disk'
    'sdr2-disk'
inst_id
    'f16', 'f17', 'f18', 'f19'


Warnings
--------
- Currently no cleaning routine.


References
----------
Larry J. Paxton, Daniel Morrison, Yongliang Zhang, Hyosub Kil, Brian Wolven,
Bernard S. Ogorzalek, David C. Humm, and Ching-I. Meng "Validation of remote
sensing products produced by the Special Sensor Ultraviolet Scanning Imager
(SSUSI): a far UV-imaging spectrograph on DMSP F-16", Proc. SPIE 4485, Optical
Spectroscopic Techniques, Remote Sensing, and Instrumentation for Atmospheric
and Space Research IV, (30 January 2002); doi:10.1117/12.454268

"""

import datetime as dt
import functools
import pandas as pds

import pysat
from pysat.instruments.methods import general as mm_gen

from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import dmsp as mm_dmsp
from pysatNASA.instruments.methods import general as mm_nasa
from pysatNASA.instruments.methods import jhuapl

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'dmsp'
name = 'ssusi'
tags = {'edr-aurora': ''.join(['Electron energy flux and mean energy, auroral',
                               ' boundaries, identified discrete auroral arcs,',
                               ' hemispheric power, and magnetic field lines ',
                               'traced to 4 Earth radii']),
        'sdr-disk': 'Fine resolution gridded disk radiances',
        'sdr2-disk': 'Coarse resolution gridded disk radiances'}
inst_ids = {sat_id: list(tags.keys())
            for sat_id in ['f16', 'f17', 'f18', 'f19']}

pandas_format = False
multi_file_day = True

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {inst_id: {tag: dt.datetime(2015, 1, 1) for tag in tags.keys()}
               for inst_id in inst_ids.keys()}
# TODO(#218, #222): Remove when compliant with multi-day load tests
_new_tests = {inst_id: {tag: False for tag in tags.keys()}
              for inst_id in inst_ids.keys()}
# TODO(pysat#1196): Un-comment when pysat bug is fixed and released
# _clean_warn = {inst_id: {tag: mm_nasa.clean_warnings
#                          for tag in inst_ids[inst_id]
#                          if tag not in ['sdr-disk', 'sdr2-disk']}
#                for inst_id in inst_ids.keys()}

# ----------------------------------------------------------------------------
# Instrument methods

# Use standard init routine
init = functools.partial(mm_nasa.init, module=mm_dmsp, name=name)


def clean(self):
    """Clean DMSP SSUSI imaging data.

    Note
    ----
        Supports 'clean', 'dusty', 'dirty', 'none'. Method is
        not called by pysat if clean_level is None or 'none'.

    """
    if self.tag in ["sdr-disk", "sdr2-disk"]:
        jhuapl.clean_by_dqi(self)
    else:
        # Follow the same warning format as the general clean warning, but
        # with additional information.
        pysat.logger.warning(' '.join(['No cleaning routines available for',
                                       self.platform, self.name, self.tag,
                                       self.inst_id, 'at clean level',
                                       self.clean_level]))
    return


def concat_data(self, new_data, combine_times=False, **kwargs):
    """Concatenate data to self.data for DMSP SSUSI data.

    Parameters
    ----------
    new_data : xarray.Dataset or list of such objects
        New data objects to be concatenated
    combine_times : bool
        For SDR data, optionally combine the different datetime coordinates
        into a single time coordinate (default=False)
    **kwargs : dict
        Optional keyword arguments passed to xr.concat

    Note
    ----
    For xarray, `dim=Instrument.index.name` is passed along to xarray.concat
    except if the user includes a value for dim as a keyword argument.

    """
    # Establish the time dimensions by data type
    time_dims = [self.index.name]

    if self.tag in ['sdr-disk', 'sdr2-dist']:
        time_dims.append('time_auroral')

    # Concatenate using the appropriate method for the number of time
    # dimensions
    jhuapl.concat_data(self, time_dims, new_data, combine_times=combine_times,
                       **kwargs)
    return


# ----------------------------------------------------------------------------
# Instrument functions
remote_dir = ''.join(('/pub/data/dmsp/dmsp{inst_id:s}/ssusi/',
                      '/data/{tag:s}/{{year:4d}}/{{day:03d}}/'))


# Set the list_files routine
def list_files(tag='', inst_id='', data_path='', **kwargs):
    """Return a Pandas Series of every file for DMSP SSUSI data.

    Parameters
    ----------
    tag : str
        Tag name used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default='')
    inst_id : str
        Instrument ID used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default='')
    data_path : str
        Path to data directory. This input is nominally provided by pysat
        itself. (default='')
    **kwargs : dict
        Dict of kwargs allowed by `pysat.instruments.general.list_files`

    Returns
    -------
    out : pds.Series
        A Series containing the verified available files

    See Also
    --------
    pysat.Files.from_os, pysat.instruments.general.list_files

    """
    # There are two potential file formats for DMSP SSUSI data, check both
    file_fmts = mm_dmsp.ssusi_fname(
        [mm_dmsp.fmt_swap_time - dt.timedelta(days=1), mm_dmsp.fmt_swap_time],
        tag=tag, inst_id=inst_id)

    out_list = list()
    for file_fmt in file_fmts:
        supported_tags = {inst_id: {tag: file_fmt}}
        out_list.append(mm_gen.list_files(tag=tag, inst_id=inst_id,
                                          data_path=data_path,
                                          supported_tags=supported_tags,
                                          **kwargs))

    # Combine the outputs
    out = pds.concat(out_list)
    return out


# Set the download routine
def download(date_array, tag='', inst_id='', data_path=None):
    """Download DMSP SSUSI data.

    Parameters
    ----------
    date_array : array-like
        Array of datetimes to download data for. Provided by pysat.
    tag : str
        Data product tag (default='')
    inst_id : str
        Instrument ID (default='')
    data_path : str or NoneType
        Path to data directory.  If None is specified, the value previously
        set in Instrument.files.data_path is used.  (default=None)

    """
    # Initalize the supported tags kwarg
    supported_tags = {inst_id: {tag: {'remote_dir': remote_dir.format(
        tag=tag, inst_id=inst_id)}}}

    # Determine the filename format for the desired period of time
    file_fmts = mm_dmsp.ssusi_fname([date_array[0], date_array[-1]], tag,
                                    inst_id)

    # Proceed differently if there are one or two potential file formats
    supported_tags[inst_id][tag]['fname'] = file_fmts[0]
    if file_fmts[0] == file_fmts[1]:
        cdw.download(date_array, data_path, tag=tag, inst_id=inst_id,
                     supported_tags=supported_tags)
    else:
        # Get a mask for the time array
        swap_mask = date_array < mm_dmsp.fmt_swap_time

        # Download the first set of data
        cdw.download(date_array[swap_mask], data_path, tag=tag, inst_id=inst_id,
                     supported_tags=supported_tags)

        # Download the second set of data
        supported_tags[inst_id][tag]['fname'] = file_fmts[1]
        cdw.download(date_array[~swap_mask], data_path, tag=tag,
                     inst_id=inst_id, supported_tags=supported_tags)
    return


# Set the list_remote_files routine
def list_remote_files(tag='', inst_id='', start=None, stop=None):
    """List every file for remote DMSP SSUSI data.

    Parameters
    ----------
    tag : str
        Data product tag (default='')
    inst_id : str
        Instrument ID (default='')
    start : dt.datetime or NoneType
        Starting time for file list. A None value will start with the first
        file found. (default=None)
    stop : dt.datetime or NoneType
        Ending time for the file list.  A None value will stop with the last
        file found. (default=None)

    Returns
    -------
    file_list : pds.Series
        A Series containing the verified available files

    """
    # Initalize the supported tags kwarg
    supported_tags = {inst_id: {tag: {'remote_dir': remote_dir.format(
        tag=tag, inst_id=inst_id)}}}

    # Determine the filename format for the desired period of time
    start_time = dt.datetime(1900, 1, 1) if start is None else start
    stop_time = dt.datetime.now(tz=dt.timezone.utc) if stop is None else stop
    file_fmts = mm_dmsp.ssusi_fname([start_time, stop_time], tag, inst_id)

    # Proceed differently if there are one or two potential file formats
    supported_tags[inst_id][tag]['fname'] = file_fmts[0]
    if file_fmts[0] == file_fmts[1]:
        file_list = cdw.list_remote_files(tag=tag, inst_id=inst_id, start=start,
                                          stop=stop,
                                          supported_tags=supported_tags)
    else:
        # Get the first set of files
        file_list_start = cdw.list_remote_files(tag=tag, inst_id=inst_id,
                                                start=start,
                                                stop=mm_dmsp.fmt_swap_time,
                                                supported_tags=supported_tags)

        # Get the second set of files
        supported_tags[inst_id][tag]['fname'] = file_fmts[1]
        file_list_stop = cdw.list_remote_files(tag=tag, inst_id=inst_id,
                                               start=mm_dmsp.fmt_swap_time,
                                               stop=stop,
                                               supported_tags=supported_tags)

        # Join the two file lists
        file_list = pds.concat([file_list_start, file_list_stop])

    return file_list


# Set the load routine
def load(fnames, tag='', inst_id='', combine_times=False):
    """Load DMSP SSUSI data into `xarray.DataSet` and `pysat.Meta` objects.

    This routine is called as needed by pysat. It is not intended
    for direct user interaction.

    Parameters
    ----------
    fnames : array-like
        Iterable of filename strings, full path, to data files to be loaded.
        This input is nominally provided by pysat itself.
    tag : str
        Tag name used to identify particular data set to be loaded.
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

        inst = pysat.Instrument('dmsp', 'ssusi', tag='sdr-disk', inst_id='f16')
        inst.load(2015, 1)

    """
    if tag == 'edr-aurora':
        data, meta = jhuapl.load_edr_aurora(fnames, tag, inst_id,
                                            pandas_format=pandas_format,
                                            strict_dim_check=False)
    elif tag.find('disk') > 0:
        data, meta = jhuapl.load_sdr_aurora(fnames, name, tag, inst_id,
                                            pandas_format=pandas_format,
                                            strict_dim_check=False,
                                            combine_times=combine_times)

    return data, meta
