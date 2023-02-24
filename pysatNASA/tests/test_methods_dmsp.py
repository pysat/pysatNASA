"""Unit tests for the DMSP methods."""

from pysatNASA.instruments.methods import dmsp


class TestDMSPMethods(object):
    """Unit tests for `pysat.instruments.methods.dmsp`."""

    def setup_method(self):
        """Set up the unit test environment for each method."""
        self.names = ['ssusi']
        return

    def teardown_method(self):
        """Clean up the unit test environment after each method."""

        del self.names
        return

    def test_ack(self):
        """Test that the acknowledgements reference the correct platform."""

        assert dmsp.ackn_str.find(
            'Defense Meteorological Satellite Program') >= 0
        return

    def test_ref(self):
        """Test that all DMSP instruments have references."""

        for name in self.names:
            assert name in dmsp.refs.keys(), "No reference for {:}".format(name)
        return
