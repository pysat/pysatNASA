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
Python 3.6+.

 ================ =================
 Common modules   Community modules
 ================ =================
  netCDF4          cdflib
  numpy            pysat
  pandas
  requests
  xarray
  beautifulsoup4
  lxml
 ================ =================


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
