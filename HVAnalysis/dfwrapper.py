import logging
import pandas as pd
from datetime import datetime
import numpy as np
from functools import cached_property
from periods import UnstablePeriods


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
        df = self._decorate_stable_original(df)
        return df

    def _decorate_averages(self, df):
        #df = df.replace(0, np.nan)
        df = df.ffill(axis=0)
        df['avgcurr'] = df['sumcurr'] / df['ncurr']
        df['avgvolt'] = df['sumvolt'] / df['nvolt']
        df['resistance'] = df['avgvolt'] / df['avgcurr']
        #df = df[~df['resistance'].isnull()]
        return df

    @cached_property
    def data_frame(self):
        df = pd.concat(self._get_data_frames(), axis=1)
        df = self._get_modified_data_frame(df)
        logging.info(f'ResistanceWrapper.data_frame =\n{df}')
        return df

    def _decorate_stable_original(self, df):
        start_ts, end_ts = [pd.to_datetime("2018-10-05 00:00:00"), pd.to_datetime("2018-10-17 12:00:00")]
        #df.loc[df.index <= start_ts, 'stable_original'] = (df.loc[df.index <= start_ts, 'resistance'] > 1452) * (df.loc[df.index <= start_ts, 'resistance'] < 1472) * (df.loc[df.index <= start_ts, 'avgvolt'] > 120000)
        #df.loc[(df.index > start_ts) * (df.index < end_ts), 'stable_original'] = (df.loc[(df.index > start_ts) * (df.index < end_ts), 'resistance'] > 1465) * (df.loc[(df.index > start_ts) * (df.index < end_ts), 'avgvolt'] > 120000)
        #df.loc[df.index >= end_ts, 'stable_original'] = (df.loc[df.index >= end_ts, 'resistance'] > 1465) * (df.loc[df.index >= end_ts, 'avgvolt'] > 180000)
        #return df
        b_df = df.loc[df.index <= start_ts]
        d_df = df.loc[(df.index > start_ts) * (df.index < end_ts)]
        a_df = df.loc[(df.index >= end_ts)]
        b_df['stable_original'] = (b_df['resistance'] > 1452) * (b_df['resistance'] < 1472) * (b_df['avgvolt'] > 120000)
        d_df['stable_original'] = (d_df['resistance'] > 1465) * (d_df['avgvolt'] > 120000)
        a_df['stable_original'] = (a_df['resistance'] > 1465) * (a_df['avgvolt'] > 180000)
        return pd.concat([b_df, d_df, a_df], axis=0)

    def get_unstable_periods(self, column_name) -> UnstablePeriods:
        df = self.data_frame
        begin = df.index[0]
        was_stable = df.loc[begin, column_name]
        unstable_periods = UnstablePeriods()
        for idx in df.index:
            is_stable = df.loc[idx, column_name]
            if was_stable:
                if not is_stable:
                    was_stable = False
                    begin = idx
            else:
                if is_stable:
                    was_stable = True
                    unstable_periods.append([begin, idx])
        return unstable_periods
