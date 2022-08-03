import csv
import pandas as pd
from datetime import datetime, timedelta
import time as pytime
import logging

class Writer:
    def __init__(self, df_wrapper):
        self.df_wrapper = df_wrapper

    def write_streamer_periods(self, file_name):
        b1 = datetime(2018, 10, 5, 0, 0, 0)
        b2 = datetime(2018, 10, 17, 12, 0, 0)
        df = self.df_wrapper.data_frame
        stream = False
        cutONperiod = []

        def period_cut_writer(unstablelist, file, start, end):
            i = start - timedelta(0, 2)
            while i < end + timedelta(0, 2):
                unstablelist.append([i])
                file.writerow([i])
                i += timedelta(0, 1)

        with open(file_name, mode='w') as f:
            writer = csv.writer(f, delimiter=',')
            for row in df.itertuples():
                if row.ncurr == 0 or row.nvolt == 0: continue # piecewise cut on resistance
                b = row.Index
                r = row.resistance
                vps = row.avgvolt

                if b <= b1:
                    if not stream and 1472 < r or r < 1452 or vps < 120000.:
                        stream = True
                        startStream = b
                    elif 1452 < r < 1472 and vps > 120000. and stream:
                        stream = False
                        period_cut_writer(cutONperiod, writer, startStream, b)
                if b1 < b < b2:
                    if not stream and (r < 1465 or vps < 120000.):
                        stream = True
                        startStream = b
                    elif stream and (r > 1465 and vps > 120000.) and stream:
                        stream = False
                        period_cut_writer(cutONperiod, writer, startStream, b)
                if b >= b2:
                    if not stream and (r < 1465 or vps < 180000.):
                        stream = True
                        startStream = b
                    elif stream and (r > 1465 and vps > 180000.) and stream:
                        stream = False
                        period_cut_writer(cutONperiod, writer, startStream, b)
'''
    def create_unstable_date_df(self, file_name):
        self.write_streamer_periods(file_name)
        df = pd.read_csv(file_name,
                         index_col=0, usecols=[0], names=['timestamp'])
        df.index = 1000000000 * df.index
        df['timestamp'] = pd.to_datetime(df.index)
        logging.info(f'HeinzWrapper.stable_data_frame =\n{df}')
        return df
'''