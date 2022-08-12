import csv
from datetime import datetime, timedelta
import time as pytime
import logging
import pandas as pd


class Writer:
    def __init__(self, df_wrapper, file_name):
        self.df_wrapper = df_wrapper
        self.file_name = file_name

    def get_unstable_periods(self):
        raise NotImplemented

    def write_unstable_periods(self, unstable_periods, safety_seconds=0):
        safety_interval = timedelta(seconds=safety_seconds)
        with open(self.file_name, mode='w') as f:
            writer = csv.writer(f, delimiter=',')
            for u_p in unstable_periods:
                begin = u_p[0] - safety_interval
                end = u_p[1] + safety_interval
                row = [to_time_stamp(begin), to_time_stamp(end)]
                writer.writerow(row)


class LinosWriter(Writer):
    """I'm trying to reproduce the results in ProtoDUNEUnstableHVFilter.fcl
    with this class."""
    def get_unstable_periods(self):
        df = self.df_wrapper.data_frame

        # for some reason, the original periods start at 2018-09-19 02:00:16
        first_date = datetime(2018, 9, 19, 0, 0, 0)
        b1 = datetime(2018, 10, 5, 0, 0, 0)    #2018-10-05 00:00:00
        b2 = datetime(2018, 10, 17, 12, 0, 0)  #2018-10-17 12:00:00
        streamer_on = False
        unstable_periods = []

        for row in df.itertuples():
            if row.ncurr == 0 or row.nvolt == 0:
                continue

            if row.Index < first_date:
                continue

            b = row.Index
            r = row.resistance
            vps = row.avgvolt

            if b <= b1 and (r > 1472 or r < 1452 or vps < 120000.) and not streamer_on:
                streamer_on = True
                start_stream = b

            if b <= b1 and (r > 1452 and r < 1472 and vps > 120000.) and streamer_on:
                streamer_on = False
                unstable_periods.append([start_stream, b])

            if b1 < b < b2 and (r < 1465 or vps < 120000.) and not streamer_on:
                streamer_on = True
                start_stream = b

            if b1 < b < b2 and (r > 1465 and vps > 120000.) and streamer_on:
                streamer_on = False
                unstable_periods.append([start_stream, b])

            if b >= b2 and (r < 1465 or vps < 180000.) and not streamer_on:
                streamer_on = True
                start_stream = b

            if b >= b2 and (r > 1465 and vps > 180000.) and streamer_on:
                streamer_on = False
                unstable_periods.append([start_stream, b])

        # write the last unstable period
        if streamer_on:
            end_time = datetime(b.year, b.month, b.day+1, 1, 0, 59)
            unstable_periods.append([start_stream, end_time])

        return unstable_periods


class ErnestsWriter(Writer):

    #Need to create new class for bool operations
    #Separate Create DF and Cut_avgvolt DF for different

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

    def cut_avgvolt_unstable_df_for_b1(self, df):
        model_1 = df['avgvolt'] > 120000.
        df = df[model_1]
        mask_1 = 1452 > df['resistance']
        mask_2 = 1472 < df['resistance']
        model_1 = mask_1.mask(mask_2, True)
        return model_1

    def cut_avgvolt_unstable_df_for_b1_b2(self, df):
        b1 = datetime(2018, 10, 5, 0, 0, 0)
        map = df.index <= b1
        df_b1, df_b1_b2 = df[map], df[~map]
        model_1 = df_b1_b2['avgvolt'] > 120000.
        df_b1_b2 = df_b1_b2[model_1]
        mask = df_b1_b2['resistance'] < 1465
        df_res_1 = self.cut_avgvolt_unstable_df_for_b1(df_b1)
        result = pd.concat([df_res_1, mask])
        return result

    def cut_avgvolt_unstable_df_for_b2(self, df):
        b2 = datetime(2018, 10, 17, 12, 0, 0)
        map = df.index < b2
        df_b1_b2, df_b2 = df[map], df[~map]
        model_1 = df_b2['avgvolt'] > 180000.
        df_b2 = df_b2[model_1]
        mask = df_b2['resistance'] < 1465
        df_res_1 = self.cut_avgvolt_unstable_df_for_b1_b2(df_b1_b2)
        result = pd.concat([df_res_1, mask])
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
        df_clear_1 = df['ncurr'] != 0
        df_clear_1[0] = True
        df_clear_1[df_clear_1.last_valid_index()] = True
        df = df[df_clear_1]
        df_clear_2 = df['nvolt'] != 0
        df_clear_2[0] = True
        df_clear_2[df_clear_2.last_valid_index()] = True
        df = df[df_clear_2]
        return df

    def cut_avgvolt_df_unstable_periods(self):
        b1 = datetime(2018, 10, 5, 0, 0, 0)  # 2018-10-05 00:00:00
        b2 = datetime(2018, 10, 17, 12, 0, 0)  # 2018-10-17 12:00:00
        df = self.df_wrapper.data_frame
        logging.info(f'HeinzWrapper.data_frame =\n{df}')
        last_index = df.last_valid_index()
        if last_index >= b2:
            df['bool'] = self.cut_avgvolt_unstable_df_for_b2(df)
        elif last_index > b1:
            df['bool'] = self.cut_avgvolt_unstable_df_for_b1_b2(df)
            print(df)
        elif last_index <= b1:
            df['bool'] = self.cut_avgvolt_unstable_df_for_b1(df)
        df = df.dropna(subset=['bool'])
        print(df)
        df_clear_1 = df['ncurr'] != 0
        df_clear_1[0] = True
        df_clear_1[df_clear_1.last_valid_index()] = True
        df = df[df_clear_1]
        df_clear_2 = df['nvolt'] != 0
        df_clear_2[0] = True
        df_clear_2[df_clear_2.last_valid_index()] = True
        df = df[df_clear_2]
        return df

    def get_unstable_periods(self):
        df = self.new_df_unstable_periods()
        logging.info(f'get_unstable_periods =\n{df}')
        stream = True
        start = df.index[0]
        unstable_periods = []
        for row in df.itertuples():
            b = row.Index
            bool = row.bool
            if bool and not stream:
                stream = True
                start = b
            if not bool and stream:
                stream = False
                unstable_periods.append([start, b])
        return unstable_periods


def to_time_stamp(dt):
    if dt < datetime(2018, 10, 28):
        return int(datetime.timestamp(dt + timedelta(hours=3)))
    return int(datetime.timestamp(dt + timedelta(hours=2)))
