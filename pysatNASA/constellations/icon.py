#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3986131
#
# DISTRIBUTION STATEMENT A: Approved for public release. Distribution is
# unlimited.
# ----------------------------------------------------------------------------
"""Creates a constellation from NASA the ICON satellite platform.

Includes the core instruments without the line of sight winds.

Note that IVM A and B are nominally never active at the same time. This
constellation should be initialized with `common_index=False`.  This forgoes
the pysat check that ensures all instruments load data.

Examples
--------
::

    import pysat
    import pysatNASA

    icon = pysat.Constellation(const_module=pysatNASA.constellations.icon,
                               common_index=False)

    icon.load(2020, 1)

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
