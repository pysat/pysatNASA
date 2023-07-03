"""Unit tests for the cdaweb instrument methods."""

import datetime as dt
import pandas as pds
import requests

import pytest

import pysat
import pysatNASA
from pysatNASA.instruments.methods import cdaweb as cdw


class TestCDAWeb(object):
    """Unit tests for `pysat.instrument.methods.cdaweb`."""

    def setup_method(self):
        """Set up the unit test environment for each method."""

        self.download_tags = pysatNASA.instruments.timed_guvi.download_tags
        self.kwargs = {'tag': None, 'inst_id': None}
        self.saved_path = pysat.params['data_dirs']
        return

    def teardown_method(self):
        """Clean up the unit test environment after each method."""

        del self.download_tags, self.kwargs
        return

    def test_remote_file_list_connection_error_append(self):
        """Test that suggested help is appended to ConnectionError."""

        with pytest.raises(Exception) as excinfo:
            # Giving a bad remote_site address yields similar ConnectionError
            cdw.list_remote_files(tag='sdr-imaging', inst_id='high_res',
                                  supported_tags=self.download_tags,
                                  remote_url='https://bad/path')

        assert excinfo.type is requests.exceptions.ConnectionError
        # Check that pysat appends the message
        assert str(excinfo.value).find('pysat -> Request potentially') > 0
        return

    def test_load_with_empty_file_list(self):
        """Test that empty data is returned if no files are requested."""

        data, meta = cdw.load(fnames=[])
        assert len(data) == 0
        assert meta is None
        return

    @pytest.mark.parametrize("bad_key,bad_val,err_msg",
                             [("tag", "badval", "inst_id / tag combo unknown."),
                              ("inst_id", "badval",
                               "inst_id / tag combo unknown.")])
    def test_bad_kwarg_download(self, bad_key, bad_val, err_msg):
        """Test that bad kwargs raise correct errors in download."""

        date_array = [dt.datetime(2019, 1, 1)]
        self.kwargs[bad_key] = bad_val
        with pytest.raises(ValueError) as excinfo:
            cdw.download(supported_tags=self.download_tags,
                         date_array=date_array,
                         data_path=self.saved_path,
                         tag=self.kwargs['tag'],
                         inst_id=self.kwargs['inst_id'])
        assert str(excinfo.value).find(err_msg) >= 0
        return

    @pytest.mark.parametrize("bad_key,bad_val,err_msg",
                             [("tag", "badval", "inst_id / tag combo unknown."),
                              ("inst_id", "badval",
                               "inst_id / tag combo unknown.")])
    def test_bad_kwarg_list_remote_files(self, bad_key, bad_val, err_msg):
        """Test that bad kwargs raise correct errors in list_remote_files."""

        self.kwargs[bad_key] = bad_val
        with pytest.raises(ValueError) as excinfo:
            cdw.list_remote_files(supported_tags=self.download_tags,
                                  tag=self.kwargs['tag'],
                                  inst_id=self.kwargs['inst_id'])
        assert str(excinfo.value).find(err_msg) >= 0
        return

    @pytest.mark.parametrize("start, stop",
                             [(None, None),
                              (dt.datetime(2009, 1, 1), None),
                              (dt.datetime(2009, 1, 1),
                               dt.datetime(2009, 1, 1)),
                              (pds.Timestamp(2009, 1, 1),
                               pds.Timestamp(2009, 1, 2))])
    def test_remote_file_list_all(self, start, stop):
        """Test that remote_file_list works for all start and stop cases."""

        self.module = pysatNASA.instruments.cnofs_plp
        self.test_inst = pysat.Instrument(inst_module=self.module)
        files = self.test_inst.remote_file_list(start, stop)
        assert len(files) > 0
        return

    @pytest.mark.parametrize("series_out", [(True), (False)])
    def test_cdas_remote_files(self, series_out):
        """Test that cdas_list_remote_files can return pandas series."""
        start = dt.datetime(2009, 1, 1)
        stop = dt.datetime(2009, 1, 2)
        self.module = pysatNASA.instruments.cnofs_plp
        self.test_inst = pysat.Instrument(inst_module=self.module)
        files = self.test_inst.remote_file_list(start, stop,
                                                series_out=series_out)
        if series_out is True:
            assert isinstance(files, pds.Series)
        else:
            assert isinstance(files, list)
        return
