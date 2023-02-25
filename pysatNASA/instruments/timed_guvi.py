# -*- coding: utf-8 -*-
"""Module for the TIMED GUVI instrument.

Supports the Global UltraViolet Imager (GUVI) instrument on the Thermosphere
Ionosphere Mesosphere Energetics Dynamics (TIMED) satellite.

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
inst_id
    None supported


Warnings
--------
- Currently no cleaning routine.


"""

import datetime as dt
import functools

from pysat.instruments.methods import general as mm_gen

from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import jhuapl
from pysatNASA.instruments.methods import general as mm_nasa
from pysatNASA.instruments.methods import timed as mm_timed

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'timed'
name = 'guvi'
tags = {'edr-aur': ''.join(['Auroral disk imaging mode'])}
inst_ids = {'': list(tags.keys())}

pandas_format = False
multi_file_day = True

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {inst_id: {tag: dt.datetime(2003, 1, 1) for tag in tags.keys()}
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
fname = ''.join(['TIMED_GUVI_L2B-{tag:s}-IMG_{{year:04d}}{{day:03d}}',
                 '{{hour:02d}}{{minute:02d}}{{second:02d}}-?????????????_REV',
                 '??????_Av{{version:2d}}-??r{{cycle:03d}}.nc'])
supported_tags = {inst_id: {tag: fname.format(tag=tag) for tag in tags.keys()}
                  for inst_id in inst_ids.keys()}
list_files = functools.partial(mm_gen.list_files, supported_tags=supported_tags)

# Set the load routine
load = functools.partial(jhuapl.load_edr_aurora, pandas_format=pandas_format)

# Set the download routine
basic_tag = {'remote_dir': ''.join(('/data/timed/guvi/levels_v13/level2b/',
                                    'imaging/{tag:s}/{{year:4d}}/',
                                    '{{day:03d}}/')),
             'fname': fname}
download_tags = {
    sat_id: {tag: {btag: basic_tag[btag].format(tag=tag, inst_id=sat_id)
                   for btag in basic_tag.keys()} for tag in tags.keys()}
    for sat_id in inst_ids.keys()}
download = functools.partial(cdw.download, supported_tags=download_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.list_remote_files,
                                      supported_tags=download_tags)
