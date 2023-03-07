<div align="left">
        <img height="0" width="0px">
        <img width="20%" src="https://raw.githubusercontent.com/pysat/pysatNASA/main/docs/figures/logo.png" alt="pysatNASA" title="pysatNASA" </img>
</div>

# pysatNASA: pysat support for NASA Space Science instruments
[![PyPI Package latest release](https://img.shields.io/pypi/v/pysatNASA.svg)](https://pypi.python.org/pypi/pysatNASA)
[![Build Status](https://github.com/github/docs/actions/workflows/main.yml/badge.svg)](https://github.com/github/docs/actions/workflows/main.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/pysat/pysatNASA/badge.svg?branch=main)](https://coveralls.io/github/pysat/pysatNASA?branch=main)

[![Documentation Status](https://readthedocs.org/projects/pysatnasa/badge/?version=latest)](https://pysatnasa.readthedocs.io/en/latest/?badge=latest)
[![DOI](https://zenodo.org/badge/287387638.svg)](https://zenodo.org/badge/latestdoi/287387638)

# Installation

The following instructions provide a guide for installing pysatNASA and give
some examples on how to use the routines

### Prerequisites

pysatNASA uses common Python modules, as well as modules developed by
and for the Space Physics community.  This module officially supports
Python 3.8+.

| Common modules   | Community modules | Optional Modules |
| ---------------- | ----------------- |------------------|
| beautifulsoup4   | cdflib            | pysatCDF         |
| lxml             | pysat>=3.0.4      |                  |
| netCDF4          |                   |                  |
| numpy<1.24       |                   |                  |
| pandas           |                   |                  |
| requests         |                   |                  |
| xarray           |                   |                  |

## PyPi Installation
```
pip install pysatNASA
```

## GitHub Installation

```
git clone https://github.com/pysat/pysatNASA.git
```

Change directories into the repository folder and run the setup.py file.  For
a local install use the "--user" flag after "install".

```
cd pysatNASA/
python setup.py install
```

Note: pre-1.0.0 version
-----------------------
pysatNASA is currently in an initial development phase and requires pysat 3.0.4.  
Feedback and contributions are appreciated.

# Using with pysat

The instrument modules are portable and designed to be run like any pysat instrument.

```
import pysat
from pysatNASA.instruments import icon_ivm

ivm = pysat.Instrument(inst_module=icon_ivm, inst_id='a')
```
Another way to use the instruments in an external repository is to register the
instruments.  This only needs to be done the first time you load an instrument.  
Afterward, pysat will identify them using the `platform` and `name` keywords.

```
import pysat

pysat.utils.registry.register(['pysatNASA.instruments.icon_ivm'])
ivm = pysat.Instrument('icon', 'ivm', inst_id='a')
```

# CDF Integration
For data products stored as CDF files, this package can use either `cdflib` or
`pysatCDF`.  Note that `cdflib` is a pure python package and more readily
deployable across systems, whereas `pysatCDF` interfaces with the fortran.  
This is a faster approach for loading data, but may not install on all systems.  
Therefore, `pysatCDF` is optional rather than required.

You can specify which load routine to use via the optional `use_cdflib` kwarg.
If no kwarg is specified, `pysatNASA` will default to `pysatCDF` if it is
successfully installed, and default to `cdflib` otherwise.

```
ivm = pysat.Instrument('cnofs', 'ivm', use_cdflib=True)
```
