"""General methods for NASA instruments."""

import pysat


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
    if 'mission' in refs.keys():
        self.references = '\n'.join((refs['mission'], refs[name]))
    else:
        self.references = refs[name]

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
    pysat.loggern.warn(' '.join(('No cleaning routines available for',
                                 self.platform, self.name)))

    return
