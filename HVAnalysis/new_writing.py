import csv
import pandas as pd
from datetime import datetime, timedelta
import time as pytime


class NewWriter:
    def __init__(self, df_wrapper, file_name):
        self.df_wrapper = df_wrapper
        self.file_name = file_name

    def write_streamer_periods(self):
        b1 = datetime(2018, 10, 5, 0, 0, 0)
        b2 = datetime(2018, 10, 17, 12, 0, 0)
        df = self.df_wrapper.data_frame
        stream = False
        cut_time = []

        def period_cut_writer(unstable_list, file, start, end):
            unstable_list.append([start - timedelta(0, 2), end + timedelta(0, 2)])
            writer.writerow([int(pytime.mktime((start - timedelta(0, 2)).timetuple())),
                             int(pytime.mktime((end + timedelta(0, 2)).timetuple()))])

        with open(self.file_name, mode='w') as f:
            writer = csv.writer(f)
            for row in df.itertuples():
                if row.ncurr == 0 or row.nvolt == 0:
                    continue
                # piecewise cut on resistance
                b = row.Index
                r = row.resistance
                avgvolt = row.avgvolt

                if b <= b1:
                    if not stream and (1472 < r or r < 1452 or avgvolt < 120000.):
                        stream = True
                        start_stream = b
                    elif stream and (1452 < r < 1472 and avgvolt > 120000.):
                        stream = False
                        period_cut_writer(cut_time, writer, start_stream, b)
                if b1 < b < b2:
                    if not stream and (r < 1465 or avgvolt < 120000.):
                        stream = True
                        start_stream = b
                    elif stream and (r > 1465 and avgvolt > 120000.) and stream:
                        stream = False
                        period_cut_writer(cut_time, writer, start_stream, b)
                if b >= b2:
                    if not stream and (r < 1465 or avgvolt < 180000.):
                        stream = True
                        start_stream = b
                    elif stream and (r > 1465 and avgvolt > 180000.) and stream:
                        stream = False
                        period_cut_writer(cut_time, writer, start_stream, b)