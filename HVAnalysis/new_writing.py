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
        df_1 = df[model_1]

        model_2 = 1452 > df['resistance']
        df_2 = df[model_2]

        model_3 = df['resistance'] > 1472
        df_3 = df[model_3]

        df_res = pd.concat([df_1, df_2, df_3]).drop_duplicates()
        df_res = df_res.sort_index()
        return df_res

    def create_unstable_df_for_b1_b2(self, df):
        b1 = datetime(2018, 10, 5, 0, 0, 0)
        map = df.index <= b1
        df_b1, df_b1_b2 = df[map], df[~map]

        model = df_b1_b2['resistance'] < 1465
        df_b1_b2_ver1 = df_b1_b2[model]

        model_2 = df_b1_b2_ver1['avgvolt'] < 120000.
        df_b1_b2_ver2 = df_b1_b2[model_2]

        df_res_1 = self.create_unstable_df_for_b1(df_b1)
        result = pd.concat([df_res_1, df_b1_b2_ver2, df_b1_b2_ver1]).drop_duplicates()
        result = result.sort_index()
        return result

    def create_unstable_df_for_b2(self, df):
        b2 = datetime(2018, 10, 17, 12, 0, 0)
        map = df.index < b2
        df_b1_b2, df_b2 = df[map], df[~map]

        model = df_b2['resistance'] < 1465
        df_b2_ver1 = df_b2[model]

        model_2 = df_b2_ver1['avgvolt'] < 180000.
        df_b2_ver2 = df_b2[model_2]

        df_res_1 = self.create_unstable_df_for_b1_b2(df_b1_b2)
        result = pd.concat([df_res_1, df_b2_ver1, df_b2_ver2]).drop_duplicates()
        result = result.sort_index()
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

        logging.info(f'HeinzWrapper.data_frame =\n{df_unstable}')
        return df_unstable

    def new_df_unstable_writer(self):
        df = self.new_df_unstable_periods()
        with open(self.file_name, mode='w') as f:
            writer = csv.writer(f)
            start = list[0]
            c = start - timedelta(0, 1)
            for row in df.itertuples():
                if row.ncurr == 0 or row.nvolt == 0:
                    continue
                b = row.Index
                if int(b-1) == c:
                    writer.writerow([int(pytime.mktime((start - timedelta(0, 2)).timetuple())),
                                     int(pytime.mktime((b + timedelta(0, 2)).timetuple()))])
                    start = int(b)
                c = int(b)






