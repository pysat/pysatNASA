"""Creates a constellation from the NASA DE2 satellite platform.

Includes the core supported instruments.


Examples
--------
::

    import pysat
    import pysatNASA

    de2 = pysat.Constellation(const_module=pysatNASA.constellations.de2)

    de2.load(1983, 1)


"""

import pysat

from pysatNASA import instruments


lang = pysat.Instrument(inst_module=instruments.de2_lang)
nacs = pysat.Instrument(inst_module=instruments.de2_nacs)
rpa = pysat.Instrument(inst_module=instruments.de2_rpa)
wats = pysat.Instrument(inst_module=instruments.de2_wats)

instruments = [lang, nacs, rpa, wats]
