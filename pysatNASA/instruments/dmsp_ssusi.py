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
    """Concatonate data to self.data for DMSP SSUSI data.

    Parameters
    ----------
    new_data : xarray.Dataset or list of such objects
        New data objects to be concatonated
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

    # Concatonate using the appropriate method for the number of time
    # dimensions
    jhuapl.concat_data(self, time_dims, new_data, combine_times=combine_times,
                       **kwargs)
    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
fname = ''.join(['dmsp{inst_id:s}_ssusi_{tag:s}_{{year:04d}}{{day:03d}}T',
                 '{{hour:02d}}{{minute:02d}}{{second:02d}}-???????T??????-REV',
                 '?????_vA{{version:1d}}.?.?r{{cycle:03d}}.nc'])
supported_tags = {sat_id: {tag: fname.format(tag=tag, inst_id=sat_id)
                           for tag in tags.keys()}
                  for sat_id in inst_ids.keys()}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the download routine
basic_tag = {'remote_dir': ''.join(('/pub/data/dmsp/dmsp{inst_id:s}/ssusi/',
                                    '/data/{tag:s}/{{year:4d}}/{{day:03d}}/')),
             'fname': fname}
download_tags = {
    sat_id: {tag: {btag: basic_tag[btag].format(tag=tag, inst_id=sat_id)
                   for btag in basic_tag.keys()} for tag in tags.keys()}
    for sat_id in inst_ids.keys()}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)


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
