"""Core library for pysatNASA.

This is a library of `pysat` instrument modules and methods designed to support
NASA instruments and missions archived at the Community Data Analysis Web
portal.

"""

import importlib
import importlib_metadata

from pysatNASA import constellations  # noqa F401
from pysatNASA import instruments  # noqa F401

# set version
try:
    __version__ = importlib.metadata.version('pysatNASA')
except AttributeError:
    # Python 3.6 requires a different version
    __version__ = importlib_metadata.version('pysatNASA')

print(__version__)
