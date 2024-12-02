Installation
============

The following instructions will allow you to install pysatNASA.

Prerequisites
-------------

.. image:: figures/poweredbypysat.png
    :width: 150px
    :align: right
    :alt: powered by pysat Logo, blue planet with orbiting python


pysatNASA uses common Python modules, as well as modules developed by
and for the Space Physics community.  This module officially supports
Python 3.9+ and pysat 3.2.0+.

 ================== =================
 Common modules     Community modules
 ================== =================
  beautifulsoup4     cdasws>=1.7.42
  lxml               cdflib>=1.0.4
  netCDF4>=1.6.0     pysat>=3.2.0
  numpy
  pandas
  requests
  scipy>=1.10.0
  xarray
 ================== =================


Installation Options
--------------------

1. Clone the git repository
::


   git clone https://github.com/pysat/pysatNASA.git


2. Install pysatNASA:
   Change directories into the repository folder and build the project.
   There are a few ways you can do this:

   A. Install on the system (root privileges required)::


        sudo pip install .

   B. Install at the user level::


        pip install --user .

   C. Install with the intent to change the code::


        pip install --user -e .

.. extras-require:: pysatcdf
    :pyproject:

.. extras-require:: test
    :pyproject:

.. extras-require:: doc
    :pyproject:

.. _post-install:

Post Installation
-----------------

After installation, you may register the :py:mod:`pysatNASA`
:py:class:`Instrument` sub-modules with pysat.  If this is your first time using
pysat, check out the `quickstart guide
<https://pysat.readthedocs.io/en/latest/quickstart.html>`_ for pysat. Once pysat
is set up, you may choose to register the the :py:mod:`pysatNASA`
:py:class:`Instruments` sub-modules by:

.. code:: python


   import pysat
   import pysatNASA

   pysat.utils.registry.register_by_module(pysatNASA.instruments)

You may then use the pysat :py:attr:`platform` and :py:attr:`name` keywords to
initialize the model :py:class:`Instrument` instead of the
:py:attr:`inst_module` keyword argument.
