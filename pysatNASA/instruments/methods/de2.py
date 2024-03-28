#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3986131
#
# DISTRIBUTION STATEMENT A: Approved for public release. Distribution is
# unlimited.
# ----------------------------------------------------------------------------
# -*- coding: utf-8 -*-

"""Provides non-instrument specific routines for DE2 data."""

ackn_str = "The Dynamics Explorer 2 satellite data is provided through CDAWeb"

refs = {'fpi': ' '.join(('Hays, P B, Killeen, T L, and Kennedy, B C.',
                         '"Fabry-Perot interferometer on Dynamics Explorer".',
                         'Space Sci. Instrum., v. 5, p. 395-416, 1981.')),
        'lang': ' '.join(('J. P. Krehbiel, L. H. Brace, R. F. Theis, W. H.',
                          'Pinkus, and R. B. Kaplan, The Dynamics Explorer 2',
                          'Langmuir Probe (LANG), Space Sci. Instrum., v. 5,',
                          'n. 4, p. 493, 1981.')),
        'nacs': ' '.join(('G. R. Carrignan, B. P. Block, J. C. Maurer,  A. E.',
                          'Hedin, C. A. Reber, N. W. Spencer, The neutral mass',
                          'spectrometer on Dynamics Explorer B, Space Sci.',
                          'Instrum., v. 5, n. 4, p. 429, 1981.')),
        'rpa': ' '.join(('W. B. Hanson, R. A. Heelis, R. A. Power, C. R.',
                         'Lippincott, D. R. Zuccaro, B. J. Holt, L. H. Harmon,',
                         'and S. Sanatani, The retarding potential analyzer',
                         'for dynamics explorer-B, Space Sci. Instrum. 5,',
                         '503–510 (1981).\n',
                         'Heelis, R. A., W. B. Hanson, C. R. Lippincott, D. R.',
                         'Zuccaro, L. L. Harmon, B. J. Holt, J. E. Doherty, R.',
                         'A. Power, The ion drift meter for Dynamics',
                         'Explorer-B, Space Sci. Instrum., 5, 511, 1981.')),
        'wats': ' '.join(('N. W. Spencer, L. E. Wharton, H. B. Niemann, A. E.',
                          'Hedin, G. R. Carrignan, J. C. Maurer, The',
                          'Dynamics Explorer Wind and Temperature Spectrometer',
                          'Space Sci. Instrum., v. 5, n. 4, p. 417, 1981.')),
        'vefi': ' '.join(('Maynard, N. C., E. A. Bielecki, H. G. Burdick,',
                          'Instrumentation for vector electric field',
                          'measurements from DE-B, Space Sci. Instrum., 5,',
                          '523, 1981.'))
        }
