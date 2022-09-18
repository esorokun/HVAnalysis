import numpy as np
import pandas as pd
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
from num_diff import NumDiff, CurrNumDiff, VoltNumDiff, ResNumDiff
from plotting import Plotter
import datetime
#from pycaret.anomaly
from pyod.models.cblof import CBLOF
from sktime.annotation.adapters import PyODAnnotator


def second(df):

    df_res = df.copy()
    new_df = df.copy()
    new_df['datetime'] = new_df.index
    new_df = new_df.reset_index()
    new_df['num'] = new_df.index

    new_df = new_df.loc[new_df['num'] % 60 == 0]
    new_df = new_df.drop([0])
    datelist = new_df['datetime']

    new_df = new_df.set_index('datetime')
    df = df.join(new_df[['num']])
    df = df.ffill(axis=0)
    df = df.bfill(axis=0)
    df['datetime'] = df.index

    df = df.loc[np.abs(df['avgcurr']) < np.abs(df['avgcurr'].shift(1) * 1.05)]
    df = df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(1) * 0.95)]
    df = df.loc[np.abs(df['avgcurr']) < np.abs(df['avgcurr'].shift(-1) * 1.05)]
    df = df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(-1) * 0.95)]
    df = df.loc[np.abs(df['avgcurr']) < np.abs(df['avgcurr'].shift(120) * 1.05)]
    df = df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(120) * 0.95)]
    df = df.loc[np.abs(df['avgcurr']) < np.abs(df['avgcurr'].shift(-120) * 1.05)]
    df = df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(-120) * 0.95)]
    new_df = df.groupby(['num']).mean()
    new_df = new_df.join(datelist)

    new_df['checker_left'] = np.abs((new_df['avgcurr'].shift(-1) - new_df['avgcurr']) / 60)
    new_df['checker_right'] = np.abs((new_df['avgcurr'].shift(1) - new_df['avgcurr']) / 60)
    new_df['checker'] = (np.abs(new_df['checker_left']) + np.abs(new_df['checker_right']))/2
    new_df = new_df.set_index('datetime')
    df = df_res
    df = df.join(new_df[['checker']])
    new_df = new_df.rename(columns={"avgcurr": "meancurr"})
    df = df.join(new_df[['meancurr']])
    df = df.ffill(axis=0)
    df = df.bfill(axis=0)
    df.loc[np.abs(df['checker']) < 0.01, 'result_curr'] = 0
    df.loc[df['result_curr'] != 0, 'result_curr'] = 1
    df.loc[np.abs(df['avgcurr']) > np.abs(df['meancurr'] * 1.025), 'result_curr'] = 1
    df.loc[np.abs(df['avgcurr']) < np.abs(df['meancurr'] * 0.975), 'result_curr'] = 1

    df.loc[df['result_curr'] == 1, 'result'] = 1
    df.loc[df['result'] != 1, 'result'] = 0
    df['datetime'] = df.index
    length = int(len(df))
    unstable = int(df['result_curr'].sum())
    perc = np.round(unstable / length, 2)
    print(str(perc) + "%\n" + str(100 - perc) + "%")

    df['datetime'] = df.index
    sns.scatterplot(x='datetime', y='avgcurr', data=df, alpha=1, s=5, hue='result')
    plt.show()

def main(args):

    conf.configure_from_args(args)

    curr_wrapper = HeinzWrapper(conf.curr_file_names, 'curr')
    volt_wrapper = HeinzWrapper(conf.volt_file_names, 'volt')
    comb_wrapper = ResistanceWrapper(volt_wrapper, curr_wrapper)

    df = comb_wrapper.data_frame
    #df['datetime'] = df.index
    df.loc[df['stable_original'], 'result'] = 0
    df.loc[~df['stable_original'], 'result'] = 1
    df = df.loc[df['stable_original']]
    #df = comb_wrapper.data_frame
    #length = int(len(df))
    #df.loc[df['stable_original'], 'result'] = 0
    #df.loc[df['result'] != 0, 'result'] = 1
    #unstable = int(df['result'].sum())
    #perc = np.round(unstable / length, 2)
    #print("unstable: " + str(perc) + "%\n" + "stable:   " + str(100 - perc) + "%")
    #df['datetime'] = df.index
    #sns.scatterplot(x='datetime', y='avgvolt', data=df, alpha=1, s=5, hue='result')
    #plt.show()

    #mldf = MLDataFrame(comb_wrapper.data_frame)
    #mldf.normal_dist_data()
    #df = mldf.data_frame
    #volt = VoltNumDiff(df)
    #volt.show_plot()
    '''
    curr = CurrNumDiff(df)
    curr_l = curr.get_result_list()
    volt = VoltNumDiff(df)
    volt_l = volt.get_result_list()

    df['result'] = curr_l
    df.loc[volt_l['result'] == 1, 'result'] = 1
    length = len(df)
    unstable = int(df['result'].sum())
    perc = np.round(unstable / length, 2)
    print("unstable: " + str(perc) + "%\n" + "stable:   " + str(100 - perc) + "%")
    print(df)
    df = df.loc[df['result'] == 0]
    sns.scatterplot(x='avgcurr', y='avgvolt', data=df, alpha=0.8, s=5, hue='result')
    '''
    '''
    g = sns.scatterplot(x='avgcurr', y='avgvolt', data=df, alpha=0.8, s=5, hue='stable_original')
    
    mybins = 30
    df_r = df[df['stable_original']]
    df_b = df[~df['stable_original']]
    _ = g.ax_marg_x.hist(df_r['avgcurr'], color='r', alpha=.6, bins=mybins * 2)
    _ = g.ax_marg_y.hist(df_r['avgvolt'], color='r', alpha=.6, bins=mybins * 2, orientation="horizontal")
    _ = g.ax_marg_x.hist(df_b['avgcurr'], color='b', alpha=.6, bins=mybins)
    _ = g.ax_marg_y.hist(df_b['avgvolt'], color='b', alpha=.6, bins=mybins, orientation="horizontal")
    '''
    g = sns.scatterplot(x='avgcurr', y='avgvolt', data=df, alpha=0.8, s=5, hue='result')
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)