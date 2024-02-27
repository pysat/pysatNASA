# -*- coding: utf-8 -*-
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

# ----------------------------------------------------------------------------
# Instrument methods


# Use standard init routine
init = functools.partial(mm_nasa.init, module=mm_dmsp, name=name)

# No cleaning, use standard warning function instead
clean = mm_nasa.clean_warn

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
def load():
    """FIX THIS HERE"""
    out = jhuapl.load_edr_aurora(pandas_format=pandas_format,
                                 strict_dim_check=False)

    return out
