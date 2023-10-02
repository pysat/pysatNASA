"""General methods for NASA instruments."""

import numpy as np

import pysat


# Define standard clean warnings
clean_warnings = {level: [('logger', 'WARN',
                           'No cleaning routines available for',
                           level)] for level in ['clean', 'dusty', 'dirty']}


def init(self, module, name):
    """Initialize the Instrument object with instrument specific values.

    Parameters
    -----------
    module : module
        module from general methods, eg, icon, de2, cnofs, etc
    name : str
        name of instrument of interest, eg, 'ivm'

    Note
    ----
    Runs once upon instantiation.

    """

    # Set acknowledgements
    self.acknowledgements = getattr(module, 'ackn_str')

    if hasattr(module, 'rules_url'):
        self.acknowledgements.format(getattr(module, 'rules_url')[name])

    pysat.logger.info(self.acknowledgements)

    # Set references
    refs = getattr(module, 'refs')
    try:
        # See if there is a tag level reference
        inst_refs = refs[name][self.tag]
    except TypeError:
        # No tag-level ref, use name-levele
        inst_refs = refs[name]
    if 'mission' in refs.keys():
        self.references = '\n'.join((refs['mission'], inst_refs))
    else:
        self.references = inst_refs

    return


def clean(self, skip_names=None):
    """Clean data to the specified level.

    Parameters
    ----------
    skip_names : list of str
        List of names to skip for cleaning. (default=None)

    Note
    ----
    Basic cleaning to replace fill values with NaN

    """

    # Get a list of coords for the data. These should be skipped for cleaning.
    if self.pandas_format:
        skip_key = [self.data.index.name]
    else:
        skip_key = [key for key in self.data.coords.keys()]

    if skip_names:
        # Add additional variable names to skip
        for key in skip_names:
            skip_key.append(key)

    for key in self.variables:
        # Check for symmetric dims
        # Indicates transformation matrix, xarray cannot broadcast
        # Skip over the coordinates when cleaning
        if key not in skip_key:
            fill = self.meta[key, self.meta.labels.fill_val]

            # Replace fill with nan
            fill_mask = self[key] == fill
            self[key] = self.data[key].where(~fill_mask)
            self.meta[key] = {self.meta.labels.fill_val: np.nan}
    return


def clean_warn(self):
    """Warn user that cleaning not yet available for this data set.

    Note
    ----
    'clean' - Not specified
    'dusty' - Not specified
    'dirty' - Not specified
    'none'  No cleaning applied, routine not called in this case.

    """
    pysat.logger.warning(' '.join(('No cleaning routines available for',
                                   self.platform, self.name)))

    return
