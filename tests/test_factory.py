from HVAnalysis import conf
from HVAnalysis.dfwrapper import ResistanceWrapper
from HVAnalysis import periods
import datetime
import tempfile
import os
import pytest


def test_conf():
    assert len(conf.curr_file_names) == 1


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
#    comb_wrapper.decorate_stable_original()
    periods = comb_wrapper.get_unstable_periods('stable_original')
    print(f'periods = {periods}')

    #assert linos_writer.get_unstable_periods() == ernests_writer.get_unstable_periods()


#def test_overlap_removal():
#    overlapping_periods = ernests_writer.write_unstable_periods()
#    clean_periods = ernests_writer.write_unstable_not_overlapping_periods()
#    assert overlapping_periods == clean_periods
