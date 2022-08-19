import pytest
import tempfile
from datetime import datetime, timedelta
from HVAnalysis.periods import UnstablePeriods
from HVAnalysis.dfwrapper import HeinzWrapper, ResistanceWrapper
from HVAnalysis import conf


@pytest.fixture(autouse=True)
def configure_from_args():
    class TestArgs:
        datelist = ['2018-09-25']
        loglvl = 0
        outputfolder = 'test_output'
    conf.configure_from_args(TestArgs)

@pytest.fixture
def curr_wrapper():
    return HeinzWrapper(conf.curr_file_names, 'curr')

@pytest.fixture
def volt_wrapper():
    return HeinzWrapper(conf.volt_file_names, 'curr')

@pytest.fixture
def comb_wrapper(curr_wrapper, volt_wrapper):
    return ResistanceWrapper(curr_wrapper, volt_wrapper)

@pytest.fixture
def my_periods():
    my_periods = UnstablePeriods()
    my_periods.append([datetime(2018, 1, 1),
                       datetime(2018, 1, 2)])
    return my_periods
