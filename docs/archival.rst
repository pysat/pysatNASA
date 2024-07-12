Building data files for archival at NASA SPDF
=============================================

The codes and routines at :py:mod:`pysatNASA` are designed for end-users of
NASA data products. However, pysat in general has also been used to build
operational instruments for generating archival data to be uploaded to the
Space Physics Data Facility (SPDF) at NASA.

In general, such instruments should include separate naming conventions. An
example of this is the REACH data, where netCDF4 files are generated for
archival purposes as part of the :py:mod:`ops_reach` package, but can be
accessed by the end user through :py:mod:`pysatNASA`.

In general, a :py:class:`pysat.Instrument` object can be constructed for any
dataset. Full instructions and conventions can be found
`at ReadTheDocs <https://pysat.readthedocs.io/en/latest/new_instrument.html>`_.
In the case of the REACH data, the operational code reads in a series of CSV
files and updates the metadata according to user specifications. Once the file
is loaded, it can be exported to a netCDF4 file via pysat. In the simplest case,
this is:

::

  reach = pysat.Instrument(inst_module=aero_reach, tag='l1b', inst_id=inst_id)
  pysat.utils.io.inst_to_netcdf(reach, 'output_file.nc', epoch_name='Epoch')


However, there are additional options when translating pysat metadata to SPDF
preferred formats.  An example of this is:

::

  # Use meta translation table to include SPDF preferred format.
  # Note that multiple names are output for compliance with pysat.
  # Using the most generalized form for labels for future compatibility.
  meta_dict = {reach.meta.labels.min_val: ['VALIDMIN'],
               reach.meta.labels.max_val: ['VALIDMAX'],
               reach.meta.labels.units: ['UNITS'],
               reach.meta.labels.name: ['CATDESC', 'LABLAXIS', 'FIELDNAM'],
               reach.meta.labels.notes: ['VAR_NOTES'],
               reach.meta.labels.fill_val: ['_FillValue'],
               'Depend_0': ['DEPEND_0'],
               'Format': ['FORMAT'],
               'Monoton': ['MONOTON'],
               'Var_Type': ['VAR_TYPE']}

  pysat.utils.io.inst_to_netcdf(reach, 'output_file.nc', epoch_name='Epoch',
                                meta_translation=meta_dict,
                                export_pysat_info=False)


In this case, note that the pysat 'name' label is output to three different
metadata values required by the ITSP standards. Additionally, the
:py:attr:`export_pysat_info` option is set to false here. This drops several
internal :py:mod:`pysat` metadata values before writing to file.

A full guide to SPDF metadata standards can be found 
`at SPDF <https://spdf.gsfc.nasa.gov/istp_guide/istp_guide.html>`_.

Other best practices for archival include adding the operational software
version to the metadata header before writing. The pysat version will be
automatically written to the metadata.

::

  reach.meta.header.Software_version = ops_reach.__version__


A full example script to generate output files can be found at
https://github.com/jklenzing/ops_reach/blob/main/scripts/netcdf_gen.py
