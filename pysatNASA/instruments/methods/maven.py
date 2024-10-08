#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3986131
#
# DISTRIBUTION STATEMENT A: Approved for public release. Distribution is
# unlimited.
# ----------------------------------------------------------------------------
"""Provides non-instrument specific routines for MAVEN data."""

ackn_str = ''.join(('Jakosky, B.M., Lin, R.P., Grebowsky, J.M. et al.',
                    ' The Mars Atmosphere and Volatile Evolution',
                    '(MAVEN) Mission. Space Sci Rev 195, 3–48 (2015).',
                    ' https://doi.org/10.1007/s11214-015-0139-x'))
refs = {'mission': ''.join(('Jakosky, B.M., Lin, R.P., Grebowsky, J.M. et',
                            ' al. The Mars Atmosphere and Volatile Evolution',
                            '(MAVEN) Mission. Space Sci Rev',
                            ' 195, 3–48 (2015).',
                            ' https://doi.org/10.1007/s11214-015-0139-x')),
        'insitu_kp': '',
        'mag': ''.join(('Connerney, J., and P. Lawton, MAVEN MAG',
                        ' PDS Archive SIS - This document ',
                        'describes the format and content of the MAVEN',
                        ' Magnetometer (MAG) Planetary Data System ',
                        '(PDS) data archive. ',
                        'It includes descriptions of the Standard',
                        'Data Products and associated metadata, ',
                        'and the volume archive format,',
                        'content, and generation pipeline. ',
                        'Connerney, J.E.P.; Espley, J.; Lawton, P.;',
                        ' Murphy, S.; Odom, J.; Oliversen, R.;',
                        'and Sheppard, D., The MAVEN Magnetic Field',
                        ' Investigation, Space Sci Rev,',
                        'Vol 195, Iss 1-4, pp.257-291, 2015. ',
                        'doi:10.1007/s11214-015-0169-4')),
        'sep': ''.join(('Larson, D.E., Lillis, R.J., Lee, C.O. et al.',
                        'The MAVEN Solar Energetic Particle Investigation.',
                        ' Space Sci Rev 195, 153–172 (2015).',
                        ' https://doi.org/10.1007/s11214-015-0218-z'))}
