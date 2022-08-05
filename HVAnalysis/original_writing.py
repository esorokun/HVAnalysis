import csv
from datetime import datetime, timedelta
import time as pytime


class Writer:
    def __init__(self, df_wrapper, file_name):
        self.df_wrapper = df_wrapper
        self.file_name = file_name

    def write_streamer_periods(self):
        df = self.df_wrapper.data_frame

        start_time = pytime.time()
        b1 = datetime(2018, 10, 5, 0, 0, 0)    #2018-10-05 00:00:00
        b2 = datetime(2018, 10, 17, 12, 0, 0)  #2018-10-17 12:00:00
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


                '''elif b == last:
                    cutONperiod.append([startStream - timedelta(0, 2), b])
                    streamerON = False
                    writer.writerow([int(pytime.mktime((startStream - timedelta(0, 2)).timetuple())),
                                    int(pytime.mktime(b.timetuple()))])'''

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

        print("--- %s seconds ---" % (pytime.time() - start_time))


class LinosWriter:
    """I'm trying to reproduce the results in ProtoDUNEUnstableHVFilter.fcl
    with this class."""
    def __init__(self, df_wrapper, file_name):
        self.df_wrapper = df_wrapper
        self.file_name = file_name

    def write_streamer_periods(self):
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
                unstable_periods.append([start_stream - timedelta(0, 2), b + timedelta(0, 2)])

            if b1 < b < b2 and (r < 1465 or vps < 120000.) and not streamer_on:
                streamer_on = True
                start_stream = b

            if b1 < b < b2 and (r > 1465 and vps > 120000.) and streamer_on:
                streamer_on = False
                unstable_periods.append([start_stream - timedelta(0, 2), b + timedelta(0, 2)])

            if b >= b2 and (r < 1465 or vps < 180000.) and not streamer_on:
                streamer_on = True
                start_stream = b

            if b >= b2 and (r > 1465 and vps > 180000.) and streamer_on:
                streamer_on = False
                unstable_periods.append([start_stream - timedelta(0, 2), b + timedelta(0, 2)])

        # write the last unstable period
        if streamer_on:
            end_time = datetime(b.year, b.month, b.day+1, 1, 0, 59)
            unstable_periods.append([start_stream - timedelta(0, 2), end_time + timedelta(0, 2)])

        with open(self.file_name, mode='w') as f:
            writer = csv.writer(f, delimiter=',')
            for u_p in unstable_periods:
                row = [to_time_stamp(dt) for dt in u_p]
                writer.writerow(row)


def to_time_stamp(dt):
    if dt < datetime(2018, 10, 28):
        return int(datetime.timestamp(dt + timedelta(hours=2)))
    return int(datetime.timestamp(dt + timedelta(hours=1)))
