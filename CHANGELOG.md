# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/).

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
