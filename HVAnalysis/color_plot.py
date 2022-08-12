from datetime import datetime, timedelta
import pandas as pd
import logging
from functools import cached_property
import matplotlib.pyplot as plt


def beamMom_period_df():
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

def beam_on_df():
    df = beamMom_period_df()
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
    beam_on_time =[]
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

    def beam_on_filter(self, df):
        df_filter = beam_on_df()
        result = df.merge(df_filter, on=['timestamp'])
        return result

    def bool_in_color_df(self):
        df = self.df_match
        mask = df['bool']
        df['color'] = 'blue'
        df.loc[mask, ['color']] = 'red'
        return df

    def percentage_of_unstable_data(self, unstable_periods):
        first_time = int(round(self.df_match.index[0].timestamp()))
        last_time = int(round(self.df_match.last_valid_index().timestamp()))
        all_time = last_time - first_time
        counter = 0
        length = int(len(unstable_periods))
        i = 0
        for u_p in unstable_periods:
            begin = u_p[0]
            end = u_p[1]
            begin = int(datetime.timestamp(begin))
            end = int(datetime.timestamp(end))
            counter += end - begin
        unstable = round(100*counter/all_time, 2)
        return unstable

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
        name = 'resistance'
        plt.hist(df_blue[name], bins=200, range=range, histtype='barstacked', stacked=True, color='b')
        plt.hist(df_red[name], bins=200, range=range, histtype='barstacked', stacked=True, color='r')
        plt.xlabel(name)
        plt.ylabel("Num")
        plt.show()