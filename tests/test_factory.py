from HVAnalysis import conf
from HVAnalysis.dfwrapper import ResistanceWrapper
import tempfile
import os
import pytest


#def test_conf():
#    assert len(conf.curr_file_names) == 1


def test_unstable_periods_seconds(my_periods):
    print('test_unstable_periods_seconds()')
    u_s = my_periods.get_unstable_seconds()
    assert len(u_s) == 60*60*24


def test_unstable_periods_writing(my_periods):
    print('test_unstable_periods_writing()')
    fd, path = tempfile.mkstemp()
    my_periods.write_to_file(path)
    os.close(fd)
    os.unlink(path)


def test_wrong_df_wrapper(volt_wrapper, curr_wrapper):
    print('test_wrong_df_wrapper()')
    with pytest.raises(Exception):
        ResistanceWrapper(curr_wrapper, volt_wrapper)


def test_df_wrapper(comb_wrapper):
    print('test_df_wrapper()')
    periods = comb_wrapper.get_unstable_periods('stable_original')
    periods.write_to_file('latest_periods.csv')
    print(f'periods = {periods}')


#def test_overlap_removal():
#    overlapping_periods = ernests_writer.write_unstable_periods()
#    clean_periods = ernests_writer.write_unstable_not_overlapping_periods()
#    assert overlapping_periods == clean_periods
