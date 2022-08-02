import csv
import pandas as pd
from datetime import datetime, timedelta
import time as pytime
from writing import Writer


class StableData:
    def __init__(self, file_names=None, val_name=None):
        self.file_names = file_names
        self.val_name = val_name

    def _get_data_frame_from_file(self, fn):
        return pd.read_csv(fn, sep=' ', index_col=0, usecols=[0, 1],
                           names=['timestamp', self.val_name])
