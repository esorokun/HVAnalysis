import pytest
import tempfile
import random
from datetime import datetime, timedelta
from HVAnalysis.periods import UnstablePeriods
from HVAnalysis.dfwrapper import HeinzWrapper, ResistanceWrapper
from HVAnalysis import conf


@pytest.fixture(autouse=True)
def configure_from_args():
    class TestArgs:
        datelist = ['2018-09-25', '2018-09-26', '2018-09-27']# None
        loglvl = 0
        outputfolder = 'test_output'
    conf.configure_from_args(TestArgs)

@pytest.fixture
def curr_wrapper():
    return HeinzWrapper(conf.curr_file_names, 'curr')

@pytest.fixture
def volt_wrapper():
    return HeinzWrapper(conf.volt_file_names, 'volt')

@pytest.fixture
def comb_wrapper(curr_wrapper, volt_wrapper):
    return ResistanceWrapper(volt_wrapper, curr_wrapper)

@pytest.fixture
def my_periods():
    my_periods = UnstablePeriods()
    my_periods.append([datetime(2018, 1, 1),
                       datetime(2018, 1, 2)])
    return my_periods

@pytest.fixture
def overlapping_periods():
    periods_ = UnstablePeriods()
    n = 10
    begin_ts = [random.randint(0, 1000) for i in range(n)]
    begin_ts.sort()
    end_ts = [b_ts + random.randint(0, 1000) for b_ts in begin_ts]
    end_ts.sort()
    for i in range(n):
        p = [datetime.fromtimestamp(begin_ts[i]), datetime.fromtimestamp(end_ts[i])]
#        p = [begin_ts[i], end_ts[i]]
        periods_.append(p)
    return periods_
