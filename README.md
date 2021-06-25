<div align="left">
        <img height="0" width="0px">
        <img width="20%" src="https://raw.githubusercontent.com/pysat/pysatNASA/main/docs/figures/pysatnasa_logo.jpg" alt="pysatNASA" title="pysatNASA" </img>
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
Python 3.7+.

| Common modules | Community modules |
| -------------- | ----------------- |
| beautifulsoup4 | cdflib            |
| lxml           | pysat             |
| netCDF4        |                   |
| numpy          |                   |
| pandas         |                   |
| requests       |                   |
| xarray         |                   |

## GitHub Installation

Currently, the main way to get pysatNASA is through github.

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
pysatNASA is currently in an initial development phase and requires pysat 3.0.0.  

# Using with pysat

The instrument modules are portable and designed to be run like any pysat instrument.

```
import pysat
from pysatNASA.instruments import icon_ivm

ivm = pysat.Instrument(inst_module=icon_ivm, inst_id='a')
```
Another way to use the instruments in an external repository is to register the instruments.  This only needs to be done the first time you load an instrument.  Afterward, pysat will identify them using the `platform` and `name` keywords.

```
import pysat

pysat.utils.registry.register('pysatNASA.instruments.icon_ivm')
ivm = pysat.Instrument('icon', 'ivm', inst_id='a')
```
