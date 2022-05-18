"""Unit and Integration Tests for each instrument module.

Note
----
Imports test methods from pysat.tests.instrument_test_class

"""

import tempfile
import warnings

import pytest

import pysat
# Make sure to import your instrument library here
import pysatNASA

# Import the test classes from pysat
from pysat.tests.classes import cls_instrument_library as clslib
from pysat.tests.instrument_test_class import InstTestClass
from pysat.utils import generate_instrument_list


# Developers for instrument libraries should update the following line to
# point to their own library package
# e.g.,
# instruments = generate_instrument_list(inst_loc=mypackage.instruments)
instruments = generate_instrument_list(inst_loc=pysatNASA.instruments)

# The following lines apply the custom instrument lists to each type of test
method_list = [func for func in dir(InstTestClass)
               if callable(getattr(InstTestClass, func))]
# Search tests for iteration via pytestmark, update instrument list
for method in method_list:
    if hasattr(getattr(InstTestClass, method), 'pytestmark'):
        # Get list of names of pytestmarks
        Nargs = len(getattr(InstTestClass, method).pytestmark)
        names = [getattr(InstTestClass, method).pytestmark[j].name
                 for j in range(0, Nargs)]
        # Add instruments from your library
        if 'all_inst' in names:
            mark = pytest.mark.parametrize("inst_name", instruments['names'])
            getattr(InstTestClass, method).pytestmark.append(mark)
        elif 'download' in names:
            mark = pytest.mark.parametrize("inst_dict", instruments['download'])
            getattr(InstTestClass, method).pytestmark.append(mark)
        elif 'no_download' in names:
            mark = pytest.mark.parametrize("inst_dict",
                                           instruments['no_download'])
            getattr(InstTestClass, method).pytestmark.append(mark)


class TestInstruments(InstTestClass):
    """Main class for instrument tests.

    Note
    ----
    Uses class level setup and teardown so that all tests use the same
    temporary directory. We do not want to geneate a new tempdir for each test,
    as the load tests need to be the same as the download tests.

    """

    def setup_class(self):
        """Initialize the testing setup once before all tests are run."""
        # Make sure to use a temporary directory so that the user's setup is not
        # altered
        self.tempdir = tempfile.TemporaryDirectory()
        self.saved_path = pysat.params['data_dirs']
        pysat.params.data['data_dirs'] = [self.tempdir.name]
        # Developers for instrument libraries should update the following line
        # to point to their own subpackage location, e.g.,
        # self.inst_loc = mypackage.instruments
        self.inst_loc = pysatNASA.instruments

    def teardown_class(self):
        """Clean up downloaded files and parameters from tests."""
        pysat.params.data['data_dirs'] = self.saved_path
        self.tempdir.cleanup()
        del self.inst_loc, self.saved_path, self.tempdir

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
            # If cleaning not used, something should be in the file
            # Not used for clean levels since cleaning may remove all data
            if clean_level == "none":
                assert not test_inst.empty
        else:
            pytest.skip(" ".join(("Download data not available or instrument",
                                  "does not use cdflib.")))

        return
