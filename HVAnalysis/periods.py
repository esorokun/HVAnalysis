from datetime import datetime, timedelta
import csv


class UnstablePeriods:
    def __init__(self):
        self._periods = []

    def __str__(self):
        return f"instance of UnstablePeriods with " \
               f"{len(self._periods)} unstable periods"

    def __iter__(self):
        return iter(self._periods)

    def append(self, start_end_pair):
        self._periods.append(start_end_pair)

    def add_safety_buffer(self, n_seconds=2):
        td = timedelta(seconds=n_seconds)
        for per in self._periods:
            per[0] -= td
            per[1] += td

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

    def has_overlap(self) -> bool:
        if len(self._periods) < 2:
            return False
        last_period = self._periods[0]
        for per in self._periods[1:]:
            if per[0] < last_period[1]:
                return True
            last_period = per
        return False

    def remove_overlap(self):
        while self.has_overlap():
            self._merge_overlap()

    def _merge_overlap(self):
        new_periods = []
        i = 0
        b = self._periods[0][0]
        while i < len(self._periods):
            for j in range(i, len(self._periods)):
                if self._periods[i][1] < self._periods[j][0]:
                    new_periods.append([b, self._periods[j - 1][1]])
                    b = self._periods[j][0]
                    i = j - 1
                    break
            i += 1
        new_periods.append([b, self._periods[-1][1]])
        self._periods = new_periods


def to_time_stamp(dt):
    if dt < datetime(2018, 10, 28):
        return int(datetime.timestamp(dt + timedelta(hours=3)))
    return int(datetime.timestamp(dt + timedelta(hours=2)))