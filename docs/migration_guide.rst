Migration from pysat 2
======================

With the release of pysat 3.0.0, the pysat project now keeps instrument modules
within distinct packages. Each of these packages acts as an interface between
the core pysat package and a unique data provider.  pysatNASA fills this role
for the `Space Physics Data Facility <https://spdf.gsfc.nasa.gov/>`_ at NASA.

Registering the pysatNASA library
---------------------------------

While each module can be loaded separately, users may find it easier
to register all instruments.

.. code ::

  import pysat
  import pysatNASA
  pysat.utils.registry.register_by_module(pysatNASA.instruments)

This creates a shortcut so that instruments may be loaded using only
``platform`` and ``name`` without having to load the instrument package each
time.

.. code ::

  import pysat
  ivm = pysat.Instrument('cnofs', 'ivm')


Modifying the directory structure
---------------------------------

The internal directory structure has been updated in pysat 3.0.0 to include
a separate layer for ``inst_id``.  Users who have already downloaded data in
a previous version should follow `this tutorial
<https://pysat.readthedocs.io/en/latest/tutorial/tutorial_v3_upgrade.html>`_
to make their local data directories compatible with the new version.

A Note about ICON data
----------------------

Starting with pysatNASA 0.0.2, the data for the Ionospheric CONnection Explorer
(ICON) is now accessed from the SPDF server directly rather than the University
of California at Berkeley server.  There is a slight update in the file names at
the new location, which is not compatible with the previous versions of pysat.
It is recommended that users download this data using the new software.
