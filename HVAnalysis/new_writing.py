import csv
import pandas as pd
from datetime import datetime, timedelta
import time as pytime
import logging
from filtering import Filter

class NewWriter:
    def __init__(self, df_wrapper, file_name):
        self.df_wrapper = df_wrapper
        self.file_name = file_name

    def hv_filter_data_in_csv(self):

        # grid_start = '2018-09-19 03:00:16'
        # grid_end = '2018-11-12 13:50:03'

        file_name = 'data/output/ProtoDUNEUnstableHVFilter.fcl'
        with open(file_name, 'r') as input_file:
            for line in input_file:
                if not 'TimeRanges' in line:
                    continue

                unstable_periods = line.split('], [')
                unstable_periods[0] = unstable_periods[0].replace('  TimeRanges: [[', '')
                unstable_periods[-1] = unstable_periods[-1].replace(']', '')

        with open('data/output/transformed_periods.csv', 'w') as output_file:
            self.file_name = 'data/output/transformed_periods.csv'
            for line in unstable_periods:
                line = line.replace(', ', ',')
                output_file.write(f'{line}\n')

    def period_cut_writer(self, unstable_list, file, start, end):
        unstable_list.append([start - timedelta(0, 2), end + timedelta(0, 2)])
        file.writerow([int(pytime.mktime((start - timedelta(0, 2)).timetuple())),
                    int(pytime.mktime((end + timedelta(0, 2)).timetuple()))])

    def write_streamer_periods(self):
        b1 = datetime(2018, 10, 5, 0, 0, 0)     #2018-10-05 00:00:00
        b2 = datetime(2018, 10, 17, 12, 0, 0)   #2018-10-17 12:00:00
        df = self.df_wrapper.data_frame
        stream = False
        cut_time = []

        with open(self.file_name, mode='w') as f:
            writer = csv.writer(f)
            last = df.last_valid_index()

            for row in df.itertuples():
                if row.ncurr == 0 or row.nvolt == 0:
                    continue  # piecewise cut on resistance

                b = row.Index
                r = row.resistance
                avgvolt = row.avgvolt

                if b <= b1:
                    if not stream and (1472 < r or r < 1452 or avgvolt < 120000.):
                        stream = True
                        start_stream = b
                    elif stream and (1452 < r < 1472 and avgvolt > 120000.):
                        stream = False
                        self.period_cut_writer(cut_time, writer, start_stream, b)

                elif b1 < b < b2:
                    if not stream and (r < 1465 or avgvolt < 120000.):
                        stream = True
                        start_stream = b
                    elif stream and (r > 1465 and avgvolt > 120000.):
                        stream = False
                        self.period_cut_writer(cut_time, writer, start_stream, b)

                elif b >= b2:
                    if not stream and (r < 1465 or avgvolt < 180000.):
                        stream = True
                        start_stream = b
                    elif stream and (r > 1465 and avgvolt > 180000.):
                        stream = False
                        self.period_cut_writer(cut_time, writer, start_stream, b)

                #if b == last:
                 #   self.last_period_cut_writer(cut_time, writer, start_stream, b)

    def create_unstable_df_for_b1(self, df):
        model_1 = (1452 > df['resistance'] or df['resistance'] > 1472 and df['avgvolt'] < 12000.)
        df_res = df[model_1]
        return df_res

    def create_unstable_df_for_b1_b2(self, df, df_add):
        model_1 = (df['resistance'] < 1465 and df['avgvolt'] < 12000.)
        df_res = df[model_1]
        result = pd.concat([df_add, df_res])
        return result

    def create_unstable_df_for_b2(self, df, df_add):
        model_1 = (df['resistance'] < 1465 and df['avgvolt'] < 18000.)
        df_res = df[model_1]
        result = pd.concat([df_add, df_res])
        return result

    def new_write_stremer_periods(self):
        b1 = datetime(2018, 10, 5, 0, 0, 0)  # 2018-10-05 00:00:00
        b2 = datetime(2018, 10, 17, 12, 0, 0)  # 2018-10-17 12:00:00
        df = self.df_wrapper.data_frame
        last_index = df.last_valid_index()
        if last_index > b2:

            map_1 = df.index <= b1
            df_b1, df_2 = df[map_1], df[~map_1]  #df for  --> b1 and b1-->
            map_2 = df_2.index < b2
            df_b1_b2, df_b2 = df_2[map_1], df_2[~map_1]  #separate  b1--> on b1-->b2 and b2-->

        elif last_index < b2:
            map_1 = df.index <= b1
            df_b1, df_b1_b2 = df[map_1], df[~map_1]


        elif last_index <= b1:




