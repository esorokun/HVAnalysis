import csv
from datetime import datetime, timedelta
import time as pytime
import logging

import numpy as np
import pandas as pd


class Writer:
    def __init__(self, df_wrapper, file_name):
        self.df_wrapper = df_wrapper
        self.file_name = file_name

    def get_unstable_periods(self):
        raise NotImplemented

    def compare_two_lists(self, unstable_periods_1, unstable_periods_2):
        length_1 = int(len(unstable_periods_1))
        length_2 = int(len(unstable_periods_2))
        time_line_1 = []
        time_line_2 = []
        i = 0
        while i < length_1:
            j = unstable_periods_1[i][0]
            while j <= unstable_periods_1[i][1]:
                time_line_1.append(j)
                j += 1
            i += 1
        i = 0
        time_line_1 = list(set(time_line_1))
        while i < length_2:
            j = unstable_periods_2[i][0]
            while j <= unstable_periods_2[i][1]:
                time_line_2.append(j)
                j += 1
            i += 1
        time_line_2 = list(set(time_line_2))
        time_length_1 = int(len(time_line_1))
        time_length_2 = int(len(time_line_2))
        print(time_length_2 - time_length_1)
        return 0

    def write_unstable_not_overlapping_periods(self, unstable_periods, safety_seconds=0,):
        safety_interval = timedelta(seconds=2*safety_seconds)
        length = int(len(unstable_periods)) - 1
        unstbl_p = []
        i = 0
        while i < length:
            start_time = unstable_periods[i][0]
            while unstable_periods[i+1][0] - unstable_periods[i][1] <= safety_interval:
                i += 1
            end_time = unstable_periods[i][1]
            unstbl_p.append([start_time, end_time])
            i += 1
        start_time = unstable_periods[i][0]
        end_time = unstable_periods[i][1]
        unstbl_p.append([start_time, end_time])
        safety_period = timedelta(seconds=safety_seconds)
        new_list = []
        with open(self.file_name, mode='w') as f:
            writer = csv.writer(f, delimiter=',')
            for u_p in unstbl_p:
                begin = u_p[0] - safety_period
                end = u_p[1] + safety_period
                row = [to_time_stamp(begin), to_time_stamp(end)]
                new_list.append(row)
                writer.writerow(row)
        return new_list

    def write_unstable_periods(self, unstable_periods, safety_seconds=0):
        new_list = []
        safety_interval = timedelta(seconds=safety_seconds)
        with open(self.file_name, mode='w') as f:
            writer = csv.writer(f, delimiter=',')
            for u_p in unstable_periods:
                begin = u_p[0] - safety_interval
                end = u_p[1] + safety_interval
                row = [to_time_stamp(begin), to_time_stamp(end)]
                new_list.append(row)
                writer.writerow(row)
        return new_list


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


class CutAvgVolt:
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

    def cut_avgvolt_df_unstable_periods(self, df):
        b1 = datetime(2018, 10, 5, 0, 0, 0)  # 2018-10-05 00:00:00
        b2 = datetime(2018, 10, 17, 12, 0, 0)  # 2018-10-17 12:00:00
        last_index = df.last_valid_index()
        if last_index >= b2:
            df['bool'] = self.cut_avgvolt_unstable_df_for_b2(df)
        elif last_index > b1:
            df['bool'] = self.cut_avgvolt_unstable_df_for_b1_b2(df)
        elif last_index <= b1:
            df['bool'] = self.cut_avgvolt_unstable_df_for_b1(df)
        df = df.dropna(subset=['bool'])
        return df


class BoolCurr:
    def curr_unstable_df_for_b1(self, df):
        model_1 = 1452 > df['resistance']
        model_2 = df['resistance'] > 1472
        model_3 = df['avgvolt'] < 120000.
        model_4 = df['avgcurr'] < 20.
        model_1 = model_1.mask(model_2, True)
        model_1 = model_1.mask(model_3, True)
        model_1 = model_1.mask(model_4, True)
        return model_1

    def curr_unstable_df_for_b1_b2(self, df):
        b1 = datetime(2018, 10, 5, 0, 0, 0)
        map = df.index <= b1
        df_b1, df_b1_b2 = df[map], df[~map]
        model_1 = df_b1_b2['resistance'] < 1465
        model_2 = df_b1_b2['avgvolt'] < 120000.
        model_3 = df_b1_b2['avgcurr'] < 20.
        model_1 = model_1.mask(model_3, True)
        model_1 = model_1.mask(model_2, True)
        df_res_1 = self.curr_unstable_df_for_b1(df_b1)
        result = pd.concat([df_res_1, model_1])
        return result

    def curr_unstable_df_for_b2(self, df):
        b2 = datetime(2018, 10, 17, 12, 0, 0)
        map = df.index < b2
        df_b1_b2, df_b2 = df[map], df[~map]
        model_1 = df_b2['resistance'] < 1465
        model_2 = df_b2['avgvolt'] < 180000.
        model_3 = df_b2['avgcurr'] < 20.
        model_1 = model_1.mask(model_3, True)
        model_1 = model_1.mask(model_2, True)
        df_res_1 = self.curr_unstable_df_for_b1_b2(df_b1_b2)
        result = pd.concat([df_res_1, model_1])
        return result

    def bool_curr_df_unstable_periods(self, df):
        b1 = datetime(2018, 10, 5, 0, 0, 0)  # 2018-10-05 00:00:00
        b2 = datetime(2018, 10, 17, 12, 0, 0)  # 2018-10-17 12:00:00
        logging.info(f'HeinzWrapper.data_frame =\n{df}')
        last_index = df.last_valid_index()
        if last_index >= b2:
            df['bool'] = self.curr_unstable_df_for_b2(df)
        elif last_index > b1:
            df['bool'] = self.curr_unstable_df_for_b1_b2(df)
        elif last_index <= b1:
            df['bool'] = self.curr_unstable_df_for_b1(df)
        return df


class CutOriginal:
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

    def new_df_unstable_periods(self, df):
        b1 = datetime(2018, 10, 5, 0, 0, 0)  # 2018-10-05 00:00:00
        b2 = datetime(2018, 10, 17, 12, 0, 0)  # 2018-10-17 12:00:00
        logging.info(f'HeinzWrapper.data_frame =\n{df}')
        last_index = df.last_valid_index()
        if last_index >= b2:
            df['bool'] = self.create_unstable_df_for_b2(df)
        elif last_index > b1:
            df['bool'] = self.create_unstable_df_for_b1_b2(df)
        elif last_index <= b1:
            df['bool'] = self.create_unstable_df_for_b1(df)
        return df


class ErnestsWriter(Writer, CutOriginal, CutAvgVolt, BoolCurr):
    def __init__(self, df_wrapper, file_name):
        super().__init__(df_wrapper, file_name)
        self.unstable_periods = None

    def df_original_unstable_periods(self):
        self.unstable_periods = self.new_df_unstable_periods(self.df_wrapper.data_frame)
        return self.unstable_periods

    def df_avgvolt_cut_unstable_periods(self):
        self.unstable_periods = self.cut_avgvolt_df_unstable_periods(self.df_wrapper.data_frame)
        return self.unstable_periods

    def df_avgcurr_bool_add_unstable_periods(self):
        self.unstable_periods = self.bool_curr_df_unstable_periods(self.df_wrapper.data_frame)
        return self.unstable_periods

    def fill_nan(self):
        self.df_wrapper.data_frame = self.df_wrapper.data_frame.ffill(axis=0)
        return self.df_wrapper.data_frame.ffill(axis=0)

    def remove_nan(self):
        df = self.df_wrapper.data_frame
        df_clear_1 = df['ncurr'] != 0
        df_clear_1[0] = True
        df_clear_1[df_clear_1.last_valid_index()] = True
        df = df[df_clear_1]
        df_clear_2 = df['nvolt'] != 0
        df_clear_2[0] = True
        df_clear_2[df_clear_2.last_valid_index()] = True
        df = df[df_clear_2]
        self.df_wrapper.data_frame = df
        return 0

    def get_unstable_periods(self):
        if self.unstable_periods == None:
            self.remove_nan()
            self.df_original_unstable_periods()
        df = self.unstable_periods
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

'''def add_size(self, df):
        df_t = df.copy()
        df = df.reset_index()
        df = (df['timestamp'] - pd.Timestamp("1970-01-01")) // pd.Timedelta("1s")
        df_copy = df.copy()
        df_copy.pop(0)
        df_copy = df_copy.reset_index(drop=True)
        s3 = df_copy.loc[df_copy.last_valid_index()]
        df_copy[df.last_valid_index()] = s3+1
        df_size = pd.DataFrame({'end': df_copy, 'start': df})
        df_size['size'] = df_size['end'] - df_size['start']
        df_size['timestamp'] = df_t.index
        df_size = df_size.set_index('timestamp')
        df_t = df_t.assign(size=df_size['size'])
        return df_t'''