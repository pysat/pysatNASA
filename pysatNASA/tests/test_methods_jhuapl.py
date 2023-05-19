"""Unit tests for the JHU-APL method functions."""

import warnings

import pysat

from pysatNASA.instruments.methods import jhuapl


class TestDeprecation(object):
    """Unit tests for deprecated functions."""

    def setup_method(self):
        """Set up the unit test environment for each method."""
        warnings.simplefilter("always", DeprecationWarning)
        return

    def teardown_method(self):
        """Clean up the unit test environment after each method."""

        return

    def test_expand_coords(self):
        """Test that convert_timestamp_to_datetime is deprecated."""

        warn_msgs = ["".join(["This function is now included in ",
                              "`pysat.utils.coords` as `expand_xarray_dims`, ",
                              "and so this function will be removed in 0.1.0+",
                              " to reduce redundancy"])]

        with warnings.catch_warnings(record=True) as war:
            jhuapl.expand_coords([], None)

        # Ensure the minimum number of warnings were raised
        assert len(war) >= len(warn_msgs)

        # Test the warning messages, ensuring each attribute is present
        pysat.utils.testing.eval_warnings(war, warn_msgs)
        return
