__all__ = ['cnofs_ivm', 'cnofs_plp', 'cnofs_vefi',
           'de2_lang', 'de2_nacs', 'de2_rpa', 'de2_wats',
           'icon_euv', 'icon_fuv', 'icon_ivm', 'icon_mighti',
           'iss_fpmu', 'omni_hro', 'formosat1_ivm', 'sport_ivm',
           'timed_saber', 'timed_see']

for inst in __all__:
    exec("from pysatNASA.instruments import {x}".format(x=inst))
