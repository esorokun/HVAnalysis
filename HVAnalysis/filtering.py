import csv
from datetime import datetime, timedelta
import pandas as pd
from original_writing import Writer
import logging
from functools import cached_property

class Filter:
    def __init__(self, df_writer):
        self.df_writer = df_writer
        self.file_name = df_writer.file_name

    def _get_data_frame_from_file(self):
        self.df_writer.write_streamer_periods()
        df = pd.read_csv(self.file_name, sep=',', usecols=[0, 1],
                           names=['start_time', 'end_time'])
        logging.info(f'HeinzWrapper.data_frame_from_file =\n{df}')
        return df

    @cached_property
    def data_frame(self):
        df = pd.concat([self._get_data_frame_from_file()], axis=0)
        logging.info(f'HeinzWrapper.data_frame =\n{df}')
        return df

    def date_type_of_data(self):
        full_date_time = []
        df = self.data_frame
        i = 0
        while i < df.index.size:
            time = df.at[i, 'start_time']
            while df.at[i, 'start_time'] <= time <= df.at[i, 'end_time']:
                full_date_time.append([time])
                time += 1
            i += 1
        full_df = pd.DataFrame(full_date_time).set_axis(['unstable_dates'], axis=1)
        logging.info(f'HeinzWrapper.unstable_data_frame_ =\n{full_df}')
        return full_df





'''
    def write_streamer_periods(self):
        b1 = datetime(2018, 10, 5, 0, 0, 0)
        b2 = datetime(2018, 10, 17, 12, 0, 0)
        df = self.df_wrapper.data_frame
        stream = False
        cut_time = []

        def period_cut_writer(unstablelist, file, start, end):
            unstablelist.append([start - timedelta(0, 2), end + timedelta(0, 2)])
            i = start - timedelta(0, 2)
            while i < end + timedelta(0, 2):
                file.writerow([i, ])
                unstablelist.append([i])

                i += timedelta(0, 1)

        with open(file_name, mode='w') as f:
            writer = csv.writer(f, delimiter=',')
            for row in df.itertuples():
                if row.ncurr == 0 or row.nvolt == 0:
                    continue
                # piecewise cut on resistance
                b = row.Index
                r = row.resistance
                vps = row.avgvolt

                if b <= b1:
                    if not stream and 1472 < r or r < 1452 or vps < 120000.:
                        stream = True
                        start_stream = b
                    elif 1452 < r < 1472 and vps > 120000. and stream:
                        stream = False
                        period_cut_writer(cut_time, writer, start_stream, b)
                if b1 < b < b2:
                    if not stream and (r < 1465 or vps < 120000.):
                        stream = True
                        start_stream = b
                    elif stream and (r > 1465 and vps > 120000.) and stream:
                        stream = False
                        period_cut_writer(cut_time, writer, start_stream, b)
                if b >= b2:
                    if not stream and (r < 1465 or vps < 180000.):
                        stream = True
                        start_stream = b
                    elif stream and (r > 1465 and vps > 180000.) and stream:
                        stream = False
                        period_cut_writer(cut_time, writer, start_stream, b)

    def create_unstable_date_df(self, file_name):
        self.write_streamer_periods(file_name)
        df = pd.read_csv(file_name,
                        index_col=0, use_cols=[0], names=['timestamp'])
        df['timestamp'] = pd.to_datetime(df.index)
        logging.info(f'HeinzWrapper.stable_data_frame =\n{df}')
        return df
'''