import logging
import pandas as pd
from datetime import datetime
from functools import cached_property
from HVAnalysis.periods import UnstablePeriods


class DataFrameWrapper:
    def __str__(self):
        return f"instance of {type(self).__name__} " \
               f"wrapping around following data frame\n" \
               f"{self.data_frame}"

    @property
    def data_frame(self):
        raise NotImplemented


class HeinzWrapper(DataFrameWrapper):
    """Wrapper class for pandas data frame"""
    def __init__(self, file_names=None, val_name=None):
        self.file_names = file_names
        self.val_name = val_name

    def add_marker_column(self, name):
        self.data_frame['marker'] = name
        return 0

    def _get_data_frame_from_file(self, fn):
        return pd.read_csv(fn, sep=' ', index_col=0, usecols=[0, 1],
                           names=['timestamp', self.val_name])

    def _get_modified_data_frame(self, df):
        df.index = 1000000 * df.index
        df['timestamp'] = pd.to_datetime(df.index)
        return df.set_index('timestamp')

    @cached_property
    def data_frame(self):
        df = pd.concat([self._get_data_frame_from_file(fn) for fn in self.file_names], axis=0)
        df = self._get_modified_data_frame(df)
        logging.info(f'HeinzWrapper.data_frame =\n{df}')
        return df

    def resample_value(self, resample_rate):
        res = self.data_frame.resample(resample_rate)[self.val_name].sum()
        return pd.Series.to_frame(res).rename(columns={self.val_name: 'sum' + self.val_name})

    def resample_count(self, resample_rate):
        res = self.data_frame.resample(resample_rate)[self.val_name].count()
        return pd.Series.to_frame(res).rename(columns={self.val_name: 'n' + self.val_name})


class ResistanceWrapper(DataFrameWrapper):
    """Wrapper class for resistance data frame. made from volt and curr wrappers"""
    def __init__(self, volt_wrapper, curr_wrapper, resample_rate='S'):
        self.volt_wrapper = volt_wrapper
        self.curr_wrapper = curr_wrapper
        self.resample_rate = resample_rate
        self._check_input_wrappers()

    def _check_input_wrappers(self):
        vn = self.volt_wrapper.val_name
        cn = self.curr_wrapper.val_name
        if not (vn == 'volt' and cn == 'curr'):
            raise Exception("The input wrappers must have values"
                            "'curr' and 'volt', respectively")

    def _get_data_frames(self):
        dfs = []
        for wrapper in [self.volt_wrapper, self.curr_wrapper]:
            dfs.append(wrapper.resample_value(self.resample_rate))
            dfs.append(wrapper.resample_count(self.resample_rate))
        return dfs

    def _get_modified_data_frame(self, df):
        df = self._decorate_averages(df)
        return df

    def _decorate_averages(self, df):
        df['avgcurr'] = df['sumcurr'] / df['ncurr']
        df['avgvolt'] = df['sumvolt'] / df['nvolt']
        df['resistance'] = df['avgvolt'] / df['avgcurr']
        return df

    @cached_property
    def data_frame(self):
        df = pd.concat(self._get_data_frames(), axis=1)
        df = self._get_modified_data_frame(df)
        logging.info(f'ResistanceWrapper.data_frame =\n{df}')
        return df

#    def decorate_stable_original(self):


    def get_unstable_periods_original(self) -> UnstablePeriods:
        df = self.data_frame

        # for some reason, the original periods start at 2018-09-19 02:00:16
        first_date = datetime(2018, 9, 19, 0, 0, 0)
        b1 = datetime(2018, 10, 5, 0, 0, 0)    #2018-10-05 00:00:00
        b2 = datetime(2018, 10, 17, 12, 0, 0)  #2018-10-17 12:00:00
        streamer_on = False
        unstable_periods = UnstablePeriods()

        for row in df.itertuples():
            if row.ncurr == 0 or row.nvolt == 0:
                continue

            if row.Index < first_date:
                continue

            b = row.Index
            r = row.resistance
            vps = row.avgvolt

            if b <= b1 and (r > 1472 or r < 1452 or vps < 120000.) and not streamer_on:
                streamer_on = True
                start_stream = b

            if b <= b1 and (r > 1452 and r < 1472 and vps > 120000.) and streamer_on:
                streamer_on = False
                unstable_periods.append([start_stream, b])

            if b1 < b < b2 and (r < 1465 or vps < 120000.) and not streamer_on:
                streamer_on = True
                start_stream = b

            if b1 < b < b2 and (r > 1465 and vps > 120000.) and streamer_on:
                streamer_on = False
                unstable_periods.append([start_stream, b])

            if b >= b2 and (r < 1465 or vps < 180000.) and not streamer_on:
                streamer_on = True
                start_stream = b

            if b >= b2 and (r > 1465 and vps > 180000.) and streamer_on:
                streamer_on = False
                unstable_periods.append([start_stream, b])

        # write the last unstable period
        if streamer_on:
            end_time = datetime(b.year, b.month, b.day+1, 1, 0, 59)
            unstable_periods.append([start_stream, end_time])

        return unstable_periods


