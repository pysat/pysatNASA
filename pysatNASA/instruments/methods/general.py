"""General methods for NASA instruments."""

import warnings

import pysat


def init(self, module, name):
    """Initialize the Instrument object with instrument specific values.

    Parameters
    -----------
    module : python module
        module from general methods, eg, icon, de2, cnofs, etc
    name : str
        name of instrument of interest, eg, 'ivm'

    Runs once upon instantiation.

    """

    # Set acknowledgements
    self.acknowledgements = getattr(module, 'ackn_str')
    pysat.logger.info(self.acknowledgements)

    # Set references
    refs = getattr(module, 'refs')
    if 'mission' in refs.keys():
        self.references = '\n'.join((refs['mission'], refs[name]))
    else:
        self.references = refs[name]

    return
