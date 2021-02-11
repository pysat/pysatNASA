"""
Creates a constellation from NASA the ICON satellite platform
"""

import pysat

from pysatNASA.instruments import icon_ivm, icon_euv, icon_fuv, icon_mighti

instruments = list()

for inst_mod in [icon_ivm, icon_euv, icon_fuv, icon_mighti]:
    for inst_id in inst_mod.inst_ids.keys():
        for tag in inst_mod.inst_ids[inst_id]:
            instruments.append(pysat.Instrument(inst_module=inst_mod, tag=tag,
                                                inst_id=inst_id))
