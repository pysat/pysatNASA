#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3986131
#
# DISTRIBUTION STATEMENT A: Approved for public release. Distribution is
# unlimited.
# ----------------------------------------------------------------------------
"""Provides non-instrument specific routines for the TIMED data."""

rules_url = {'guvi': 'http://guvitimed.jhuapl.edu/home_guvi-datausage',
             'saber': 'https://saber.gats-inc.com/data_services.php',
             'see': 'https://www.timed.jhuapl.edu/WWW/scripts/mdc_rules.pl'}

ackn_str = "".join(["This Thermosphere Ionosphere Mesosphere Energetics ",
                    "Dynamics (TIMED) satellite data is provided through ",
                    "CDAWeb. Please see the Rules of the Road at {:s}"])

refs = {'guvi': ''.join(['Larry J. Paxton, Andrew B. Christensen, David C. ',
                         'Humm, Bernard S. Ogorzalek, C. Thompson Pardoe, ',
                         'Daniel Morrison, Michele B. Weiss, W. Crain, ',
                         'Patricia H. Lew, Dan J. Mabry, John O. Goldsten, ',
                         'Stephen A. Gary, David F. Persons, Mark J. Harold, ',
                         'E. Brian Alvarez, Carl J. Ercol, Douglas J. ',
                         'Strickland, and Ching-I. Meng "Global ultraviolet ',
                         'imager (GUVI): measuring composition and energy ',
                         'inputs for the NASA Thermosphere Ionosphere ',
                         'Mesosphere Energetics and Dynamics (TIMED) mission",',
                         'Proc. SPIE 3756, Optical Spectroscopic Techniques ',
                         'and Instrumentation for Atmospheric and Space ',
                         'Research III, (20 October 1999); ',
                         'doi:10.1117/12.366380']),
        'saber': ' '.join(['Esplin, R., Mlynczak, M. G., Russell, J., Gordley,',
                           'L., & The SABER Team. (2023). Sounding of the',
                           'Atmosphere using Broadband Emission Radiometry',
                           '(SABER): Instrument and science measurement',
                           'description. Earth and Space Science, 10,',
                           'e2023EA002999.',
                           'https://doi.org/10.1029/2023EA002999.\n',
                           'Overview of the SABER experiment and preliminary',
                           'calibration results (1999). J. M. Russell III, M.',
                           'G. Mlynczak, L. L. Gordley, J. J. Tansock, Jr.,',
                           'and R. W. Esplin, Proc. SPIE 3756, 277,',
                           'DOI:10.1117/12.366382']),
        'see': ' '.join(('Woods, T. N., Eparvier, F. G., Bailey,',
                         'S. M., Chamberlin, P. C., Lean, J.,',
                         'Rottman, G. J., Solomon, S. C., Tobiska,',
                         'W. K., and Woodraska, D. L. (2005),',
                         'Solar EUV Experiment (SEE): Mission',
                         'overview and first results, J. Geophys.',
                         'Res., 110, A01312, doi:10.1029/2004JA010765.'))}
