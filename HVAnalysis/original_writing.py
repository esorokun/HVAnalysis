import csv
from datetime import datetime, timedelta
import time as pytime


class Writer:
    def __init__(self, df_wrapper, file_name):
        self.df_wrapper = df_wrapper
        self.file_name = file_name

    def write_streamer_periods(self):
        b1 = datetime(2018, 10, 5, 0, 0, 0)    #2018-10-05 00:00:00
        b2 = datetime(2018, 10, 17, 12, 0, 0)  #2018-10-17 12:00:00
        df = self.df_wrapper.data_frame
        streamerON = False
        cutONperiod = []
        with open(self.file_name, mode='w') as f:
            writer = csv.writer(f, delimiter=',')
            last = df.last_valid_index()
            for row in df.itertuples():
                if row.ncurr == 0 or row.nvolt == 0:
                    continue
                # piecewise cut on resistance
                b = row.Index
                r = row.resistance
                vps = row.avgvolt
                if b <= b1 and (r > 1472 or r < 1452 or vps < 120000.) and not streamerON:
                    streamerON = True
                    startStream = b

                elif b == last:
                    cutONperiod.append([startStream - timedelta(0, 2), b])
                    streamerON = False
                    writer.writerow([int(pytime.mktime((startStream - timedelta(0, 2)).timetuple())),
                                    int(pytime.mktime(b.timetuple()))])

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