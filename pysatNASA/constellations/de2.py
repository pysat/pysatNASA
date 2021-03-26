import pysat

from pysatNASA import instruments
"""
Creates a constellation from the NASA DE2 satellite platform
"""


lang = pysat.Instrument(inst_module=instruments.de2_lang)
nacs = pysat.Instrument(inst_module=instruments.de2_nacs)
rpa = pysat.Instrument(inst_module=instruments.de2_rpa)
wats = pysat.Instrument(inst_module=instruments.de2_wats)

instruments = [lang, nacs, rpa, wats]
