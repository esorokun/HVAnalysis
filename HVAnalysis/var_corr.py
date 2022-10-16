import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

class VarCorr():
    def __init__(self, data_frame, name, seconds):
        self.data_frame = data_frame
        self.seconds = seconds
        self.name = name
        self.rate = 0.05

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

    def mean_filtering(self):
        name = self.name
        datelist = self._create_work_df()
        df = self.work_df
        seconds = self.seconds
        rate = self.rate
        # df = df.loc[np.abs(df[name]) < np.abs(df[name].shift(1) * (1 + rate))]
        # df = df.loc[np.abs(df[name]) > np.abs(df[name].shift(1) * (1 - rate))]
        # df = df.loc[np.abs(df[name]) < np.abs(df[name].shift(-1) * (1 + rate))]
        # df = df.loc[np.abs(df[name]) > np.abs(df[name].shift(-1) * (1 - rate))]
        # df = df.loc[np.abs(df[name]) < np.abs(df[name].shift(2*seconds) * (1 + rate))]
        # df = df.loc[np.abs(df[name]) > np.abs(df[name].shift(2*seconds) * (1 - rate))]
        # df = df.loc[np.abs(df[name]) < np.abs(df[name].shift(-2*seconds) * (1 + rate))]
        # df = df.loc[np.abs(df[name]) > np.abs(df[name].shift(-2*seconds) * (1 - rate))]
        new_df = df.groupby(['num']).mean()
        new_df['var'] = df.groupby(['num']).var()
        new_df = new_df.join(datelist)
        return new_df
    #
    # def _checker(self):
    #     new_df = self._mean_filtering()
    #     name = self.name
    #     seconds = self.seconds
    #
    #     new_df['checker_left'] = np.abs((new_df[name].shift(-1) - new_df[name]) / seconds)
    #     new_df['checker_right'] = np.abs((new_df[name].shift(1) - new_df[name]) / seconds)
    #     new_df['checker'] = (np.abs(new_df['checker_left']) + np.abs(new_df['checker_right'])) / 2
    #     new_df = new_df.set_index('datetime')
    #     return new_df
    #
    # def _result_value(self):
    #     df = self.data_frame.copy()
    #     new_df = self._checker()
    #     name = self.name
    #     angle = self.angle
    #     rate = self.rate
    #     seconds = self.seconds
    #
    #     df = df.join(new_df[['checker']])
    #     new_df = new_df.rename(columns={name: "meanvalue"})
    #     df = df.join(new_df[['meanvalue']])
    #     df = df.ffill(axis=0)
    #     df = df.bfill(axis=0)
    #     print(df)
    #     df.loc[np.abs(df['checker']) < angle, 'result_value'] = 0
    #     df.loc[df['result_value'] != 0, 'result_value'] = 1
    #     df.loc[np.abs(df[name]) > np.abs(df['meanvalue'] * (1 + rate / 2)), 'result_value'] = 1
    #     df.loc[np.abs(df[name]) < np.abs(df['meanvalue'] * (1 - rate / 2)), 'result_value'] = 1
    #     interval = seconds
    #     df.loc[
    #         (df['result_value'].shift(interval) == 0) &
    #         (df['result_value'] == 1) &
    #         np.abs(df[name]/df['meanvalue'].shift(interval) < (1 + rate/3)) &
    #         np.abs(df[name]/df['meanvalue'].shift(interval) > (1 - rate/3))
    #         , 'result_value'] = 0
    #     df.loc[
    #         (df['result_value'].shift(-interval) == 0) &
    #         (df['result_value'] == 1) &
    #         np.abs(df[name] / df['meanvalue'].shift(-interval) < (1 + rate/3)) &
    #         np.abs(df[name] / df['meanvalue'].shift(-interval) > (1 - rate/3))
    #         , 'result_value'] = 0
    #     df.loc[np.abs(df[name].shift(-5)-df[name].shift(5)) > df[name]*0.1, 'result_value'] = 1
    #     return df
    #
    # def _result_df(self):
    #     df = self._result_value()
    #     df.loc[df['result_value'] == 1, 'result'] = 1
    #     df.loc[df['result'] != 1, 'result'] = 0
    #     df['datetime'] = df.index
    #     return df
    #
    # def show_plot(self):
    #     name = self.name
    #     df = self._result_df()
    #
    #     length = int(len(df))
    #     unstable = int(df['result_value'].sum())
    #     perc = np.round(unstable / length, 2)
    #     print("unstable: " + str(perc) + "%\n" + "stable:   " + str(100 - perc) + "%")
    #     df['datetime'] = df.index
    #     sns.scatterplot(x='datetime', y=name, data=df, alpha=1, s=5, hue='result')
    #     plt.show()

class Poly1d():
    def __init__(self, data_frame, name, points, height):
        self.data_frame = data_frame
        self.name = name
        self.points = points
        self.height = height

    def _clear_df(self, df):
        del df['ncurr']
        del df['nvolt']
        del df['sumvolt']
        del df['sumcurr']
        del df['stable_original']
        self.data_frame = df
        return self.data_frame

    def _create_df(self):
        df = self.data_frame.copy()
        points = self.points
        df['timeset'] = (df.index.astype('uint64') / 1_000_000_000).astype(np.int64)
        df1 = df.copy()

        df1['datetime'] = df1.index
        df1 = df1.reset_index()
        df1['num'] = df1.index
        df1 = df1.loc[df1['num'] % points == 0]
        df1 = df1.drop([0])
        self.date1 = df1['datetime']
        df1 = df1.set_index('datetime')

        df['datetime'] = df.index
        df = df.join(df1[['num']])
        df = df.ffill(axis=0)
        df = df.bfill(axis=0)
        df['datetime'] = df.index
        print(df)
        return df

    def mean_filtering(self):
        df = self._create_df()
        name = self.name
        points = self.points
        df_l = pd.DataFrame({'num': df['num'], 'meanvalue': df[name]})
        df_l = df_l.groupby('num').mean()
        print(df_l)
        res = df.groupby('num').apply(lambda x: pd.Series(np.polyfit(x.timeset, x.avgcurr, 1), index=['slope', 'intercept']))
        timedelta = df.groupby('num').sum('timedelta')
        res = res.join(self.date1)
        res = res.join(timedelta)
        res = res.join(df_l)
        res = res.rename(columns={'timedelta': 'timedelta_sum'})
        res = res.set_index('datetime')
        res['height'] = np.abs(res['slope']*res['timedelta_sum'])
        df = df.join(res[['height', 'meanvalue']])
        df = df.ffill(axis=0)
        df = df.bfill(axis=0)
        print(df)
        df.loc[df['height'] < self.height, 'result'] = 0
        df.loc[df['result'] != 0, 'result'] = 1
        # df.loc[(df['result'].shift(points) == 0) & (df['result'] == 1) &
        #        (np.abs(df[name] - df['meanvalue'].shift(points) < 2*1.16687)), 'result'] = 0
        # df.loc[(df['result'].shift(-points) == 0) & (df['result'] == 1) &
        #        (np.abs(df[name] - df['meanvalue'].shift(-points)) < 2*1.16687), 'result'] = 0
        # df.loc[(df['result'] == 0) & (np.abs(df[name] - df['meanvalue']) > 2 * 1.16687), 'result'] = 1
        return df

    def show_result(self):
        df = self.mean_filtering()
        name = self.name
        sns.scatterplot(data=df, x='datetime', y=name, alpha=1, s=5, hue='result')
        plt.show()