import pysat
"""
Creates a constellation from NASA ICON instrumentation
"""

# FIXME: syntax has changed since this was written.  Not imported
ivm = pysat.Instrument('icon', 'ivm', inst_id='a', tag='level_2',
                       clean_level='clean', update_files=True)
euv = pysat.Instrument('icon', 'euv', inst_id='', tag='level_2',
                       clean_level='clean', update_files=True)
fuv = pysat.Instrument('icon', 'fuv', inst_id='', tag='level_2',
                       clean_level='clean', update_files=True)
mighti_green = pysat.Instrument('icon', 'mighti', inst_id='green',
                                tag='level_2', clean_level='clean',
                                update_files=True)
mighti_red = pysat.Instrument('icon', 'mighti', inst_id='red', tag='level_2',
                              clean_level='clean', update_files=True)

instruments = [ivm, euv, fuv, mighti_green, mighti_red]
