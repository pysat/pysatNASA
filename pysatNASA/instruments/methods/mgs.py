# -*- coding: utf-8 -*-
"""Provides non-instrument specific routines for MGS data.

Created on Wed Feb  7 11:42:10 2024

@author: tesman
"""

ackn_str = ' '.join(('Much of the information provided in this meta data ',
                     'originates from text files provided at: ',
                     'https://pds-ppi.igpp.ucla.edu/search/?sc=Mars%20Global%',
                     '20Surveyor&i=MAG within the CATALOG folder and the ',
                     'AAREADME.txt files. The development of the netCDF files ',
                     'was supported by the NASA',
                     'Postdoctoral Program Fellowship awarded to Teresa Esman ',
                     'in 2022. The success of the MGS MAG project is',
                     'owed to, among others, the people listed here: ',
                     'https://mars.nasa.gov/mgs/people/. ',
                     'Addtional information on the MAG dataset can be found ',
                     'at: https://mgs-mager.gsfc.nasa.gov/status.html. ',
                     'Documentation on MGS MAG data on the PDS has been ',
                     'maintained by J.E.P. Connerney, Mark Sharlow, D. ',
                     'Kazden, J. Springborn, and B. Semenov, among others. ',
                     'Teresa Esman, now a NPP Fellow at NASA Goddard Space ',
                     'Flight Center, compiled MGS MAG low resolution and ',
                     'high resolution data products, translated time to ',
                     'unix time, and performed the calculation and ',
                     'interpolation (to high resolution) of the altitude',
                     'data product.'))

refs = {'mission': ''.join(('Glenn E. Cunningham, Mars global surveyor ',
                            'mission, Acta Astronautica, Volume 38, ',
                            'Issues 4–8, 1996, Pages 367-375, ISSN 0094-5765',
                            'https://doi.org/10.1016/0094-5765(96)00035-5.')),
        'PDS data': ''.join(('The NASA Planetary Data System,',
                             'doi: 	https://doi.org/10.17189/1519752')),
        'mag': ''.join(('Acuna, M. A., J. E. P. Connerney, P. Wasilewski, ',
                        'R. P. Lin, K. A. Anderson, C. W. Carlson, ',
                        'J. McFadden, D. W. Curtis, H. Reme, A. Cros, ',
                        'J. L. Medale, J. A. Sauvaud, C. d\'Uston, ',
                        'S. J. Bauer, P. Cloutier, M. Mayhew, ',
                        'and N. F. Ness, Mars Observer Magnetic Fields ',
                        'Investigation, J. Geophys. Res., 97, 7799-7814, ',
                        '1992.'))}
