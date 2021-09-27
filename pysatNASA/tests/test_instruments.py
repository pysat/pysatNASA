"""Unit and Integration Tests for each instrument module.

Note
----
Imports test methods from pysat.tests.instrument_test_class

"""

# Make sure to import your instrument library here
import pysatNASA

# Import the test classes from pysat
from pysat.tests.classes.cls_instrument_library import InstLibTests

# Tell the standard tests which instruments to run each test on.
InstLibTests.initialize_test_package(InstLibTests,
                                     inst_loc=pysatNASA.instruments)


class TestInstruments(InstLibTests):
    """Main class for instrument tests.

    Note
    ----
    All standard tests, setup, and teardown inherited from the core pysat
    instrument test class.

    """
