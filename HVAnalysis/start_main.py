import numpy as np
import pandas as pd
from pyod.models.cblof import CBLOF
from sklearn.preprocessing import MinMaxScaler
from sktime.clustering.k_means import TimeSeriesKMeans
from sktime.clustering.k_medoids import TimeSeriesKMedoids
from sktime.clustering.k_shapes import TimeSeriesKShapes
from sktime.clustering.kernel_k_means import TimeSeriesKernelKMeans
from sktime.clustering.partitioning import TimeSeriesLloyds
from sktime.transformations.panel.summarize import PlateauFinder

from ML import MLDataFrame, PlotBuilder, MLTrainSet
import sktime.clustering
from dfwrapper import HeinzWrapper, ResistanceWrapper
import argparse
import conf
import matplotlib.pyplot as plt
import seaborn as sns
from var_corr import VarCorr, Poly1d
from num_diff import NumDiff, CurrNumDiff, VoltNumDiff, ResNumDiff, Timedelta
from plotting import Plotter
import datetime
#from pycaret.anomaly
from pyod.models.cblof import CBLOF
from sktime.annotation.adapters import PyODAnnotator

def main(args):

    conf.configure_from_args(args)

    curr_wrapper = HeinzWrapper(conf.curr_file_names, 'curr')
    volt_wrapper = HeinzWrapper(conf.volt_file_names, 'volt')
    comb_wrapper = ResistanceWrapper(volt_wrapper, curr_wrapper)
    df_original = comb_wrapper.data_frame
    new = Timedelta(df_original)
    df_original = new.transformed_df
    del df_original['ncurr']
    del df_original['nvolt']
    del df_original['sumvolt']
    del df_original['sumcurr']
    del df_original['resistance']
    del df_original['stable_original']
    df = df_original.copy()
    poly1 = Poly1d(df, 'avgvolt', 216, 141.4158)
    df1 = poly1.mean_filtering()
    poly2 = Poly1d(df, 'avgvolt', 759, 141.4158)
    df2 = poly2.mean_filtering()
    poly3 = Poly1d(df, 'avgvolt', 1120, 141.4158)
    df3 = poly3.mean_filtering()
    poly4 = Poly1d(df, 'avgvolt', 1719, 141.4158)
    df4 = poly4.mean_filtering()
    poly_fall = Poly1d(df, 'avgvolt', 20, 141.4158)
    dff = poly_fall.mean_filtering()
    df_sig = pd.DataFrame({'sigma_50': df1['height'],
                           'sigma_100': df2['height'],
                           'sigma_150': df3['height'],
                           'sigma_200': df4['height']})
    df_mean = pd.DataFrame({'sigma_50': df1['meanvalue'],
                           'sigma_100': df2['meanvalue'],
                           'sigma_150': df3['meanvalue'],
                           'sigma_200': df4['meanvalue']})
    df_mean['meanvalue'] = np.sqrt((df_mean['sigma_50'] ** 2 + df_mean['sigma_100'] ** 2 +
                                      df_mean['sigma_150'] ** 2 + df_mean['sigma_200'] ** 2) / 4)
    df_mean['start_avg'] = df['avgvolt']
    df_sig['res_sigma_sq'] = np.sqrt((df_sig['sigma_50']**2 + df_sig['sigma_100']**2 +
                                      df_sig['sigma_150']**2 + df_sig['sigma_200']**2)/4)
    print(df_mean['meanvalue'])
    df_sig.loc[df_sig['res_sigma_sq'] < 141.4158, 'result'] = 0
    df_sig.loc[df_sig['result'] != 0, 'result'] = 1
    df = df.join(df_sig['result'])
    df = df.join(df_mean['meanvalue'])
    df = df.join(df_mean['sigma_50'])
    df = df.join(dff['height'])
    df['new_result'] = df['result']
    df.loc[(df['result'] == 0) & (np.abs(df['avgvolt'] - df['sigma_50']) > 2.5*141.4158), 'new_result'] = 1
    df.loc[(df['result'].shift(500) == 0) & (df['result'] == 1) &
           ((np.abs(df['avgvolt'] - df['sigma_50'].shift(2000))) < (2*141.4158)), 'new_result'] = 0
    df.loc[(df['result'].shift(-500) == 0) & (df['result'] == 1) &
           ((np.abs(df['avgvolt'] - df['sigma_50'].shift(-2000))) < (2*141.4158)), 'new_result'] = 0
    df.loc[np.abs(df['height']) > 500, 'new_result'] = 1
    df.loc[(df['result'] == 0) & (np.abs(df['avgvolt'] - df['avgvolt'].shift(5)) > 550), 'new_result'] = 1
    df.loc[(df['result'] == 0) & (np.abs(df['avgvolt'] - df['avgvolt'].shift(-5)) > 550), 'new_result'] = 1

    df_original['volt_result'] = df['new_result']
    df = df_original.copy()
    poly1 = Poly1d(df, 'avgcurr', 216, 1.16687)
    df1 = poly1.mean_filtering()
    poly2 = Poly1d(df, 'avgcurr', 759, 1.16687)
    df2 = poly2.mean_filtering()
    poly3 = Poly1d(df, 'avgcurr', 1120, 1.16687)
    df3 = poly3.mean_filtering()
    poly4 = Poly1d(df, 'avgcurr', 1719, 1.16687)
    df4 = poly4.mean_filtering()
    poly_fall = Poly1d(df, 'avgcurr', 20, 1.16687)
    dff = poly_fall.mean_filtering()
    df_sig = pd.DataFrame({'sigma_50': df1['height'],
                           'sigma_100': df2['height'],
                           'sigma_150': df3['height'],
                           'sigma_200': df4['height']})
    df_mean = pd.DataFrame({'sigma_50': df1['meanvalue'],
                            'sigma_100': df2['meanvalue'],
                            'sigma_150': df3['meanvalue'],
                            'sigma_200': df4['meanvalue']})
    df_mean['meanvalue'] = np.sqrt((df_mean['sigma_50'] ** 2 + df_mean['sigma_100'] ** 2 +
                                    df_mean['sigma_150'] ** 2 + df_mean['sigma_200'] ** 2) / 4)
    df_mean['start_avg'] = df['avgcurr']
    df_sig['res_sigma_sq'] = np.sqrt((df_sig['sigma_50'] ** 2 + df_sig['sigma_100'] ** 2 +
                                      df_sig['sigma_150'] ** 2 + df_sig['sigma_200'] ** 2) / 4)
    print(df_mean['meanvalue'])
    df_sig.loc[df_sig['res_sigma_sq'] < 1.16687, 'result'] = 0
    df_sig.loc[df_sig['result'] != 0, 'result'] = 1
    df = df.join(df_sig['result'])
    df = df.join(df_mean['meanvalue'])
    df = df.join(df_mean['sigma_50'])
    df = df.join(dff['height'])
    df['new_result'] = df['result']
    df.loc[(df['result'] == 0) & (np.abs(df['avgcurr'] - df['sigma_50']) > 2 * 1.16687), 'new_result'] = 1
    df.loc[(df['result'].shift(500) == 0) & (df['result'] == 1) &
           ((np.abs(df['avgcurr'] - df['sigma_50'].shift(2000))) < (2 * 1.16687)), 'new_result'] = 0
    df.loc[(df['result'].shift(-500) == 0) & (df['result'] == 1) &
           ((np.abs(df['avgcurr'] - df['sigma_50'].shift(-2000))) < (2 * 1.16687)), 'new_result'] = 0
    df.loc[np.abs(df['height']) > 5, 'new_result'] = 1
    df.loc[(df['result'] == 0) & (np.abs(df['avgcurr'] - df['avgcurr'].shift(5)) > 5), 'new_result'] = 1
    df.loc[(df['result'] == 0) & (np.abs(df['avgcurr'] - df['avgcurr'].shift(-5)) > 5), 'new_result'] = 1

    df_original['curr_result'] = df['new_result']
    df_original.loc[df_original['avgcurr'] < 10, 'curr_result'] = 1
    df_original.loc[df_original['avgvolt'] < 1000, 'volt_result'] = 1
    df_original.loc[(df_original['volt_result'] == 0) & (df_original['curr_result'] == 0), 'final_result'] = 0
    df_original.loc[df_original['final_result'] != 0, 'final_result'] = 1
    df_original.loc[(df_original['volt_result'] == 0) & (df_original['curr_result'] == 0), 'counter'] = 1
    df_original.loc[df_original['counter'] != 1, 'counter'] = 0
    stable = df_original['counter'].sum()
    unstable = df_original['final_result'].sum()
    print(round(stable/(stable+unstable), 6))

    g = sns.jointplot(x='avgcurr', y='avgvolt', data=df_original, hue='final_result', palette=['b', 'r'],
                      s=3, alpha=0.1, marginal_ticks=True, height=8, ratio=4)
    mybins = 30
    _ = g.ax_marg_x.hist(df_original.loc[df_original['final_result'] == 1, 'avgcurr'], color='r', alpha=.6, bins=mybins * 2)
    _ = g.ax_marg_y.hist(df_original.loc[df_original['final_result'] == 1, 'avgvolt'], color='r', alpha=.6, bins=mybins * 2, orientation="horizontal")
    _ = g.ax_marg_x.hist(df_original.loc[df_original['final_result'] == 0, 'avgcurr'], color='b', alpha=.6, bins=mybins)
    _ = g.ax_marg_y.hist(df_original.loc[df_original['final_result'] == 0, 'avgvolt'], color='b', alpha=.6, bins=mybins, orientation="horizontal")
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)