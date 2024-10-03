#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3986131
#
# DISTRIBUTION STATEMENT A: Approved for public release. Distribution is
# unlimited.
# ----------------------------------------------------------------------------
"""Provides non-instrument specific routines for JPL ROTI data.

.. deprecated:: 0.0.5
    This module is now included in `methods.igs`.
    This instrument will be removed in 0.1.0+ to reduce redundancy.

"""

ackn_str = ' '.join(("The GPS Total Electron Content (TEC) data",
                     "produced by the International Global Navigation",
                     "Satellite Systems Service (IGS) Ionosphere Working",
                     "Group is provided through CDAWeb"))

refs = {'mission': ' '.join(('Feltens J, Schaer S (1998) IGS Products for the',
                             'Ionosphere, IGS Position Paper. In:',
                             'Proceedings of the IGS analysis centers',
                             'workshop, ESOC, Darmstadt, Germany,',
                             'pp 225–232, 9–11 February')),
        'roti15min_jpl': ' '.join(('Pi, X., A. J. Mannucci, U. J.',
                                   'Lindqwister, and C. M. Ho, Monitoring of',
                                   'global ionospheric irregularities using',
                                   'the worldwide GPS network, Geophys. Res.',
                                   'Lett., 24, 2283, 1997.\n',
                                   'Pi, X., F. J. Meyer, K. Chotoo, Anthony',
                                   'Freeman, R. G. Caton, and C. T. Bridgwood,',
                                   'Impact of ionospheric scintillation on',
                                   'Spaceborne SAR observations studied using',
                                   'GNSS, Proc. ION-GNSS, pp.1998-2006,',
                                   '2012.'))}
