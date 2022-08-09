from datetime import datetime
import pandas as pd
import logging
from functools import cached_property
import matplotlib.pyplot as plt


class Filter:
    def __init__(self, df_writer):
        self.df_writer = df_writer
        self.file_name = df_writer.file_name
        self.df_wrapper = df_writer.df_wrapper

    def _get_data_frame_from_file(self):
        self.df_writer.write_streamer_periods()
        df = pd.read_csv(self.df_writer.file_name, sep=',', usecols=[0, 1], names=['start_time', 'end_time'])
        return df

    @cached_property
    def data_frame(self):
        return pd.concat([self._get_data_frame_from_file()], axis=0)

    def date_type_of_data(self):
        full_date_time = []
        df = self.data_frame
        i = 0

        while i < df.index.size:
            time = df.at[i, 'start_time']
            while df.at[i, 'start_time'] <= time <= df.at[i, 'end_time']:
                full_date_time.append([datetime.fromtimestamp(time)])
                time += 1
            i += 1
        full_df = pd.DataFrame(full_date_time).set_axis(['timestamp'], axis=1)
        full_df = full_df.drop_duplicates()
        full_df.to_csv('data/output/pandas_old.csv', header=True,
                           sep="\t", mode='w', float_format='%.0f')
        return full_df

    def colored_type_of_data(self):
        df = self.df_wrapper.data_frame
        unstable_df = self.date_type_of_data()

        unstable_df['color'] = 'red'
        unstable_df.set_index('timestamp', inplace=True)

        df_filter = pd.merge(df, unstable_df, on='timestamp', how='left')
        empty = df_filter['color'] != 'red'
        df_filter.loc[empty, ['color']] = 'blue'

        return df_filter

    def bool_in_color_df(self, df):
        mask = df['bool']
        df['color'] = 'blue'
        df.loc[mask, ['color']] = 'red'
        return df

    def build_color_scatter_plot(self, df):
        color_list = df['color'].values

        plt.scatter(y=df['avgvolt'], x=df['avgcurr'], alpha=0.05, s=0.1, c=color_list,)
        #plt.xlim(500, 3000)
        #plt.ylim(0, 200)
        plt.xlabel('avgcurr')
        plt.ylabel('avgvolt')

        plt.show()

    def build_color_histogram_plot(self, df):
        df_red = df[df['bool']]
        df_blue_mask = df['bool'] == False
        df_blue = df[df_blue_mask]
        range = [-2000, 3000]
        plt.hist(df_blue['resistance'], bins=60, range=range, density=True, histtype='bar', stacked=True, color='b')
        plt.hist(df_red['resistance'], bins=60, range=range, density=True, histtype='bar', stacked=True, color='r')
        plt.xlabel("resistance")
        plt.ylabel("Num")
        plt.show()