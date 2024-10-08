#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3986131
#
# DISTRIBUTION STATEMENT A: Approved for public release. Distribution is
# unlimited.
# ----------------------------------------------------------------------------
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


fpi = pysat.Instrument(inst_module=instruments.de2_fpi)
lang = pysat.Instrument(inst_module=instruments.de2_lang)
nacs = pysat.Instrument(inst_module=instruments.de2_nacs)
rpa = pysat.Instrument(inst_module=instruments.de2_rpa)
wats = pysat.Instrument(inst_module=instruments.de2_wats)
vefi = pysat.Instrument(inst_module=instruments.de2_vefi)

instruments = [fpi, lang, nacs, rpa, wats, vefi]
