import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


class Timedelta():
    def __init__(self, data_frame):
        self.data_frame = data_frame
        self.transformed_df = self._restructure_df()

    def _restructure_df(self):
        df = self.data_frame.copy()
        df = df.loc[(df['nvolt'] != 0) & (df['ncurr'] != 0)]
        df_c =df.copy()
        df['unixtime'] = (df.index.astype('uint64') / 1_000_000_000).astype(np.int64)
        df['unixtime_next'] = df['unixtime'].shift(+1)
        df = df.bfill(axis=0)
        df_c['timedelta'] = df['unixtime'] - df['unixtime_next']
        self.transformed_df = df_c
        return df_c


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
        return df

    def show_result(self):
        df = self.mean_filtering()
        name = self.name
        sns.scatterplot(data=df, x='datetime', y=name, alpha=1, s=5, hue='result')
        plt.show()


class Volt_Filter():
    def __init__(self, data_frame, points):
        self.data_frame = data_frame
        self.points = points
        self.unstable_periods = None

    def make_init(self):
        numbers = self.points
        num_1 = round(numbers / 4)
        num_2 = round(numbers / 2)
        num_3 = round(numbers)
        num_4 = round(numbers * 2)
        poly1 = Poly1d(self.data_frame, 'avgvolt', num_1, 141.4158)
        poly2 = Poly1d(self.data_frame, 'avgvolt', num_2, 141.4158)
        poly3 = Poly1d(self.data_frame, 'avgvolt', num_3, 141.4158)
        poly4 = Poly1d(self.data_frame, 'avgvolt', num_4, 141.4158)

        df1 = poly1.mean_filtering()
        df2 = poly2.mean_filtering()
        df3 = poly3.mean_filtering()
        df4 = poly4.mean_filtering()

        df_values = pd.DataFrame({'var_1': df1['height'], 'var_2': df2['height'],
                               'var_3': df3['height'], 'var_4': df4['height'],
                               'mean_1': df1['meanvalue'], 'mean_2': df2['meanvalue'],
                               'mean_3': df3['meanvalue'], 'mean_4': df4['meanvalue']})
        return df_values

    def meaning(self):
        df_values = self.make_init()
        df = self.data_frame
        df_values['mean_value'] = np.sqrt((df_values['mean_1'] ** 2 + df_values['mean_2'] ** 2 +
                                          df_values['mean_3'] ** 2 + df_values['mean_4'] ** 2) / 4)
        df_values['mean_variance'] = np.sqrt((df_values['var_1'] ** 2 + df_values['var_2'] ** 2 +
                                             df_values['var_3'] ** 2 + df_values['var_4'] ** 2) / 4)

        df_values.loc[df_values['mean_variance'] < 141.4158, 'result'] = 0
        df_values.loc[df_values['result'] != 0, 'result'] = 1
        df = df.join(df_values['result'])
        df = df.join(df_values['mean_value'])
        df = df.join(df_values['mean_1'])

        poly_cut = Poly1d(self.data_frame, 'avgvolt', 20, 141.4158)
        dff = poly_cut.mean_filtering()

        df = df.join(dff['height'])