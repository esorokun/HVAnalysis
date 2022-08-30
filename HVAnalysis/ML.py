from sklearn.preprocessing import MinMaxScaler, StandardScaler, PowerTransformer, Normalizer
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from dfwrapper import HeinzWrapper, ResistanceWrapper
import conf
from pyod.models.cblof import CBLOF
from sktime.annotation.adapters import PyODAnnotator


class MLDataFrame:
    def __init__(self, data_frame):
        self.data_frame = self._clear_df(data_frame)
        self.trans_df = NotImplemented
        #self.log10_df = self._log10_params()

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

    def for_train(self):
        df = self.data_frame
        df_l = pd.DataFrame({'avgcurr': df['avgcurr'], 'avgvolt': df['avgvolt']})
        return df_l

    def remove_low_val(self):
        df = self.data_frame
        df = df.loc[df['avgvolt'] > 50_000]
        df = df.loc[df['avgcurr'] > 40]
        self.data_frame = df

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

    def normal_dist_data(self):
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

    '''def _log10_params(self):
        df = self.data_frame
        df['logcurr'] = np.log10(df['avgcurr'])
        df['logvolt'] = np.log10(df['avgvolt'])
        df['logcurr'] = df['logcurr'].ffill(axis=0)
        df['logvolt'] = df['logvolt'].ffill(axis=0)
        df_learn = pd.DataFrame({'logcurr': df['logcurr'], 'logvolt': df['logvolt'],
                                 'avgcurr': df['avgcurr'], 'avgvolt': df['avgvolt'],
                                 'resistance': df['resistance']})
        self.log10_df = df_learn
        return self.log10_df'''

    def all_for_ml(self):
        df = self.trans_df
        df_l = pd.DataFrame({'binavgcurr': df['binavgcurr'], 'binavgvolt': df['binavgvolt'],
                             'binresistance': df['binresistance']})
        return df_l

    def curr_volt_for_ml(self):
        df = self.trans_df
        df_l = pd.DataFrame({'binavgcurr': df['binavgcurr'], 'binavgvolt': df['binavgvolt']})
        return df_l

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


class MLTrainSet(MLDataFrame):

    def __init__(self):
        curr_wrapper = HeinzWrapper(conf.curr_train, 'curr')
        volt_wrapper = HeinzWrapper(conf.volt_train, 'volt')
        comb_wrapper = ResistanceWrapper(volt_wrapper, curr_wrapper)
        super().__init__(data_frame=comb_wrapper.data_frame)
        self.train_df = NotImplemented


    def create_train_list(self):
        self.normal_dist_data()
        df = self.data_frame
        alldf = self.curr_volt_for_ml()
        pyod_model = CBLOF(contamination=0.0095)
        pyod_sktime_annotator_curr = PyODAnnotator(pyod_model)
        pyod_sktime_annotator_curr.fit(alldf)
        list_result = pyod_sktime_annotator_curr.predict(alldf)
        df['result'] = list_result
        df.loc[df['avgvolt'] < 50_000, 'result'] = 1
        df.loc[df['avgcurr'] < 40, 'result'] = 1
        list_res = df['result']
        df_l = pd.DataFrame({'avgcurr': df['avgcurr'], 'avgvolt': df['avgvolt']})
        #df_l['result'] = list_res
        self.train_df = df_l
        return list_res


class PlotBuilder:
    def __init__(self, data_frame, list_result):
        self.build_df = self._add_result(data_frame, list_result)

    def _add_result(self, data_frame, list_result):
        data_frame['result'] = list_result
        data_frame['datetime'] = data_frame.index
        self.build_df = data_frame
        return self.build_df

    def build_scatter_plot(self):
        df = self.build_df
        df['datetime'] = df.index
        g = sns.jointplot(x='avgcurr', y='avgvolt', data=df, alpha=1, s=5, hue='result', palette=['b', 'r'])
        mybins = 30
        df_r = df.loc[df['result'] == 1]
        _ = g.ax_marg_x.hist(df_r['avgcurr'], color='r', alpha=.6, bins=mybins * 2)
        _ = g.ax_marg_y.hist(df_r['avgvolt'], color='r', alpha=.6, bins=mybins * 2, orientation="horizontal")
        df_b = df.loc[df['result'] == 0]
        _ = g.ax_marg_x.hist(df_b['avgcurr'], color='b', alpha=.6, bins=mybins)
        _ = g.ax_marg_y.hist(df_b['avgvolt'], color='b', alpha=.6, bins=mybins, orientation="horizontal")
        plt.show()

    def build_datetime_plot(self, name):
        df = self.build_df
        df_red = df.loc[df['result'] != 0]
        df_blue = df.loc[df['result'] == 0]
        fig, axes = plt.subplots(1, 2)
        fig = sns.scatterplot(x='datetime', y=name, data=df_red, s=2, color='r', ax=axes[0])
        axes = sns.scatterplot(x='datetime', y=name, s=2, data=df_blue, color='b', ax=axes[1])
        plt.show()