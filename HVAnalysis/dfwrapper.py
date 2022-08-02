import logging
import pandas as pd
from functools import cached_property


class HeinzWrapper:
    """Wrapper class for pandas data frame"""
    def __init__(self, file_names=None, val_name=None):
        self.file_names = file_names
        self.val_name = val_name

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

    def _join_wrapper(self, wrapper_1):
        dfall = pd.merge(self.data_frame, wrapper_1.data_frame, on=['timestamp'], how='left')
        dfall = self._get_modified_data_frame(dfall)
        return dfall

    def resample_value(self, resample_rate):
        res = self.data_frame.resample(resample_rate)[self.val_name].sum()
        return pd.Series.to_frame(res).rename(columns={self.val_name: 'sum'+self.val_name})

    def resample_count(self, resample_rate):
        res = self.data_frame.resample(resample_rate)[self.val_name].count()
        return pd.Series.to_frame(res).rename(columns={self.val_name: 'n'+self.val_name})


class ResistanceWrapper:
    """Wrapper class for resistance data frame. made from volt and curr wrappers"""
    def __init__(self, volt_wrapper, curr_wrapper, resample_rate='S'):
        self.volt_wrapper = volt_wrapper
        self.curr_wrapper = curr_wrapper
        self.resample_rate = resample_rate

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


'''class Voltage_CurrentWrapper:
    """Wrapper class for voltage and current in one data frame. made from volt and curr wrappers"""
    def __init__(self, volt_wrapper, curr_wrapper):
        self.volt_wrapper = volt_wrapper
        self.curr_wrapper = curr_wrapper

    def _connect_data_frames(self):
        dfs = []
        for wrapper in [self.volt_wrapper, self.curr_wrapper]:
            dfs.append(wrapper.self.volt_wrapper)
            dfs.append(wrapper.self.curr_wrapper)
        return dfs
        '''
