from datetime import datetime, timedelta
import csv


class UnstablePeriods:
    def __init__(self):
        self._periods = []

    def __str__(self):
        return f"instance of UnstablePeriods with " \
               f"{len(self._periods)} unstable periods"

    def append(self, start_end_pair):
        self._periods.append(start_end_pair)

    def write_to_file(self, file_name):
        with open(file_name, mode='w') as f:
            writer = csv.writer(f, delimiter=',')
            for per in self._periods:
                writer.writerow([to_time_stamp(dt) for dt in per])

    def get_unstable_seconds(self) -> set:
        unstable_seconds = set()
        for per in self._periods:
            dt = per[0]
            while dt < per[1]:
                unstable_seconds.add(dt)
                dt += timedelta(seconds=1)
        return unstable_seconds


def to_time_stamp(dt):
    if dt < datetime(2018, 10, 28):
        return int(datetime.timestamp(dt + timedelta(hours=3)))
    return int(datetime.timestamp(dt + timedelta(hours=2)))
