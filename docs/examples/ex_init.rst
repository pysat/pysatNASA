Loading ICON IVM data
=====================

pysatNASA uses `pysat <https://github.com/pysat/pysat>`_ to load
space science instrument data.  As specified in the
`pysat tutorial <https://pysat.readthedocs.io/en/latest/tutorial.html>`_,
data may be loaded using the following commands.  Data from the Ion Velocity
Meter on board the Ionospheric CONnection Explorer `(ICON) <https://www.nasa.gov/icon>`_ is used as an example.

::


   import datetime as dt
   import pysat
   import pysatNASA as py_nasa
   pysat.utils.registry.register_by_module(py_nasa.instruments)

   old_time = dt.datetime(2020, 1, 1)
   ivm = pysat.Instrument(platform='icon', name='ivm',
                          inst_id='a', update_files=True)
   ivm.download(start=old_time)
   ivm.load(date=old_time)
   print(ivm)


The output shows some basic info about the instrument object, as well as
information about the data loaded.

::

  pysat Instrument object
  -----------------------
  Platform: 'icon'
  Name: 'ivm'
  Tag: ''
  Instrument id: 'a'

  Data Processing
  ---------------
  Cleaning Level: 'clean'
  Data Padding: None
  Keyword Arguments Passed to list_files: {}
  Keyword Arguments Passed to load: {}
  Keyword Arguments Passed to preprocess: {}
  Keyword Arguments Passed to download: {}
  Keyword Arguments Passed to list_remote_files: {}
  Keyword Arguments Passed to clean: {}
  Keyword Arguments Passed to init: {}
  Custom Functions: 0 applied

  Local File Statistics
  ---------------------
  Number of files: 402
  Date Range: 22 October 2019 --- 29 December 2020

  Loaded Data Statistics
  ----------------------
  Date: 01 January 2020
  DOY: 001
  Time range: 31 December 2019 23:59:57 --- 01 January 2020 23:59:55
  Number of Times: 86400
  Number of variables: 91

  Variable Names:
  A_Activity          A_Status            Altitude
                          ...
  Unit_Vector_Zonal_X Unit_Vector_Zonal_Y Unit_Vector_Zonal_Z

  pysat Meta object
  -----------------
  Tracking 21 metadata values
  Metadata for 92 standard variables
  Metadata for 0 ND variables
