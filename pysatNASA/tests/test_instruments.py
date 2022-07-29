"""Unit and Integration Tests for each instrument module.

Note
----
Imports test methods from pysat.tests.instrument_test_class

"""

import warnings

import pytest

import pysat
# Make sure to import your instrument library here
import pysatNASA

# Import the test classes from pysat
from pysat.tests.classes import cls_instrument_library as clslib
from pysat.tests.classes.cls_instrument_library import InstLibTests
from pysat.utils import generate_instrument_list


# Tell the standard tests which instruments to run each test on.
# Need to return instrument list for custom tests.
instruments = InstLibTests.initialize_test_package(
    InstLibTests, inst_loc=pysatNASA.instruments)


class TestInstruments(InstLibTests):
    """Main class for instrument tests.

    Note
    ----
    All standard tests, setup, and teardown inherited from the core pysat
    instrument test class.

    """

    @pytest.mark.second
    # Need to maintain download mark for backwards compatibility.
    # Can remove once pysat 3.1.0 is released and libraries are updated.
    @pytest.mark.load_options
    @pytest.mark.download
    @pytest.mark.parametrize("clean_level", ['none', 'dirty', 'dusty', 'clean'])
    @pytest.mark.parametrize("inst_dict", instruments['download'])
    def test_load_cdflib(self, clean_level, inst_dict):
        """Test that instruments load at each cleaning level.

        Parameters
        ----------
        clean_level : str
            Cleanliness level for loaded instrument data.
        inst_dict : dict
            Dictionary containing info to instantiate a specific instrument.

        """

        test_inst, date = clslib.initialize_test_inst_and_date(inst_dict)
        files = test_inst.files.files
        if len(files) > 0 and '.cdf' in files[0]:
            # Set Clean Level
            test_inst.clean_level = clean_level
            target = 'Fake Data to be cleared'
            test_inst.data = [target]
            try:
                test_inst.load(date=date, use_header=True, use_cdflib=False)
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
            # If cleaning not used, something should be in the file
            # Not used for clean levels since cleaning may remove all data
            if clean_level == "none":
                assert not test_inst.empty
        else:
            pytest.skip(" ".join(("Download data not available or instrument",
                                  "does not use cdflib.")))

        return
