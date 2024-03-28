# -*- coding: utf-8 -*-
"""Interface for pysatNASA to manage and analyze multiple pysat instruments.

Each instrument is contained within a subpackage of the pysatNASA.instruments
package.
"""

import logging

import pysat

__all__ = ['de2', 'icon']

# TODO(#89): reevaluate logger suppression if fixes implemented in pysat
# Save current level and turn off before constellation import
user_level = pysat.logger.level
pysat.logger.setLevel(logging.WARNING)

# Import constellation objects
for const in __all__:
    exec("from pysatNASA.constellations import {:}".format(const))

# Restore user level
pysat.logger.setLevel(user_level)

# Remove dummy variable
del const, user_level
