# -*- coding: utf-8 -*-
"""Provides non-instrument specific routines for ACE data."""

import numpy as np

from pysatNASA.instruments.methods import cdaweb as cdw

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


def load(fnames, tag='', inst_id='', to_pandas=False):
    """Load data via xarray and convert to pandas if needed.

    This routine is called as needed by pysat. It is not intended
    for direct user interaction.

    Parameters
    ----------
    fnames : array-like
        Iterable of filename strings, full path, to data files to be loaded.
        This input is nominally provided by pysat itself.
    tag : str
        Tag name used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default='')
    inst_id : str
        Instrument ID used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default='')
    to_pandas : bool
        If True, convert to pandas. If False, leave as xarray. (default=False)

    Returns
    -------
    data : pds.DataFrame or xr.Dataset
        A pandas DataFrame or xarray Dataset with data prepared for the
        `pysat.Instrument`.
    meta : pysat.Meta
        Metadata formatted for a pysat.Instrument object.

    Note
    ----
    Several variables relating to time stored in different formats are dropped.
    These are redundant and complicate the load procedure.

    """

    meta_translation = {'CATDESC': 'desc', 'FILLVAL': 'fill',
                        'LABLAXIS': 'plot_label', 'VALIDMAX': 'value_max',
                        'VALIDMIN': 'value_min', 'VAR_NOTES': 'notes'}
    data, meta = cdw.load(fnames, tag=tag, inst_id=inst_id, pandas_format=False,
                          meta_translation=meta_translation,
                          drop_dims=['dim_empty', 'dim0', 'unit_time'],
                          use_cdflib=True)

    if to_pandas:
        data = data.to_pandas()

    return data, meta


def clean(self):
    """Clean ACE data to the specified level.

    Note
    ----
    Basic cleaning to replace fill values with NaN

    """

    # Get a list of coords for the data
    if self.pandas_format:
        coords = [self.data.index.name]
    else:
        coords = [key for key in self.data.coords]

    for key in self.variables:
        # Skip over the coordinates when cleaning
        if key not in coords:
            fill = self.meta[key, self.meta.labels.fill_val]

            # Replace fill with nan
            fill_mask = self[key] == fill
            self[key] = self.data[key].where(~fill_mask)
            self.meta[key] = {self.meta.labels.fill_val: np.nan}
    return
