#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3986131
#
# DISTRIBUTION STATEMENT A: Approved for public release. Distribution is
# unlimited.
# ----------------------------------------------------------------------------
"""Provides non-instrument specific routines for IGS GPS data."""

ackn_str = ' '.join(("The GPS Total Electron Content (TEC) data",
                     "produced by the International Global Navigation",
                     "Satellite Systems Service (IGS) Ionosphere Working",
                     "Group is provided through CDAWeb"))

refs = {'mission': ' '.join(('Feltens J, Schaer S (1998) IGS Products for the',
                             'Ionosphere, IGS Position Paper. In:',
                             'Proceedings of the IGS analysis centers',
                             'workshop, ESOC, Darmstadt, Germany,',
                             'pp 225–232, 9–11 February')),
        'gps': {'tec': ' '.join(('M. Hernández-Pajares, J.M. Juan, J. Sanz, R.',
                                 'Orus, A. Garcia-Rigo, J. Feltens, A.',
                                 'Komjathy, S.C. Schaer, and A. Krankowski,',
                                 'The IGS VTEC maps: a reliable source of',
                                 'ionospheric information since 1998, Journal',
                                 'of Geodesy (2009) 83:263–275',
                                 'doi:10.1007/s00190-008-0266-1.\n',
                                 'Feltens, J., M. Angling, N. Jackson‐Booth,',
                                 'N. Jakowski, M. Hoque, M. Hernández‐Pajares,',
                                 'A. Aragón‐Àngel, R. Orús, and R. Zandbergen',
                                 '(2011), Comparative testing of four',
                                 'ionospheric models driven with GPS',
                                 'measurements, Radio Sci., 46, RS0D12,',
                                 'doi:10.1029/2010RS004584.\n',
                                 'Peng Chen, Hang Liu, Yongchao Ma, Naiquan',
                                 'Zheng, Accuracy and consistency of different',
                                 'global ionospheric maps released by IGS',
                                 'ionosphere associate analysis centers,',
                                 'Advances in Space Research, Volume 65, Issue',
                                 '1, 2020, Pages 163-174,',
                                 'doi:10.1016/j.asr.2019.09.042.\n')),
                'roti': ' '.join(('Pi, X., A. J. Mannucci, U. J.',
                                  'Lindqwister, and C. M. Ho, Monitoring of',
                                  'global ionospheric irregularities using',
                                  'the worldwide GPS network, Geophys. Res.',
                                  'Lett., 24, 2283, 1997.\n',
                                  'Pi, X., F. J. Meyer, K. Chotoo, Anthony',
                                  'Freeman, R. G. Caton, and C. T. Bridgwood,',
                                  'Impact of ionospheric scintillation on',
                                  'Spaceborne SAR observations studied using',
                                  'GNSS, Proc. ION-GNSS, pp.1998-2006,',
                                  '2012.'))}}
