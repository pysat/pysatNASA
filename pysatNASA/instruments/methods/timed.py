# -*- coding: utf-8 -*-
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
        'saber': '',
        'see': ' '.join(('Woods, T. N., Eparvier, F. G., Bailey,',
                         'S. M., Chamberlin, P. C., Lean, J.,',
                         'Rottman, G. J., Solomon, S. C., Tobiska,',
                         'W. K., and Woodraska, D. L. (2005),',
                         'Solar EUV Experiment (SEE): Mission',
                         'overview and first results, J. Geophys.',
                         'Res., 110, A01312, doi:10.1029/2004JA010765.'))}
