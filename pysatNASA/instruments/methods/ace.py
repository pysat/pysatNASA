# -*- coding: utf-8 -*-
"""Provides non-instrument specific routines for ACE data."""

import numpy as np


ackn_str = ' '.join(("Please acknowledge the NASA National Space Science Data",
                     "Center, the Space Physics Data Facility, and the ACE",
                     "Principal Investigator, Edward C. Stone of the",
                     "California Institute of Technology, for usage of ACE",
                     "data from this site in publications and presentations."))

refs = {'mission': ' '.join(('Stone, E., Frandsen, A., Mewaldt, R. et al.',
                             'The Advanced Composition Explorer. Space Science',
                             'Reviews 86, 1–22 (1998).',
                             'https://doi.org/10.1023/A:1005082526237')),
        'epam_l2': ' '.join(('Gold, R., Krimigis, S., Hawkins, S. et al.',
                             'Electron, Proton, and Alpha Monitor on the',
                             'Advanced Composition Explorer spacecraft.',
                             'Space Science Reviews 86, 541–562 (1998).',
                             'https://doi.org/10.1023/A:1005088115759')),
        'mag_l2': ' '.join(("Smith, C., L'Heureux, J., Ness, N. et al. The ACE",
                            "Magnetic Fields Experiment. Space Science Reviews",
                            "86, 613–632 (1998).",
                            "https://doi.org/10.1023/A:1005092216668")),
        'sis_l2': ' '.join(('Stone, E., Cohen, C., Cook, W. et al. The Solar',
                            'Isotope Spectrometer for the Advanced Composition',
                            'Explorer. Space Science Reviews 86, 357–408',
                            '(1998). https://doi.org/10.1023/A:1005027929871')),
        'swepam_l2': ' '.join(('McComas, D., Bame, S., Barker, P. et al. Solar',
                               'Wind Electron Proton Alpha Monitor (SWEPAM)',
                               'for the Advanced Composition Explorer. Space',
                               'Science Reviews 86, 563–612 (1998).',
                               'https://doi.org/10.1023/A:1005040232597'))
        }


def clean(self):
    """Clean ACE data to the specified level.

    Note
    ----
    Basic cleaning to replace fill values with NaN

    """

    for key in self.variables:
        if key != 'time':
            fill = self.meta[key, self.meta.labels.fill_val]
            # Replace fill with nan
            self[key] = self.data[key].where(key != fill)
            self.meta[key] = {self.meta.labels.fill_val: np.nan}
    return
