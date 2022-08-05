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

        model_1 = df['avgvolt'] < 120000.
        df['bool'] = model_1

        model_2 = 1452 > df['resistance']
        model_1 = model_1.mask(model_2, True)

        model_3 = df['resistance'] > 1472
        model_1 = model_1.mask(model_3, True)

        df['bool'] = model_1
        return df

    def create_unstable_df_for_b1_b2(self, df):
        b1 = datetime(2018, 10, 5, 0, 0, 0)
        map = df.index <= b1
        df_b1, df_b1_b2 = df[map], df[~map]

        model_1 = df_b1_b2['resistance'] < 1465
        model_2 = df_b1_b2['avgvolt'] < 120000.
        model_1 = model_1.mask(model_2, True)
        df_b1_b2['bool'] = model_1

        df_res_1 = self.create_unstable_df_for_b1(df_b1)

        result = pd.concat([df_res_1, df_b1_b2]).sort_index()
        return result

    def create_unstable_df_for_b2(self, df):
        b2 = datetime(2018, 10, 17, 12, 0, 0)
        map = df.index < b2
        df_b1_b2, df_b2 = df[map], df[~map]

        model_1 = df_b2['resistance'] < 1465
        model_2 = df_b2['avgvolt'] < 180000.
        model_1 = model_1.mask(model_2, True)

        df_res_1 = self.create_unstable_df_for_b1_b2(df_b1_b2)
        df_b2['bool'] = model_1
        result = pd.concat([df_res_1, df_b2]).sort_index()
        return result

    def new_df_unstable_periods(self):

        b1 = datetime(2018, 10, 5, 0, 0, 0)  # 2018-10-05 00:00:00
        b2 = datetime(2018, 10, 17, 12, 0, 0)  # 2018-10-17 12:00:00
        df = self.df_wrapper.data_frame
        last_index = df.last_valid_index()
        df_unstable = []
        if last_index >= b2:
            print(1)
            df_unstable = self.create_unstable_df_for_b2(df)
        elif last_index > b1:
            print(2)
            df_unstable = self.create_unstable_df_for_b1_b2(df)
        elif last_index <= b1:
            print(3)
            df_unstable = self.create_unstable_df_for_b1(df)

        return df_unstable

    def new_df_unstable_writer(self):
        df = self.new_df_unstable_periods()
        mask_1 = df['bool'].eq(True)
        mask_2 = df['bool'].shift(1).eq(True)
        mask_3 = df['bool'].shift(-1).eq(True)
        mask_1 = mask_1.mask(mask_2, True)
        mask_1 = mask_1.mask(mask_3, True)
        df = df[mask_1]
        mask_1 = df['bool'].eq(False)
        mask_2 = df['bool'].shift(1).eq(False)
        mask_3 = df['bool'].shift(-1).eq(False)
        mask_1 = mask_1.mask(mask_2, True)
        mask_1 = mask_1.mask(mask_3, True)
        df = df[mask_1]

        df.to_csv('data/output/pandas.csv', header=True,
                           sep="\t", mode='w', float_format='%.1f')
        logging.info(f'HeinzWrapper.data_frame =\n{df}')
        with open(self.file_name, mode='w') as f:
            writer = csv.writer(f)
            stream = False
            for row in df.itertuples():
                if row.ncurr == 0 or row.nvolt == 0:
                    continue
                b = row.Index
                bool = row.bool
                if bool and not stream:
                    stream = True
                    start = b
                elif not bool and stream:
                    stream = False
                    writer.writerow([int(pytime.mktime((start - timedelta(0, 2)).timetuple())),
                                     int(pytime.mktime((b + timedelta(0, 2)).timetuple()))])






