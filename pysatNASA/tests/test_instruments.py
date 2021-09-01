"""Unit and Integration Tests for each instrument module.

Note
----
Imports test methods from pysat.tests.instrument_test_class

"""

# Make sure to import your instrument library here
import pysatNASA

# Import the test classes from pysat
from pysat.tests.instrument_test_class import InstTestClass

# Tell the standard tests which instruments to run each test on.
InstTestClass.apply_marks_to_tests(InstTestClass,
                                   inst_loc=pysatNASA.instruments)


class TestInstruments(InstTestClass):
    """Main class for instrument tests.

    Note
    ----
    All standard tests, setup, and teardown inherited from the core pysat
    instrument test class.

    """
