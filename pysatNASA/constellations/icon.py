"""Creates a constellation from NASA the ICON satellite platform.

Includes the core instruments without the line of sight winds.

Note that IVM A and B are nominally never active at the same time. This
constellation requires a bug-fix in pysat 3.1.0.

"""

import pysat

from pysatNASA.instruments import icon_euv
from pysatNASA.instruments import icon_fuv
from pysatNASA.instruments import icon_ivm
from pysatNASA.instruments import icon_mighti

instruments = list()

for inst_mod in [icon_ivm, icon_euv, icon_fuv, icon_mighti]:
    for inst_id in inst_mod.inst_ids.keys():
        for tag in inst_mod.inst_ids[inst_id]:
            # Skip over line of sight winds
            if tag.find('los') == -1:
                instruments.append(pysat.Instrument(inst_module=inst_mod,
                                                    tag=tag, inst_id=inst_id))
