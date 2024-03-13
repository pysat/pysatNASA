"""Unit tests for the JHU APL instrument methods."""

import numpy as np
import pandas as pds

import pytest

import pysat
from pysatNASA.instruments.methods import jhuapl


class TestJHUAPL(object):
    """Unit tests for `pysat.instrument.methods.jhuapl`."""

    def setup_method(self):
        """Set up the unit test environment for each method."""

        self.test_inst = pysat.Instrument(
            inst_module=pysat.instruments.pysat_ndtesting)
        self.var_list = ["images", "variable_profiles"]
        self.out = None
        self.comp = None
        return

    def teardown_method(self):
        """Clean up the unit test environment after each method."""

        del self.test_inst, self.var_list, self.out, self.comp
        return

    def set_jhuapl(self):
        """Update the test instrument to have JHUAPL varialbes."""

        if self.test_inst.empty:
            self.test_inst.load(
                date=pysat.instruments.pysat_ndtesting._test_dates[''][''])

        # Create the common string for this time using `var`
        self.test_inst['YEAR{:s}'.format(self.var_list[0])] = np.full(
            shape=self.test_inst['time'].shape, fill_value=self.test_inst.yr)
        self.test_inst['DOY{:s}'.format(self.var_list[0])] = np.full(
            shape=self.test_inst['time'].shape, fill_value=self.test_inst.doy)
        self.test_inst['TIME{:s}'.format(self.var_list[0])] = self.test_inst[
            'uts']

        # Add DQI masks for the multi-dim data variables
        self.test_inst['DQI_Z'] = np.zeros(shape=(
            self.test_inst.data.sizes['time'], self.test_inst.data.sizes['z']))
        self.test_inst['DQI_X'] = np.zeros(shape=(
            self.test_inst.data.sizes['time'], self.test_inst.data.sizes['x']))

        # Set some bad values for the DQI data
        self.test_inst['DQI_Z'][:, 0] = 3
        self.test_inst['DQI_Z'][:, 1] = 2
        self.test_inst['DQI_Z'][:, 2] = 1
        self.test_inst['DQI_X'][:, 0] = 3
        self.test_inst['DQI_X'][:, 1] = 2
        self.test_inst['DQI_X'][:, 2] = 1

        return

    @pytest.mark.parametrize("epoch,epoch_var", [
        (None, 'time'),
        (pysat.instruments.pysat_ndtesting._test_dates[''][''], 'uts')])
    def test_build_dtimes(self, epoch, epoch_var):
        """Test creation of datetime list from JHU APL times.

        Parameters
        ----------
        epoch : dt.datetime or NoneType
            Epoch to subtract from data or NoneType to get seconds of day from
            `data`
        epoch_var : str
            Epoch variable containing time data that seconds of day will be
            obtained from if `epoch` != None

        """
        # Set up the test instrument with necessary times
        self.set_jhuapl()

        # Get the time list
        self.out = jhuapl.build_dtimes(self.test_inst.data, self.var_list[0],
                                       epoch=epoch, epoch_var=epoch_var)

        # Get the comparison from the Instrument index
        self.comp = [pds.to_datetime(tval).to_pydatetime()
                     for tval in self.test_inst.index]
        if epoch is not None:
            self.comp = [tval - epoch for tval in self.test_inst.index]

        # Ensure the lists are equal
        pysat.utils.testing.assert_lists_equal(self.out, self.comp)
        return

    @pytest.mark.parametrize("clean_level", ['clean', 'dusty', 'dirty', 'none'])
    def test_clean_by_dqi(self, clean_level):
        """Test creation of datetime list from JHU APL times.

        Parameters
        ----------
        clean_level : str
            String denoting desired clean level

        """
        # Set up the test instrument with necessary flag arrays
        self.set_jhuapl()

        # Update the clean level
        self.test_inst.clean_level = clean_level
        self.out = {'clean': 2, 'dusty': 1, 'dirty': 1}

        # Clean the data to the desired level
        jhuapl.clean_by_dqi(self.test_inst)

        # Test that there are fill values only in the appropriate variables and
        # places
        for var in self.test_inst.variables:
            # Get the fill value for this variable
            self.comp = self.test_inst.meta[
                var, self.test_inst.meta.labels.fill_val]

            if var in self.var_list and clean_level != 'none':
                # This variable will have been cleaned
                if np.isnan(self.comp):
                    assert np.isnan(
                        self.test_inst[var][:, self.out[
                            clean_level]].values).all()
                else:
                    assert np.all(
                        self.test_inst[var][:, self.out[clean_level]].values
                        == self.comp)
            else:
                # This variable should not have any fill values
                if np.isnan(self.comp):
                    assert np.isnan(self.test_inst[var].values).all()
                else:
                    assert np.all(self.test_inst[var].values == self.comp)
        return
