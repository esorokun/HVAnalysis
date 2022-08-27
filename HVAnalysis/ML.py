from sklearn.preprocessing import MinMaxScaler, StandardScaler, PowerTransformer, Normalizer
import numpy as np
import pandas as pd


class MLDataFrame:
    def __init__(self, data_frame):
        self.data_frame = self._clear_df(data_frame)
        self.trans_df = self._normal_dist_data()
        self.log10_df = self._log10_params()

    def __str__(self):
        df = "data for ML :   " + str(self.data_frame.first_valid_index()) \
            + " || " + str(self.data_frame.last_valid_index()) + "\n"
        return df

    def _clear_df(self, df):
        del df['ncurr']
        del df['nvolt']
        del df['sumvolt']
        del df['sumcurr']
        del df['stable_original']
        self.data_frame = df
        return self.data_frame

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
        return self.trans_df

    def _normal_dist_data(self):
        df = self.data_frame
        scaler = PowerTransformer(copy=False)
        df.loc[df['avgcurr'] < 0, 'avgcurr'] = 0
        df.loc[df['avgcurr'] > 300, 'avgcurr'] = 300
        df.loc[df['avgvolt'] < 0, 'avgvolt'] = 0
        df.loc[df['avgvolt'] > 500_000, 'avgvolt'] = 500_000
        df.loc[df['resistance'] < 0, 'resistance'] = 0
        df.loc[df['resistance'] > 10_000, 'resistance'] = 10_000
        scaler.fit(df[['avgcurr', 'avgvolt', 'resistance']])
        df[['binavgcurr', 'binavgvolt', 'binresistance']] = scaler.transform(
            df[['avgcurr', 'avgvolt', 'resistance']])
        df_learn = pd.DataFrame({'binavgcurr': df['binavgcurr'], 'binavgvolt': df['binavgvolt'],
                                 'binresistance': df['binresistance']})
        self.trans_df = df_learn
        return self.trans_df

    def _log10_params(self):
        df = self.data_frame
        df['logcurr'] = np.log10(df['avgcurr'])
        df['logvolt'] = np.log10(df['avgvolt'])
        df['logcurr'] = df['logcurr'].ffill(axis=0)
        df['logvolt'] = df['logvolt'].ffill(axis=0)
        df_learn = pd.DataFrame({'logcurr': df['logcurr'], 'logvolt': df['logvolt'],
                                 'avgcurr': df['avgcurr'], 'avgvolt': df['avgvolt'],
                                 'resistance': df['resistance']})
        self.log10_df = df_learn
        return self.log10_df

    def curr_for_ml(self):
        df = self.trans_df
        df_l = pd.DataFrame({'binavgcurr': df['binavgcurr']})
        return df_l

    def volt_for_ml(self):
        df = self.trans_df
        df_l = pd.DataFrame({'binavgvolt': df['binavgvolt']})
        return df_l

    def resistance_for_ml(self):
        df = self.trans_df.copy()
        df_l = pd.DataFrame({'binresistance': df['binresistance']})
        return df_l

    def add_unix_time_from_index(self, df):
        df['time_to_unix'] = (df.index.astype('uint64') / 1_000_000_000).astype(np.int64)

    def connect_two_df(self, df1, df2):
        df_first = df1
        df_second = df2
        df_res = df_first.merge(df_second, left_index=True, right_index=True)
        return df_res

