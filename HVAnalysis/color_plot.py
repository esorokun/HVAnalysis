from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import logging
from functools import cached_property
import matplotlib.pyplot as plt
import seaborn as sns


class BeamFilter:
    def beamMom_period_df(self):
        file_name = 'data/output/beamMom.txt'
        unstable_periods = []
        with open(file_name, 'r') as input_file:
            for line in input_file:
                line = line.replace('\t', '')
                line = line.replace('\n', '')
                while line.find('  ') != -1:
                    line = line.replace('  ', ' ')
                unstable_periods.append(line)
        unstable_periods.pop(0)
        with open('data/output/beamMom_df.txt', 'w') as output_file:
            for line in unstable_periods:
                output_file.write(f'{line}\n')
        unstable_periods_time = []
        unstable_periods_value = []
        for line in unstable_periods:
            unstable_periods_time.append(datetime.strptime(line.split(',')[0], "%Y-%m-%d %H:%M:%S"))
            if float(line.split(',')[1]) != 0:
                bool = True
            else:
                bool = False
            unstable_periods_value.append(bool)
        model = {'timestamp': unstable_periods_time, 'stable': unstable_periods_value}
        df = pd.DataFrame(model)
        return df

    def beam_on_df(self):
        df = self.beamMom_period_df()
        stream = False
        stable_period_start = []
        stable_period_end = []
        for row in df.itertuples():
            b = row.Index
            time = row.timestamp
            bool = row.stable
            if bool and not stream:
                stream = True
                start = time
            if not bool and stream:
                stream = False
                stable_period_start.append(start)
                stable_period_end.append(time)
        beam_on_time = []
        length = len(stable_period_start)
        i = 0
        while i < length:
            j = stable_period_start[i]
            while j < stable_period_end[i]:
                beam_on_time.append(j)
                j += timedelta(seconds=1)
            i += 1
        df = pd.DataFrame({'timestamp': beam_on_time})
        return df

    def beam_on_filter(self, df):
        df_filter = self.beam_on_df()
        result = df.merge(df_filter, on=['timestamp'])
        result = result.set_index('timestamp')
        logging.info(f'beam_on_filter_df =\n{result}')
        return result


class ColorDF(BeamFilter):
    def __init__(self, df_bool):
        self.df_bool = df_bool

    def filter_df_by_beam_mom(self):
        self.df_bool = self.beam_on_filter(self.df_bool)
        return 0

    ''' def date_type_of_data(self, unstable_period):
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

        return df_filter'''

    def bool_in_color_df(self):
        df = self.df_bool
        mask = df['bool']
        df['color'] = 'blue'
        df.loc[mask, ['color']] = 'red'
        return df


class BuildColorPlots(ColorDF):
    def __init__(self, df_bool):
        super().__init__(df_bool)
        self.df_color = self.bool_in_color_df()

    def percentage_of_unstable_data(self):
        df = self.df_bool
        first_time = int(round(df.index[0].timestamp()))
        last_time = int(round(df.last_valid_index().timestamp()))
        all_time = last_time - first_time
        mask_1 = df['bool'].eq(True)
        mask_2 = df['bool'].shift(1).eq(True)
        mask_3 = df['bool'].shift(-1).eq(True)
        submask = mask_1.mask(mask_2, True)
        submask = submask.mask(mask_3, True)
        submask[0] = True
        submask[submask.last_valid_index()] = True
        df = df[submask]
        mask_1 = df['bool'].eq(False)
        mask_2 = df['bool'].shift(1).eq(False)
        mask_3 = df['bool'].shift(-1).eq(False)
        submask = mask_1.mask(mask_2, True)
        submask = submask.mask(mask_3, True)
        submask[0] = True
        submask[submask.last_valid_index()] = True
        df = df[submask]
        print(df)
        length = int(len(df))
        i, red_count = 0, 0
        while i < length - 1:
            if df.loc[df.index[i], 'bool']:
                if df.loc[df.index[i], 'bool'] == df.loc[df.index[i+1], 'bool']:
                    red_count += int(datetime.timestamp(df.index[i+1])) - int(datetime.timestamp(df.index[i]))
                else:
                    red_count += 1
            i += 1
        red = round(red_count*100/all_time, 2)
        return red

    def build_color_scatter_plot(self):
        df = self.df_color
        color_list = df['color'].values
        plt.scatter(y=df['avgvolt'], x=df['avgcurr'], alpha=0.05, s=0.1, c=color_list,)
        plt.xlabel('avgcurr')
        plt.ylabel('avgvolt')
        unstable = self. percentage_of_unstable_data()
        stable = round(100 - unstable, 2)
        plt.title('Stable periods    : ' + str(stable) + '%\nUnstable periods : ' + str(unstable) + '%')
        plt.show()

    def build_color_histogram_plot(self, name='resistance'):
        df = self.df_color
        df_red = df[df['bool']]
        df_blue_mask = df['bool'] == False
        df_blue = df[df_blue_mask]
        range = None
        if name == 'resistance':
            range = [-2000, 3000]
        plt.hist(df_blue[name], bins=100, range=range, histtype='barstacked', stacked=True, color='b')
        plt.hist(df_red[name], bins=100, range=range, histtype='barstacked', stacked=True, color='r')
        plt.xlabel(name)
        plt.ylabel("Num")
        unstable = self.percentage_of_unstable_data()
        stable = round(100 - unstable, 2)
        plt.title('Stable periods    : ' + str(stable) + '%\nUnstable periods : ' + str(unstable) + '%')
        plt.show()

    def build_color_sns_scatter_plot(self):
        df = self.df_color
        mask = df['bool']
        df['color'] = 'Stable'
        df.loc[mask, ['color']] = 'Unstable'
        g = sns.jointplot(x='avgcurr', y='avgvolt', data=df, hue='color', palette=['b', 'r'],
                          s=3, alpha=0.1, marginal_ticks=True, height=8, ratio=4)
        un = self.percentage_of_unstable_data()
        stbl = round(100 - un, 2)
        plt.legend(labels=[str(un) + "%", str(stbl) + "%"])
        df_r = df[df['bool']]
        mybins = 30
        _ = g.ax_marg_x.hist(df_r['avgcurr'], color='r', alpha=.6, bins=mybins)
        _ = g.ax_marg_y.hist(df_r['avgvolt'], color='r', alpha=.6, bins=mybins, orientation="horizontal")
        df_b = df[~df['bool']]
        _ = g.ax_marg_x.hist(df_b['avgcurr'], color='b', alpha=.6, bins=mybins)
        _ = g.ax_marg_y.hist(df_b['avgvolt'], color='b', alpha=.6, bins=mybins, orientation="horizontal")
        plt.show()