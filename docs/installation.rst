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
Python 3.7+ and pysat 3.0.0+.

 ================== =================
 Common modules     Community modules
 ================== =================
  beautifulsoup4     cdflib>=0.4.4
  lxml               pysat>=3.0.2
  netCDF4
  numpy
  pandas
  requests
  xarray>2022.06.0
 ================== =================


Installation Options
--------------------

1. Clone the git repository
::


   git clone https://github.com/pysat/pysatNASA.git


2. Install pysatNASA:
   Change directories into the repository folder and run the setup.py file.
   There are a few ways you can do this:

   A. Install on the system (root privileges required)::


        sudo python setup.py install
   B. Install at the user level::


        python setup.py install --user
   C. Install with the intent to develop locally::


        python setup.py develop --user

.. extras-require:: all
    :setup.cfg:

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
