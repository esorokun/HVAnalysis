import csv
import pandas as pd
from datetime import datetime, timedelta
import time as pytime
import logging
from filtering import Filter


def hv_filter_data_in_csv():
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
        for line in unstable_periods:
            line = line.replace(', ', ',')
            output_file.write(f'{line}\n')

class NewWriter:
    def __init__(self, df_wrapper, file_name):
        self.df_wrapper = df_wrapper
        self.file_name = file_name

    def create_unstable_df_for_b1(self, df):

        model_1 = df['avgvolt'] < 120000.
        model_2 = 1452 > df['resistance']
        model_1 = model_1.mask(model_2, True)

        model_3 = df['resistance'] > 1472
        model_1 = model_1.mask(model_3, True)

        return model_1

    def create_unstable_df_for_b1_b2(self, df):
        b1 = datetime(2018, 10, 5, 0, 0, 0)
        map = df.index <= b1
        df_b1, df_b1_b2 = df[map], df[~map]

        model_1 = df_b1_b2['resistance'] < 1465
        model_2 = df_b1_b2['avgvolt'] < 120000.
        model_1 = model_1.mask(model_2, True)

        df_res_1 = self.create_unstable_df_for_b1(df_b1)

        result = pd.concat([df_res_1, model_1])
        return result

    def create_unstable_df_for_b2(self, df):
        b2 = datetime(2018, 10, 17, 12, 0, 0)
        map = df.index < b2
        df_b1_b2, df_b2 = df[map], df[~map]

        model_1 = df_b2['resistance'] < 1465
        model_2 = df_b2['avgvolt'] < 180000.
        model_1 = model_1.mask(model_2, True)

        df_res_1 = self.create_unstable_df_for_b1_b2(df_b1_b2)

        result = pd.concat([df_res_1, model_1])
        return result

    def new_df_unstable_periods(self):

        b1 = datetime(2018, 10, 5, 0, 0, 0)  # 2018-10-05 00:00:00
        b2 = datetime(2018, 10, 17, 12, 0, 0)  # 2018-10-17 12:00:00
        df = self.df_wrapper.data_frame

        logging.info(f'HeinzWrapper.data_frame =\n{df}')
        last_index = df.last_valid_index()
        if last_index >= b2:
            df['bool'] = self.create_unstable_df_for_b2(df)
        elif last_index > b1:
            df['bool'] = self.create_unstable_df_for_b1_b2(df)
        elif last_index <= b1:
            df['bool'] = self.create_unstable_df_for_b1(df)
        return df

    def short_unstable_df(self):
        df = self.new_df_unstable_periods()

        first_date = datetime(2018, 9, 19, 0, 0, 0)
        start_date = df.index > first_date
        df = df[start_date]

        df_clear_1 = df['ncurr'] != 0
        df = df[df_clear_1]
        df_clear_2 = df['nvolt'] != 0
        df = df[df_clear_2]

        mask_1 = df['bool'].eq(True)
        mask_2 = df['bool'].shift(1).eq(True)
        mask_3 = df['bool'].shift(-1).eq(True)
        submask = mask_1.mask(mask_2, True)
        submask = submask.mask(mask_3, True)
        df = df[submask]

        mask_1 = df['bool'].eq(False)
        mask_2 = df['bool'].shift(1).eq(False)
        mask_3 = df['bool'].shift(-1).eq(False)
        submask = mask_1.mask(mask_2, True)
        submask = submask.mask(mask_3, True)
        df = df[submask]
        return df

    def new_df_unstable_writer(self):
        df = self.short_unstable_df()
        start_time = pytime.time()
        first_date = datetime(2018, 9, 19, 0, 0, 0)
        stream = True
        start = datetime(2018, 9, 19, 0, 0, 18)
        unstable_periods = []
        logging.info(f'HeinzWrapper.data_frame =\n{df}')

        for row in df.itertuples():
            b = row.Index
            bool = row.bool
            if bool and not stream:
                stream = True
                start = b
            elif not bool and stream:
                stream = False
                unstable_periods.append([start - timedelta(0, 2), b + timedelta(0, 2)])

        unstable_periods.pop()
        unstable_periods.append([start - timedelta(0, 2), b + timedelta(0, 4, hours=1, minutes=1)])

        with open(self.file_name, mode='w') as f:
            writer = csv.writer(f, delimiter=',')
            for u_p in unstable_periods:
                row = [to_time_stamp(dt) for dt in u_p]
                writer.writerow(row)

        print("--- %s seconds ---" % (pytime.time() - start_time))

def to_time_stamp(dt):
    if dt < datetime(2018, 10, 28):
        return int(datetime.timestamp(dt + timedelta(hours=3)))
    return int(datetime.timestamp(dt + timedelta(hours=2)))

