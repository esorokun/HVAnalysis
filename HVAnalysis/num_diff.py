import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

import conf
from dfwrapper import HeinzWrapper, ResistanceWrapper
from ML import MLDataFrame
sigma_v = 14.14158
sigma_c = 1.16687

class NumDiff():
    def __init__(self, data_frame, name, seconds, sigma, rate):
        self.data_frame = data_frame
        self.seconds = seconds
        self.name = name
        self.angle = float(sigma/seconds)
        self.rate = rate

    def get_result_list(self):
        df = self._result_df()
        return df

    def get_filter_df(self):
        df = self._mean_filtering()
        return df

    def _create_work_df(self):
        new_df = self.data_frame.copy()
        df = self.data_frame.copy()
        seconds = self.seconds

        new_df['datetime'] = new_df.index
        new_df = new_df.reset_index()
        new_df['num'] = new_df.index

        new_df = new_df.loc[new_df['num'] % seconds == 0]
        new_df = new_df.drop([0])

        datelist = new_df['datetime']

        new_df = new_df.set_index('datetime')
        df = df.join(new_df[['num']])
        df = df.ffill(axis=0)
        df = df.bfill(axis=0)
        df['datetime'] = df.index
        self.work_df = df
        return datelist

    def _mean_filtering(self):
        name = self.name
        datelist = self._create_work_df()
        df = self.work_df
        seconds = self.seconds
        rate = self.rate
        df = df.loc[np.abs(df[name]) < np.abs(df[name].shift(1) * (1 + rate))]
        df = df.loc[np.abs(df[name]) > np.abs(df[name].shift(1) * (1 - rate))]
        df = df.loc[np.abs(df[name]) < np.abs(df[name].shift(-1) * (1 + rate))]
        df = df.loc[np.abs(df[name]) > np.abs(df[name].shift(-1) * (1 - rate))]
        df = df.loc[np.abs(df[name]) < np.abs(df[name].shift(2*seconds) * (1 + rate))]
        df = df.loc[np.abs(df[name]) > np.abs(df[name].shift(2*seconds) * (1 - rate))]
        df = df.loc[np.abs(df[name]) < np.abs(df[name].shift(-2*seconds) * (1 + rate))]
        df = df.loc[np.abs(df[name]) > np.abs(df[name].shift(-2*seconds) * (1 - rate))]
        new_df = df.groupby(['num']).mean()
        new_df['var'] = df.groupby(['num']).var()
        new_df = new_df.join(datelist)
        return new_df

    def _checker(self):
        new_df = self._mean_filtering()
        name = self.name
        seconds = self.seconds

        new_df['checker_left'] = np.abs((new_df[name].shift(-1) - new_df[name]) / seconds)
        new_df['checker_right'] = np.abs((new_df[name].shift(1) - new_df[name]) / seconds)
        new_df['checker'] = (np.abs(new_df['checker_left']) + np.abs(new_df['checker_right'])) / 2
        new_df = new_df.set_index('datetime')
        return new_df

    def _result_value(self):
        df = self.data_frame.copy()
        new_df = self._checker()
        name = self.name
        angle = self.angle
        rate = self.rate
        seconds = self.seconds

        df = df.join(new_df[['checker']])
        new_df = new_df.rename(columns={name: "meanvalue"})
        df = df.join(new_df[['meanvalue']])
        df = df.ffill(axis=0)
        df = df.bfill(axis=0)
        print(df)
        df.loc[np.abs(df['checker']) < angle, 'result_value'] = 0
        df.loc[df['result_value'] != 0, 'result_value'] = 1
        df.loc[np.abs(df[name]) > np.abs(df['meanvalue'] * (1 + rate / 2)), 'result_value'] = 1
        df.loc[np.abs(df[name]) < np.abs(df['meanvalue'] * (1 - rate / 2)), 'result_value'] = 1
        interval = seconds
        df.loc[
            (df['result_value'].shift(interval) == 0) &
            (df['result_value'] == 1) &
            np.abs(df[name]/df['meanvalue'].shift(interval) < (1 + rate/3)) &
            np.abs(df[name]/df['meanvalue'].shift(interval) > (1 - rate/3))
            , 'result_value'] = 0
        df.loc[
            (df['result_value'].shift(-interval) == 0) &
            (df['result_value'] == 1) &
            np.abs(df[name] / df['meanvalue'].shift(-interval) < (1 + rate/3)) &
            np.abs(df[name] / df['meanvalue'].shift(-interval) > (1 - rate/3))
            , 'result_value'] = 0
        df.loc[np.abs(df[name].shift(-5)-df[name].shift(5)) > df[name]*0.1, 'result_value'] = 1
        return df

    def _result_df(self):
        df = self._result_value()
        df.loc[df['result_value'] == 1, 'result'] = 1
        df.loc[df['result'] != 1, 'result'] = 0
        df['datetime'] = df.index
        return df

    def show_plot(self):
        name = self.name
        df = self._result_df()

        length = int(len(df))
        unstable = int(df['result_value'].sum())
        perc = np.round(unstable / length, 2)
        print("unstable: " + str(perc) + "%\n" + "stable:   " + str(100 - perc) + "%")
        df['datetime'] = df.index
        sns.scatterplot(x='datetime', y=name, data=df, alpha=1, s=5, hue='result')
        plt.show()


class CurrNumDiff(NumDiff):
    def __init__(self, data_frame, name='avgcurr', seconds=3600, sigma=1.16687, rate=0.04):
        super().__init__(data_frame, name, seconds, sigma, rate)

    def _result_df(self):
        df = self._result_value()
        name = self.name
        df.loc[df['result_value'] == 1, 'result'] = 1
        df.loc[df['result'] != 1, 'result'] = 0
        df.loc[df[name] < 10, 'result'] = 1
        df['datetime'] = df.index
        return df

class VoltNumDiff(NumDiff):
    def __init__(self, data_frame, name='avgvolt'):
        super().__init__(data_frame, name, seconds=2400, sigma=14.14158, rate=0.05)

    def _result_df(self):
        df = self._result_value()
        name = self.name
        df.loc[df['result_value'] == 1, 'result'] = 1
        df.loc[df['result'] != 1, 'result'] = 0
        df.loc[df[name] < 1000, 'result'] = 1
        df['datetime'] = df.index
        return df

class ResNumDiff(NumDiff):
    def __init__(self, data_frame):
        super().__init__(data_frame, name='binresistance', seconds=120, sigma=0.012, rate=0.05)

    def _result_df(self):
        df = self._result_value()
        df.loc[df['binresistance'] < -1, 'result'] = 1
        df.loc[df['result_value'] == 1, 'result'] = 1
        df.loc[df['result'] != 1, 'result'] = 0
        df['datetime'] = df.index
        return df

    def show_plot(self):
        name = self.name
        df = self._result_df()

        length = int(len(df))
        unstable = int(df['result_value'].sum())
        perc = np.round(unstable / length, 2)
        print("unstable: " + str(perc) + "%\n" + "stable:   " + str(100 - perc) + "%")
        df['datetime'] = df.index
        sns.jointplot(x='datetime', y=name, data=df, alpha=1, s=5, hue='result')
        plt.show()