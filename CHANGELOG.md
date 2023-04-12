# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/).

## [0.X.X] - 2023-XX-XX
* New Instruments
  * ACE EPAM
  * ACE MAG
  * ACE SIS
  * ACE SWEPAM
  * DE2 Fabry-Perot Interferometer (FPI)
  * DE2 Vector Electric Field Instrument (VEFI) and magnetometer
  * DMSP SSUSI EDR-Aurora data
  * IGS GPS (TEC and ROTI)
  * TIMED GUVI
* Add TIMED GUVI platform to support L1C intensity datasets.
  * Type of sensor source handled by inst_id with options of
    spectrograph, imaging
  * Resolution of dataset handled by tag with
    low, high
* Added CDAWeb methods that can use cdasws to get the remote file list
* Bug Fixes
  * Updated CDAWeb routines to allow for data stored by year/day-of-year
  * Updated GOLD nmax to sort scans by time.
  * Added 1 usec to GOLD nmax channel B times to ensure uniqueness
  * Fixed multi-file loads for cdf xarray datasets.
* Documentation
  * Added TIMED-GUVI platform
  * Added missing sub-module imports
  * Added discussion of ICON constellation to docstrings, including caveats
* Enhancements
  * Updated platform methods to follow a consistent style and work with the
    general `init` function
  * Added unit tests for the different platform method attributes
  * xarray support for TIMED SABER and SEE
  * Added `drop_dims` kwarg to `load_xarray` interface so that orphan dims can
    be removed before attempting to merge.
* Deprecations
  * Deprecated jpl_gps instrtument module, moved roti instrument to igs_gps
* Maintenance
  * Removed duplicate tests if pysatCDF not isntalled
  * Only test pysatCDF on GitHub Actions for older numpy versions
  * Updated actions and templates based on pysatEcosystem docs
  * Remove pandas cap on NEP29 tests
  * Updated dosctring style for consistency
  * Removed version cap for xarray
  * Added manual workflow to check that latest RC is installable through test pip
  * Update meta label type for instruments
  * Use pyproject.toml to manage setup

## [0.0.4] - 2022-11-07
* Update instrument tests with new test class
* Support xarray datasets through cdflib
* Preferentially loads data into pandas using pysatCDF if installed
* Adds pysatCDF to optional requirements invoked via '[all]' option at installation
* New Instruments
  * JPL GPS ROTI
* Bug Fixes
  * Fixed a bug in metadata when loading GOLD Nmax data.
  * Fixed a bug in user feedback for `methods.cdaweb.download`
  * Fixed a bug in loading ICON IVM data (added multi_file_day = True)
  * Allow for array-like OMNI HRO meta data
  * Fixed date handling for OMNI HRO downloads
  * Updated filenames for TIMED SABER
* Maintenance
  * Reduce duplication of code in instrument modules
  * Include flake8 linting of docstrings and style in Github Actions
  * Move OMNI HRO custom functions to a methods module
  * Deprecate OMNI HRO custom functions in instrument module
  * Update GitHub actions to the latest versions
  * Added downstream test to test code with pysat RC
  * Remove deprecated `convert_timestamp_to_datetime` calls
  * Remove deprecated pandas syntax
  * Added version cap for xarray 2022.11
* Documentation
  * New logo added

## [0.0.3] - 2022-05-18
* Include flake8 linting of docstrings and style in Github Actions
* Include Windows tests in Github Actions
* Bug Fixes
  * Expanded cleaning of ICON IVM ion drifts to more variables
  * Fixed a bug in loading ICON IVM data (added multi_file_day = True)
  * Fixed a bug where OMNI meta data float values are loaded as arrays
  * Fixed metadata type issues when loading ICON instrument data.
* Maintenance
  * Removed dummy vars after importing instruments and constellations
  * Updated NEP29 compliance in Github Actions
  * Limit versions of hacking for improved pip compliance
  * Update instrument template standards
  * Updated documentation style
  * Removed cap on cdflib

## [0.0.2] - 2021-06-07
* Updated Instruments and routines to conform with changes made for pysat 3.0
* Added documentation
* Instrument Changes
  * Preliminary support added for SES-14 GOLD Nmax
  * Updated cleaning routines for C/NOFS IVM data
  * Migrated remote server for ICON instruments to SPDF from UCB
  * Renamed ROCSAT1 IVM as FORMOSAT1 IVM
  * Dropped support for SPORT IVM (unlaunched, moved to pysatIncubator)
* Implements GitHub Actions as primary CI test environment
* Improved PEP8 compliance
* Replaced pysatCDF with cdflib support
* Bug Fixes
  * `remote_file_list` error if start/stop dates unspecified
  * Improved download robustness

## [0.0.1] - 2020-08-13
* Initial port of existing routines from pysat
