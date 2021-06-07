# -*- coding: utf-8 -*-
"""Provides non-instrument specific routines for ICON data"""

from pysat.instruments.methods import general as mm_gen


ackn_str = ''.join(('This is a data product from the NASA Ionospheric ',
                    'Connection Explorer mission, an Explorer launched ',
                    'at 21:59:45 EDT on October 10, 2019.\n\nGuidelines ',
                    'for the use of this product are described in the ',
                    'ICON Rules of the Road  ',
                    '(https://icon.ssl.berkeley.edu/Data).',
                    '\n\nResponsibility for the mission science ',
                    'falls to the Principal Investigator, Dr. ',
                    'Thomas Immel at UC Berkeley:\nImmel, T.J., ',
                    'England, S.L., Mende, S.B. et al. Space Sci Rev ',
                    '(2018) 214: 13. ',
                    'https://doi.org/10.1007/s11214-017-0449-2\n\n',
                    'Responsibility for the validation of the L1 data ',
                    'products falls to the instrument lead investigators/',
                    'scientists.\n* EUV: Dr. Eric Korpela :  https://',
                    'doi.org/10.1007/s11214-017-0384-2\n * FUV: Dr. Harald ',
                    'Frey : https://doi.org/10.1007/s11214-017-0386-0\n* ',
                    'MIGHTI: Dr. Christoph Englert : https://doi.org/10.10',
                    '07/s11214-017-0358-4, and https://doi.org/10.1007/s11',
                    '214-017-0374-4\n* IVM: Dr. Roderick Heelis : ',
                    'https://doi.org/10.1007/s11214-017-0383-3\n\n ',
                    'Responsibility for the validation of the L2 data ',
                    'products falls to those scientists responsible for ',
                    'those products.\n * Daytime O and N2 profiles: Dr. ',
                    'Andrew Stephan : ',
                    'https://doi.org/10.1007/s11214-018-0477-6\n* Daytime ',
                    '(EUV) O+ profiles: Dr. Andrew Stephan : ',
                    'https://doi.org/10.1007/s11214-017-0385-1\n* ',
                    'Nighttime (FUV) O+ profiles: Dr. Farzad Kamalabadi : ',
                    'https://doi.org/10.1007/s11214-018-0502-9\n* Neutral',
                    ' Wind profiles: Dr. Jonathan Makela :',
                    ' https://doi.org/10.1007/s11214-017-0359-3\n* ',
                    'Neutral Temperature profiles: Dr. Christoph Englert ',
                    ': https://doi.org/10.1007/s11214-017-0434-9\n* Ion ',
                    'Velocity Measurements : Dr. Russell Stoneback : ',
                    'https://doi.org/10.1007/s11214-017-0383-3\n\n',
                    'Responsibility for Level 4 products falls to those ',
                    'scientists responsible for those products.\n*',
                    ' Hough Modes : Dr. Chihoko Yamashita :  ',
                    'https://doi.org/10.1007/s11214-017-0401-5\n* TIEGCM : ',
                    'Dr. Astrid Maute : ',
                    'https://doi.org/10.1007/s11214-017-0330-3\n* ',
                    'SAMI3 : Dr. Joseph Huba : ',
                    'https://doi.org/10.1007/s11214-017-0415-z\n\n',
                    'Pre-production versions of all above papers are ',
                    'available on the ICON website.\n\nOverall validation ',
                    'of the products is overseen by the ICON Project ',
                    'Scientist, Dr. Scott England.\n\nNASA oversight for ',
                    'all products is provided by the Mission Scientist, ',
                    'Dr. Jeffrey Klenzing.\n\nUsers of these data should ',
                    'contact and acknowledge the Principal Investigator ',
                    'Dr. Immel and the party directly responsible for the ',
                    'data product (noted above) and acknowledge NASA ',
                    'funding for the collection of the data used in the ',
                    'research with the following statement : "ICON is ',
                    'supported by NASA’s Explorers Program through ',
                    'contracts NNG12FA45C and NNG12FA42I".\n\nThese data ',
                    'are openly available as described in the ICON Data ',
                    'Management Plan available on the ICON website ',
                    '(https://icon.ssl.berkeley.edu/Data).'))

refs = {'euv': ' '.join(('Stephan, A.W., Meier, R.R., England, S.L. et al.',
                         'Daytime O/N2 Retrieval Algorithm for the Ionospheric',
                         'Connection Explorer (ICON). Space Sci Rev 214, 42',
                         '(2018). https://doi.org/10.1007/s11214-018-0477-6\n',
                         'Stephan, A.W., Korpela, E.J., Sirk, M.M. et al.',
                         'Daytime Ionosphere Retrieval Algorithm for the',
                         'Ionospheric Connection Explorer (ICON). Space Sci',
                         'Rev 212, 645–654 (2017).',
                         'https://doi.org/10.1007/s11214-017-0385-1')),
        'fuv': ' '.join(('Kamalabadi, F., Qin, J., Harding, B.J. et al.',
                         'Inferring Nighttime Ionospheric Parameters with the',
                         'Far Ultraviolet Imager Onboard the Ionospheric',
                         'Connection Explorer. Space Sci Rev 214, 70 (2018).',
                         'https://doi.org/10.1007/s11214-018-0502-9')),
        'ivm': ' '.join(('Heelis, R.A., Stoneback, R.A., Perdue, M.D. et al.',
                         'Ion Velocity Measurements for the Ionospheric',
                         'Connections Explorer. Space Sci Rev 212, 615–629',
                         '(2017). https://doi.org/10.1007/s11214-017-0383-3')),
        'mighti': ' '.join(('Harding, B.J., Makela, J.J., Englert, C.R. et al.',
                            'The MIGHTI Wind Retrieval Algorithm: Description',
                            'and Verification. Space Sci Rev 212, 585–600',
                            '(2017).',
                            'https://doi.org/10.1007/s11214-017-0359-3\n',
                            'Stevens, M.H., Englert, C.R., Harlander, J.M. et',
                            'al. Retrieval of Lower Thermospheric Temperatures',
                            'from O2 A Band Emission: The MIGHTI Experiment on',
                            'ICON. Space Sci Rev 214, 4 (2018).',
                            'https://doi.org/10.1007/s11214-017-0434-9')),
        'mission': ' '.join(('Immel, T.J., England, S.L., Mende, S.B. et al.',
                             'The Ionospheric Connection Explorer Mission:',
                             'Mission Goals and Design. Space Sci Rev 214, 13',
                             '(2018).',
                             'https://doi.org/10.1007/s11214-017-0449-2\n'))}


def remove_preamble(inst):
    """Removes preambles in variable names

    Parameters
    -----------
    inst : pysat.Instrument
        ICON FUV or MIGHTI Instrument class object

    """
    id_str = inst.inst_id.upper()

    target = {'los_wind_green': 'ICON_L21_',
              'los_wind_red': 'ICON_L21_',
              'vector_wind_green': 'ICON_L22_',
              'vector_wind_red': 'ICON_L22_',
              'temperature': ['ICON_L1_MIGHTI_{id:s}_'.format(id=id_str),
                              'ICON_L23_MIGHTI_{id:s}_'.format(id=id_str),
                              'ICON_L23_'],
              'day': 'ICON_L24_',
              'night': 'ICON_L25_'}
    mm_gen.remove_leading_text(inst, target=target[inst.tag])

    return
