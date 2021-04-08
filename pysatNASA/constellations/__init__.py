__all__ = ['de2', 'icon']

for const in __all__:
    exec("from pysatNASA.constellations import {:}".format(const))
