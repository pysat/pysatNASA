__all__ = ['de2', 'icon']

for inst in __all__:
    exec("from pysatNASA.constellations import {x}".format(x=inst))
