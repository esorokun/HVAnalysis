from HVAnalysis.dfwrapper import ResistanceWrapper
import tempfile
import os
import pytest


def test_unstable_periods_seconds(my_periods):
    u_s = my_periods.get_unstable_seconds()
    assert len(u_s) == 60*60*24


def test_unstable_periods_writing(my_periods):
    fd, path = tempfile.mkstemp()
    my_periods.write_to_file(path)
    os.close(fd)
    os.unlink(path)


def test_wrong_df_wrapper(volt_wrapper, curr_wrapper):
    with pytest.raises(Exception):
        ResistanceWrapper(curr_wrapper, volt_wrapper)


def test_df_wrapper(comb_wrapper):
    periods = comb_wrapper.get_unstable_periods('stable_original')
    periods.write_to_file('latest_periods.csv')


def test_overlap(comb_wrapper):
    periods = comb_wrapper.get_unstable_periods('stable_original')
    assert not periods.has_overlap()


def test_remove_overlap(overlapping_periods):
    old_seconds = overlapping_periods.get_unstable_seconds()
    assert overlapping_periods.has_overlap()
    overlapping_periods.remove_overlap()
    assert not overlapping_periods.has_overlap()
    assert old_seconds == overlapping_periods.get_unstable_seconds()
