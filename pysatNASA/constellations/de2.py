"""Creates a constellation from the NASA DE2 satellite platform."""

import pysat

from pysatNASA import instruments


fpi = pysat.Instrument(inst_module=instruments.de2_fpi)
lang = pysat.Instrument(inst_module=instruments.de2_lang)
nacs = pysat.Instrument(inst_module=instruments.de2_nacs)
rpa = pysat.Instrument(inst_module=instruments.de2_rpa)
wats = pysat.Instrument(inst_module=instruments.de2_wats)
vefi = pysat.Instrument(inst_module=instruments.de2_vefi)

instruments = [fpi, lang, nacs, rpa, wats, vefi]
