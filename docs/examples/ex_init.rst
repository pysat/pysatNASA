Loading ICON IVM data
========================

pysatNASA uses `pysat <https://github.com/pysat/pysat>`_ to load
space science instrument data.  As specified in the
`pysat tutorial <https://pysat.readthedocs.io/en/latest/tutorial.html>`_,
data may be loaded using the following commands.  Data from the Ion Velocity
Meter on board the Ionospheric CONnection Explorer (ICON) is used as an example.

::


   import datetime as dt
   import pysat
   import pysatNASA as py_nasa

   old_time = dt.datetime(2020, 1, 1)
   ivm = pysat.Instrument(inst_module=py_nasa.instruments.icon_ivm,
                          inst_id='a', update_files=True)
   ivm.download(start=old_time)
   ivm.load(date=old_time)
   print(ivm)


The output shows

::
