from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd


class MLDataFrame:
    def __init__(self, data_frame):
        self.data_frame = data_frame
        self.trans_df = NotImplemented
        self.log10_df = NotImplemented


    def transform_data(self):
        df = self.data_frame
        scaler = MinMaxScaler(feature_range=(0, 1))
        df[['binavgcurr', 'binavgvolt', 'binresistance']] = scaler.fit_transform(
            df[['avgcurr', 'avgvolt', 'resistance']])
        df['binavgcurr'] = df['binavgcurr'].values.reshape(-1, 1)
        df['binavgvolt'] = df['binavgvolt'].values.reshape(-1, 1)
        df['binresistance'] = df['binresistance'].values.reshape(-1, 1)
        df_learn = pd.DataFrame({'binavgcurr': df['binavgcurr'], 'binavgvolt': df['binavgvolt'],
                                 'binresistance': df['binresistance']})
        self.trans_df = df_learn

    def add_log10_params(self):
        df = self.data_frame
        df['logcurr'] = np.log10(df['avgcurr'])
        df['logvolt'] = np.log10(df['avgvolt'])
        df['logcurr'] = df['logcurr'].ffill(axis=0)
        df['logvolt'] = df['logvolt'].ffill(axis=0)
        df_learn = pd.DataFrame({'logcurr': df['logcurr'], 'logvolt': df['logvolt'],
                                 'avgcurr': df['avgcurr'], 'avgvolt': df['avgvolt'],
                                 'resistance': df['resistance']})
        self.log10_df = df_learn

    def add_unix_time_from_index(self, df):
        df['time_to_unix'] = (df.index.astype('uint64') / 1_000_000_000).astype(np.int64)

    def connect_two_df(self, df1, df2):
        df_first = df1
        df_second = df2
        df_res = df_first.merge(df_second, left_index=True, right_index=True)
        return df_res

