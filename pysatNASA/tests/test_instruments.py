"""Unit and Integration Tests for each instrument module.

Note
----
Imports test methods from pysat.tests.instrument_test_class

"""

import warnings

import pytest

# Make sure to import your instrument library here
import pysatNASA

# Import the test classes from pysat
from pysat.tests.classes import cls_instrument_library as clslib

try:
    import pysatCDF  # noqa: F401
    # If this successfully imports, tests need to be run with both pysatCDF
    # and cdflib
    cdflib_only = False
except ImportError:
    # pysatCDF is not present, standard tests default to cdflib.
    cdflib_only = True


# Tell the standard tests which instruments to run each test on.
# Need to return instrument list for custom tests.
instruments = clslib.InstLibTests.initialize_test_package(
    clslib.InstLibTests, inst_loc=pysatNASA.instruments)

# Create a new list of instruments with the option of forcing cdflib
instruments['cdf'] = []
for inst in instruments['download']:
    fname = inst['inst_module'].supported_tags[inst['inst_id']][inst['tag']]
    if '.cdf' in fname:
        instruments['cdf'].append(inst)


class TestInstruments(clslib.InstLibTests):
    """Main class for instrument tests.

    Note
    ----
    All standard tests, setup, and teardown inherited from the core pysat
    instrument test class.

    """

    @pytest.mark.second
    @pytest.mark.parametrize("inst_dict", instruments['cdf'])
    @pytest.mark.skipif(cdflib_only)
    def test_load_cdflib(self, inst_dict):
        """Test that instruments load at each cleaning level.

        Parameters
        ----------
        inst_dict : dict
            Dictionary containing info to instantiate a specific instrument.

        """

        test_inst, date = clslib.initialize_test_inst_and_date(inst_dict)
        files = test_inst.files.files
        if len(files) > 0:
            # Set Clean Level
            target = 'Fake Data to be cleared'
            test_inst.data = [target]
            try:
                test_inst.load(date=date, use_header=True, use_cdflib=True)
            except ValueError as verr:
                # Check if instrument is failing due to strict time flag
                if str(verr).find('Loaded data') > 0:
                    test_inst.strict_time_flag = False
                    with warnings.catch_warnings(record=True) as war:
                        test_inst.load(date=date, use_header=True)
                    assert len(war) >= 1
                    categories = [war[j].category for j in range(0, len(war))]
                    assert UserWarning in categories
                else:
                    # If error message does not match, raise error anyway
                    raise(verr)

            # Make sure fake data is cleared
            assert target not in test_inst.data
        else:
            pytest.skip("Download data not available.")

        return
