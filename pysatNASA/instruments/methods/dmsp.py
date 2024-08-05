#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3986131
#
# DISTRIBUTION STATEMENT A: Approved for public release. Distribution is
# unlimited.
# ----------------------------------------------------------------------------
"""Provides non-instrument specific routines for the DMSP data."""

import datetime as dt

ackn_str = "".join(["This Defense Meteorological Satellite Program (DMSP) ",
                    "satellite data is provided through CDAWeb"])

refs = {'ssusi': ''.join(('Larry J. Paxton, Daniel Morrison, Yongliang Zhang,',
                          ' Hyosub Kil, Brian Wolven, Bernard S. Ogorzalek, ',
                          'David C. Humm, and Ching-I. Meng "Validation of ',
                          'remote sensing products produced by the Special ',
                          'Sensor Ultraviolet Scanning Imager (SSUSI): a far ',
                          'UV-imaging spectrograph on DMSP F-16", Proc. SPIE ',
                          '4485, Optical Spectroscopic Techniques, Remote ',
                          'Sensing, and Instrumentation for Atmospheric and ',
                          'Space Research IV, (30 January 2002); ',
                          'doi:10.1117/12.454268'))}

# The DMSP SSUSI filename format in SPDF fully changes on 81-2023 to have a
# 6-padded revision number (previously 5-digit revision number
fmt_swap_time = dt.datetime(2023, 3, 22)


def ssusi_fname(ftimes, tag=None, inst_id=None):
    """Provide a DMSP SSUSI filename format for the desired time.

    Parameters
    ----------
    ftimes : list of dt.datetime
        List of dates and times to retrieve the filename format.
    tag : str or NoneType
        Tag name used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default=None)
    inst_id : str or NoneType
        Satellite ID used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default=None)

    Returns
    -------
    file_fmts : list
        List of filename formats for the desired times, if either `tag` or
        `inst_id` are not supplied (NoneType provided), these will be included
        as first-level format options, while the date, version, and cycle are
        second-level format options. Otherwise the date, version, and cycle are
        first-level format options.

    """
    file_fmts = list()
    for ftime in ftimes:
        if ftime < fmt_swap_time:
            file_fmt = ''.join(['dmsp{inst_id:s}_ssusi_{tag:s}_{{year:04d}}',
                                '{{day:03d}}T{{hour:02d}}{{minute:02d}}',
                                '{{second:02d}}-???????T??????-REV?????_vA',
                                '{{version:1d}}.?.?r{{cycle:03d}}.nc'])
        else:
            file_fmt = ''.join(['dmsp{inst_id:s}_ssusi_{tag:s}_{{year:04d}}',
                                '{{day:03d}}T{{hour:02d}}{{minute:02d}}',
                                '{{second:02d}}-???????T??????-REV??????_vA',
                                '{{version:1d}}.?.?r{{cycle:03d}}.nc'])

        # If desired, format the tag and inst_id
        if tag is not None and inst_id is not None:
            file_fmt = file_fmt.format(tag=tag, inst_id=inst_id)

        # Save to the list
        file_fmts.append(file_fmt)

    return file_fmts
