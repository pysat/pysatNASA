# -*- coding: utf-8 -*-
"""Collection of instruments for the pysatNASA library.

Each instrument is contained within a subpackage of this set.

"""
from pysatNASA.instruments import methods  # noqa F401

__all__ = ['ace_epam_l2', 'ace_mag_l2', 'ace_sis_l2', 'ace_swepam_l2',
           'cnofs_ivm', 'cnofs_plp', 'cnofs_vefi',
           'de2_lang', 'de2_nacs', 'de2_rpa', 'de2_wats', 'de2_vefi',
           'dmsp_ssusi', 'formosat1_ivm',
           'icon_euv', 'icon_fuv', 'icon_ivm', 'icon_mighti',
           'iss_fpmu', 'jpl_gps', 'omni_hro', 'ses14_gold',
           'timed_guvi', 'timed_saber', 'timed_see']

for inst in __all__:
    exec("from pysatNASA.instruments import {x}".format(x=inst))

# Remove dummy variable
del inst
