"""Interface for pysatNASA to manage and analyze multiple pysat instruments.

Each instrument is contained within a subpackage of the pysatNASA.instruments
package.
"""


__all__ = ['de2', 'icon']

for const in __all__:
    exec("from pysatNASA.constellations import {:}".format(const))
