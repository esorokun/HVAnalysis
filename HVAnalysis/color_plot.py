from datetime import datetime
import pandas as pd
import logging
from functools import cached_property
import matplotlib.pyplot as plt


def beamMom_period_writer():
    file_name = 'data/output/beamMom.txt'
    unstable_periods = []
    with open(file_name, 'r') as input_file:
        for line in input_file:
            line = line.replace('\t', '')
            line = line.replace('\n', '')
            while line.find(' ') != -1:
                line = line.replace(' ', '')
            unstable_periods.append(line)
    unstable_periods.pop(0)
    print(unstable_periods)
    with open('data/output/beamMom_df.txt', 'w') as output_file:
        for line in unstable_periods:
            #line = line.replace(', ', ',')
            output_file.write(f'{line}\n')


class ColorPlots:
    def __init__(self, df_match):
        self.df_match = df_match

    def date_type_of_data(self, unstable_period):
        full_date_time = []
        i = 0
        while i < unstable_period.index.size:
            time = unstable_period.at[i, 'start_time']
            while unstable_period.at[i, 'start_time'] <= time <= unstable_period.at[i, 'end_time']:
                full_date_time.append([datetime.fromtimestamp(time)])
                time += 1
            i += 1
        full_df = pd.DataFrame(full_date_time).set_axis(['timestamp'], axis=1)
        full_df = full_df.drop_duplicates()
        return full_df

    def colored_type_of_data(self, unstable_periods):
        df = self.df_match
        unstable_df = self.date_type_of_data(unstable_periods)

        unstable_df['color'] = 'red'
        unstable_df.set_index('timestamp', inplace=True)

        df_filter = pd.merge(df, unstable_df, on='timestamp', how='left')
        empty = df_filter['color'] != 'red'
        df_filter.loc[empty, ['color']] = 'blue'

        return df_filter

    def bool_in_color_df(self):
        df = self.df_match
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
        plt.hist(df_blue['resistance'], bins=200, range=range, histtype='barstacked', stacked=True, color='b')
        plt.hist(df_red['resistance'], bins=200, range=range, histtype='barstacked', stacked=True, color='r')
        plt.xlabel("resistance")
        plt.ylabel("Num")
        plt.show()