"""Unit tests for the common NASA platform method attributes."""


from pysatNASA.instruments import methods


class TestTIMEDMethods(object):
    """Unit tests for `pysat.instruments.methods.timed`."""

    def setup_method(self):
        """Set up the unit test environment for each method."""
        self.names = ['see', 'saber', 'guvi']
        self.module = methods.timed
        self.platform_str = '(TIMED)'
        return

    def teardown_method(self):
        """Clean up the unit test environment after each method."""

        del self.names, self.module, self.platform_str
        return

    def test_ack(self):
        """Test that the acknowledgements reference the correct platform."""

        assert self.module.ackn_str.find(self.platform_str) >= 0
        return

    def test_rules(self):
        """Test that the rules of the road exist for each instrument."""

        if hasattr(self.module, "rules_url"):
            for name in self.names:
                assert name in self.module.rules_url.keys(
                ), "No rules URL for {:}".format(name)
        return

    def test_ref(self):
        """Test that all instruments have references."""

        for name in self.names:
            assert name in self.module.refs.keys(
            ), "No reference for {:}".format(name)
        return


class TestDMSPMethods(TestTIMEDMethods):
    """Unit tests for `pysat.instruments.methods.dmsp`."""

    def setup_method(self):
        """Set up the unit test environment for each method."""
        self.names = ['ssusi']
        self.module = methods.dmsp
        self.platform_str = '(DMSP)'
        return

    def teardown_method(self):
        """Clean up the unit test environment after each method."""

        del self.names, self.module, self.platform_str
        return


class TestCNOFSMethods(TestTIMEDMethods):
    """Unit tests for `pysat.instruments.methods.cnofs`."""

    def setup_method(self):
        """Set up the unit test environment for each method."""
        self.names = ['ivm', 'plp', 'vefi']
        self.module = methods.cnofs
        self.platform_str = '(C/NOFS)'
        return

    def teardown_method(self):
        """Clean up the unit test environment after each method."""

        del self.names, self.module, self.platform_str
        return


class TestDE2Methods(TestTIMEDMethods):
    """Unit tests for `pysat.instruments.methods.de2`."""

    def setup_method(self):
        """Set up the unit test environment for each method."""
        self.names = ['lang', 'nacs', 'rpa', 'wats']
        self.module = methods.de2
        self.platform_str = 'Dynamics Explorer 2'
        return

    def teardown_method(self):
        """Clean up the unit test environment after each method."""

        del self.names, self.module, self.platform_str
        return


class TestSES14Methods(TestTIMEDMethods):
    """Unit tests for `pysat.instruments.methods.ses14`."""

    def setup_method(self):
        """Set up the unit test environment for each method."""
        self.names = ['gold']
        self.module = methods.ses14
        self.platform_str = 'Global-scale Observations of the Limb and Disk'
        return

    def teardown_method(self):
        """Clean up the unit test environment after each method."""

        del self.names, self.module, self.platform_str
        return


class TestGPSMethods(TestTIMEDMethods):
    """Unit tests for `pysat.instruments.methods.gps`."""

    def setup_method(self):
        """Set up the unit test environment for each method."""
        self.names = ['roti15min_jpl']
        self.module = methods.gps
        self.platform_str = 'GPS Total Electron Content'
        return

    def teardown_method(self):
        """Clean up the unit test environment after each method."""

        del self.names, self.module, self.platform_str
        return
