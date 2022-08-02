import csv
import pandas as pd
from datetime import datetime, timedelta
import time as pytime


class Writer:
    def __init__(self, df_wrapper):
        self.df_wrapper = df_wrapper

    def write_streamer_periods(self, file_name):
        b1 = datetime(2018, 10, 5, 0, 0, 0)
        b2 = datetime(2018, 10, 17, 12, 0, 0)
        df = self.df_wrapper.data_frame
        streamerON = False
        cutONperiod = []
        with open(file_name, mode='w') as f:
            writer = csv.writer(f, delimiter=',')
            for row in df.itertuples():
                if row.ncurr == 0 or row.nvolt == 0: # piecewise cut on resistance
                    continue
                b = row.Index
                r = row.resistance
                vps = row.avgvolt
                '''
                if b <= b1:
                    if streamerON and 1472 < r or r < 1452 or vps < 120000.:
                        streamerON = True
                        startStream = b
                    elif 1452 < r < 1472 and vps > 120000. and streamerON:
                        streamerON = False
                        cutONperiod.append([startStream - timedelta(0, 2), b + timedelta(0, 2)])
                        writer.writerow([int(pytime.mktime((startStream - timedelta(0, 2)).timetuple())),
                                     int(pytime.mktime((b + timedelta(0, 2)).timetuple()))])
                '''
                if b <= b1 and (r > 1472 or r < 1452 or vps < 120000.) and not streamerON:
                    streamerON = True
                    startStream = b
                if b <= b1 and (r > 1452 and r < 1472 and vps > 120000.) and streamerON:
                    streamerON = False
                    cutONperiod.append([startStream - timedelta(0, 2), b + timedelta(0, 2)])
                    writer.writerow([int(pytime.mktime((startStream - timedelta(0, 2)).timetuple())),
                                     int(pytime.mktime((b + timedelta(0, 2)).timetuple()))])

                if b > b1 and b < b2 and (r < 1465 or vps < 120000.) and not streamerON:
                    streamerON = True
                    startStream = b
                if b > b1 and b < b2 and (r > 1465 and vps > 120000.) and streamerON:
                    streamerON = False
                    cutONperiod.append([startStream - timedelta(0, 2), b + timedelta(0, 2)])
                    writer.writerow([int(pytime.mktime((startStream - timedelta(0, 2)).timetuple())),
                                     int(pytime.mktime((b + timedelta(0, 2)).timetuple()))])

                if b >= b2 and (r < 1465 or vps < 180000.) and not streamerON:
                    streamerON = True
                    startStream = b
                if b >= b2 and (r > 1465 and vps > 180000.) and streamerON:
                    streamerON = False
                    cutONperiod.append([startStream - timedelta(0, 2), b + timedelta(0, 2)])
                    writer.writerow([int(pytime.mktime((startStream - timedelta(0, 2)).timetuple())),
                                     int(pytime.mktime((b + timedelta(0, 2)).timetuple()))])

