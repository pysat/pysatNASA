"""Unit tests for OMNI HRO special functions."""

import datetime as dt
import numpy as np
import warnings

import pandas as pds
import pytest

import pysat
from pysatNASA.instruments.methods import omni
from pysatNASA.instruments import omni_hro as depr_omni


class TestOMNICustom(object):
    """Unit tests for `pysat.instrument.methods.omni`."""

    def setup_method(self):
        """Set up the unit test environment for each method."""

        # Load a test instrument
        self.test_inst = pysat.Instrument('pysat', 'testing', tag='',
                                          num_samples=12, clean_level='clean',
                                          use_header=True)
        self.test_inst.load(2009, 1)

        # Recast time in minutes rather than seconds
        self.test_inst.data.index = pds.Series(
            [t + dt.timedelta(seconds=(60 - i)) + dt.timedelta(minutes=i)
             for i, t in enumerate(self.test_inst.data.index)])

        # Add IMF data
        self.test_inst['BX_GSM'] = pds.Series([3.17384966, 5.98685138,
                                               1.78749668, 0.38628409,
                                               2.73080263, 1.58814078,
                                               5.24880448, 3.92347300,
                                               5.59494670, 0.93246592,
                                               5.23676319, 1.14214992],
                                              index=self.test_inst.data.index)
        self.test_inst['BY_GSM'] = pds.Series([3.93531272, 2.50331246,
                                               0.99765539, 1.07203600,
                                               5.43752734, 5.10629137,
                                               0.59588891, 2.19412638,
                                               0.15550858, 3.75433603,
                                               4.82323932, 3.61784563],
                                              index=self.test_inst.data.index)
        self.test_inst['BZ_GSM'] = pds.Series([3.94396168, 5.61163579,
                                               4.02930788, 5.47347958,
                                               5.69823962, 0.47219819,
                                               1.47760461, 3.47187188,
                                               4.12581021, 4.40641671,
                                               2.87780562, 0.58539121],
                                              index=self.test_inst.data.index)
        self.test_inst['flow_speed'] = \
            pds.Series([394.396168, 561.163579,
                        402.930788, 547.347958,
                        569.823962, 47.219819,
                        147.760461, 347.187188,
                        412.581021, 440.641671,
                        287.780562, 58.539121],
                       index=self.test_inst.data.index)

        return

    def teardown_method(self):
        """Clean up the unit test environment after each method."""

        del self.test_inst
        return

    def test_clock_angle(self):
        """Test results of calculate_clock_angle."""

        # Run the clock angle routine
        omni.calculate_clock_angle(self.test_inst)

        # Set test clock angle
        test_angle = np.array([44.93710732, 24.04132437, 13.90673288,
                               11.08167359, 43.65882745, 84.71666707,
                               21.96325222, 32.29174675, 2.15855047,
                               40.43151704, 59.17741091, 80.80882619])

        # Test the difference.  There may be a 2 pi integer ambiguity
        test_diff = abs(test_angle - self.test_inst['clock_angle'])
        assert np.all(test_diff < 1.0e-8)
        return

    def test_yz_plane_mag(self):
        """Test the Byz plane magnitude calculation."""

        # Run the clock angle routine
        omni.calculate_clock_angle(self.test_inst)

        # Calculate plane magnitude
        test_mag = np.array([5.57149172, 6.14467489, 4.15098040, 5.57747612,
                             7.87633407, 5.12807787, 1.59323538, 4.10707742,
                             4.12873986, 5.78891590, 5.61652942, 3.66489971])

        # Test the difference
        test_diff = abs(test_mag - self.test_inst['BYZ_GSM'])
        assert np.all(test_diff < 1.0e-8)
        return

    def test_yz_plane_cv(self):
        """Test the IMF steadiness CV calculation."""

        # Run the clock angle and steadiness routines
        omni.calculate_clock_angle(self.test_inst)
        omni.calculate_imf_steadiness(self.test_inst, steady_window=5,
                                      min_window_frac=0.8)

        # Ensure the BYZ coefficient of variation is calculated correctly
        byz_cv = np.array([np.nan, 0.158620, 0.229267, 0.239404, 0.469371,
                           0.470944, 0.495892, 0.384522, 0.396275, 0.208209,
                           0.221267, np.nan])

        # Test the difference
        test_diff = abs(byz_cv - self.test_inst['BYZ_CV'])

        assert test_diff[np.isnan(test_diff)].shape[0] == 2
        assert np.all(test_diff[~np.isnan(test_diff)] < 1.0e-6)
        assert np.all(np.isnan(self.test_inst['BYZ_CV']) == np.isnan(byz_cv))
        return

    def test_clock_angle_std(self):
        """Test the IMF steadiness standard deviation calculation."""

        # Run the clock angle and steadiness routines
        omni.calculate_clock_angle(self.test_inst)
        omni.calculate_imf_steadiness(self.test_inst, steady_window=5,
                                      min_window_frac=0.8)

        # Ensure the BYZ coefficient of variation is calculated correctly
        ca_std = np.array([np.nan, 13.317200, 14.429278, 27.278579,
                           27.468469, 25.500730, 27.673033, 27.512069,
                           19.043833, 26.616713, 29.250390, np.nan])

        # Test the difference
        test_diff = abs(ca_std - self.test_inst['clock_angle_std'])

        assert test_diff[np.isnan(test_diff)].shape[0] == 2
        assert np.all(test_diff[~np.isnan(test_diff)] < 1.0e-6)
        assert np.all(np.isnan(self.test_inst['clock_angle_std'])
                      == np.isnan(ca_std))
        return

    def test_dayside_recon(self):
        """Test the dayside reconnection calculation."""

        # Run the clock angle and steadiness routines
        omni.calculate_clock_angle(self.test_inst)
        omni.calculate_dayside_reconnection(self.test_inst)

        # Ensure the BYZ coefficient of variation is calculated correctly
        rcon = np.array([698.297487, 80.233896, 3.033586, 2.216075,
                         1425.310083, 486.460306, 2.350339, 103.843722,
                         0.000720, 534.586320, 1464.596772, 388.974792])

        # Test the difference
        test_diff = abs(rcon - self.test_inst['recon_day'])

        assert test_diff.shape[0] == 12
        assert np.all(test_diff < 1.0e-6)
        return

    def test_time_shift_to_magnetic_poles(self):
        """Test the time shift routines."""

        # Choose values to result in 1 hour shift
        self.test_inst['Vx'] = 6371.2
        self.test_inst['BSN_x'] = 3600.0

        old_index = self.test_inst.index.copy()
        omni.time_shift_to_magnetic_poles(self.test_inst)

        # Check shifted index
        assert (old_index[0] - self.test_inst.index[0]).seconds == 3600
        # Check new cadence
        assert (self.test_inst.index[1] - self.test_inst.index[0]).seconds == 60
        return


class TestDeprecation(object):
    """Unit tests for deprecation warnings in `pysat.instrument.omni_hro`."""

    def setup_method(self):
        """Set up the unit test environment for each method."""

        # Use an empty instrument to test redirect
        self.test_inst = pysat.Instrument()

        warnings.simplefilter("always", DeprecationWarning)

        return

    def teardown_method(self):
        """Clean up test environment after each method."""

        del self.test_inst

        return

    @pytest.mark.parametrize(
        "func_name, kvar", [("calculate_clock_angle", "BY_GSM"),
                            ("time_shift_to_magnetic_poles", "Vx"),
                            ("calculate_imf_steadiness", "BYZ_GSM"),
                            ("calculate_dayside_reconnection", "clock_angle")])
    def test_deprecation(self, func_name, kvar):
        """Test that running moved functions will give DeprecationWarning.

        Parameters
        ----------
        func_name : str
            Name of function that is deprecated.
        kvar : str
            Name of key error that should be raised if the correct function is
            redirected for an empty instrument.

        """

        func = getattr(depr_omni, func_name)
        with warnings.catch_warnings(record=True) as war:
            try:
                # Using an empty instrument produces a KeyError after the
                # warning is generated.
                func(self.test_inst)
            except KeyError as kerr:
                if kvar not in str(kerr):
                    # If an unexpected error occurs, raise it
                    raise kerr

        warn_msgs = ["{:} has been moved to".format(func_name)]

        pysat.utils.testing.eval_warnings(war, warn_msgs)

        return
