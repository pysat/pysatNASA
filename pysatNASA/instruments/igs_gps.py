# -*- coding: utf-8 -*-
"""Module for the IGS GPS data products.

Supports GPS data produced from International GNSS Service Total Electron
Content (TEC).

From CDAWeb (modified):

This directory contains the GPS Total Electron Content (TEC) data produced by
the International Global Navigation Satellite Systems Service (IGS) Ionosphere
Working Group and by the Analysis Centers that have contributed to the IGS data
including CODE of the University of Bern (Switzerland), ESA of the European
Space Operations Center (ESOC) in Darmstadt (Germany), JPL of the Jet Propulsion
Laboratory, Pasadena (USA), and UPC of the University Politechnical Catalonia in
Barcelona (Spain). The IGS data are a computed as a weighted mean of the data
from the four analysis centers.

Properties
----------
platform
    'igs'
name
    'gps'
tag
    ['15min', '1hr', '2hr']
inst_id
    None supported


Warnings
--------
- The cleaning parameters for the instrument are still under development.


References
----------
M. Hernández-Pajares, J.M. Juan, J. Sanz, R. Orus, A. Garcia-Rigo, J. Feltens,
A. Komjathy, S.C. Schaer, and A. Krankowski, The IGS VTEC maps: a reliable
source of ionospheric information since 1998Journal of Geodesy (2009) 83:263–275
doi:10.1007/s00190-008-0266-1

Feltens, J., M. Angling, N. Jackson‐Booth, N. Jakowski, M. Hoque, M.
Hernández‐Pajares, A. Aragón‐Àngel, R. Orús, and R. Zandbergen (2011),
Comparative testing of four ionospheric models driven with GPS measurements,
Radio Sci., 46, RS0D12,	doi:10.1029/2010RS004584

Peng Chen, Hang Liu, Yongchao Ma, Naiquan Zheng, Accuracy and consistency of
different global ionospheric maps released by IGS ionosphere associate analysis
centers, Advances in Space Research, Volume 65, Issue 1, 2020, Pages 163-174,
doi:10.1016/j.asr.2019.09.042.

"""

import datetime as dt
import functools

from pysat.instruments.methods import general as mm_gen

from pysatNASA.instruments.methods import cdaweb as cdw
from pysatNASA.instruments.methods import general as mm_nasa
from pysatNASA.instruments.methods import igs as mm_igs

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'igs'
name = 'gps'
tags = {'tec': 'Total Electron Content',
        'roti': 'Rate of Change in TEC'}
# tags = {'15min': '15 min cadence TEC',
#         '1hr': '1 hour cadence TEC',
#         '2hr': '2 hour cadence TEC'}
inst_ids = {'15min': ['tec', 'roti'],
            '1hr': ['tec'],
            '2hr': ['tec']}
pandas_format = False
# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {jj: {kk: dt.datetime(2013, 1, 1) for kk in inst_ids[jj]}
               for jj in inst_ids.keys()}
# ----------------------------------------------------------------------------
# Instrument methods


# Use standard init routine
init = functools.partial(mm_nasa.init, module=mm_igs, name=name)


# No cleaning, use standard warning function instead
clean = mm_nasa.clean_warn

# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default CDAWeb and pysat methods

# Set the list_files routine
cdas_labels = {'15min': {'tec': 'GPS_TEC15MIN_IGS',
                         'roti': 'GPS_ROTI15MIN_JPL'},
               '1hr': {'tec': 'GPS_TEC1HR_IGS'},
               '2hr': {'tec': 'GPS_TEC2HR_IGS'}}

date_ver = '{year:4d}{month:02d}{day:02d}_v{version:02d}'
fname = '{cdas:s}_{date_ver:s}.cdf'

supported_tags = {id: {tag: fname.format(cdas=cdas_labels[id][tag].lower(),
                                         date_ver=date_ver)
                       for tag in inst_ids[id]} for id in inst_ids.keys()}
list_files = functools.partial(mm_gen.list_files,
                               supported_tags=supported_tags)

# Set the load routine
load = functools.partial(cdw.load, pandas_format=pandas_format)

# Set the download routine
download = functools.partial(cdw.cdas_download, supported_tags=cdas_labels)

# Set the list_remote_files routine
list_remote_files = functools.partial(cdw.cdas_list_remote_files,
                                      supported_tags=cdas_labels)
