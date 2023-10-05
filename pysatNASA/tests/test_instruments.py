"""Unit and Integration Tests for each instrument module.

Note
----
Imports test methods from pysat.tests.instrument_test_class

"""

import warnings

import pytest

# Import the test classes from pysat
import pysat
from pysat.tests.classes import cls_instrument_library as clslib
from pysat.utils import testing

# Make sure to import your instrument library here
import pysatNASA

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
        temp_inst, _ = clslib.initialize_test_inst_and_date(inst)
        if temp_inst.pandas_format:
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
    @pytest.mark.skipif(cdflib_only,
                        reason=" ".join(("Additional load tests not required",
                                         "when pysatCDF not installed")))
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
                    raise ValueError(verr)

            # Make sure fake data is cleared
            assert target not in test_inst.data
        else:
            pytest.skip("Download data not available.")

        return

    # TODO(https://github.com/pysat/pysat/issues/1020): This test should be
    # removed when header level data is tested in version 3.2.0+ of pysat
    @pytest.mark.second
    @pytest.mark.parametrize("inst_dict", instruments['cdf'])
    def test_meta_header(self, inst_dict):
        """Test that instruments have header level metadata attached.

        Parameters
        ----------
        inst_dict : dict
            Dictionary containing info to instantiate a specific instrument.

        """
        test_inst, date = clslib.initialize_test_inst_and_date(inst_dict)
        try:
            test_inst.load(date=date, use_header=True, use_cdflib=True)
        except ValueError as verr:
            # Check if instrument is failing due to strict time flag
            if str(verr).find('Loaded data') > 0:
                test_inst.strict_time_flag = False
                with warnings.catch_warnings(record=True) as war:
                    test_inst.load(date=date, use_header=True, use_cdflib=True)

                assert len(war) >= 1
                categories = [war[j].category for j in range(0, len(war))]
                assert UserWarning in categories
            else:
                # If error message does not match, raise error anyway
                raise (verr)
        assert test_inst.meta.to_dict() != {}


class TestDeprecation(object):
    """Unit test for deprecation warnings."""

    def setup_method(self):
        """Set up the unit test environment for each method."""

        warnings.simplefilter("always", DeprecationWarning)
        return

    def teardown_method(self):
        """Clean up the unit test environment after each method."""

        return

    @pytest.mark.parametrize("inst_module,tag", [('jpl_gps', 'roti')])
    def test_deprecated_instruments(self, inst_module, tag):
        """Check that instantiating old instruments raises a DeprecationWarning.

        Parameters
        ----------
        inst_module : str
            name of deprecated module.
        tag : str
            tag of depracted instrument.

        """

        with warnings.catch_warnings(record=True) as war:
            pysat.Instrument(inst_module=getattr(pysatNASA.instruments,
                                                 inst_module),
                             tag=tag, use_header=True)

        warn_msgs = [" ".join(["The instrument module",
                               "`{:}`".format(inst_module),
                               "has been deprecated and will be removed",
                               "in 0.1.0+."])]

        # Ensure the minimum number of warnings were raised.
        assert len(war) >= len(warn_msgs)

        # Test the warning messages, ensuring each attribute is present.
        testing.eval_warnings(war, warn_msgs)
        return
