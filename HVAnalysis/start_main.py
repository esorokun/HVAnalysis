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

def main(args):

    conf.configure_from_args(args)

    curr_wrapper = HeinzWrapper(conf.curr_file_names, 'curr')
    #volt_wrapper = HeinzWrapper(conf.volt_file_names, 'volt')
    #comb_wrapper = ResistanceWrapper(volt_wrapper, curr_wrapper)

    seconds = 200
    df_c = curr_wrapper.data_frame.copy()
    df_c['datetime'] = df_c.index
    df = curr_wrapper.data_frame.copy()
    df['datetime'] = df.index
    df = df.reset_index()
    df['num'] = df.index

    df = df.loc[df['num'] % seconds == 0]
    df = df.drop([0])
    datelist = df['datetime']
    df = df.set_index('datetime')
    df = curr_wrapper.data_frame.copy().join(df[['num']])
    df = df.ffill(axis=0)
    df = df.bfill(axis=0)
    new_df = np.sqrt(df.groupby(['num']).var())
    new_df['mean'] = df.groupby(['num']).mean()
    new_df['const'] = new_df['mean']/new_df['curr']
    new_df['result'] = new_df['curr'] < 0.35
    new_df['datetime'] = datelist
    new_df.rename(columns={'var': 'curr'})
    new_df = new_df.set_index('datetime')
    #n = 100000
    #df = df.head(n)
    #x = df['curr'].values
    #var = np.sqrt(np.var(x))
    #mean = np.mean(x)
    #print(f'var = {var.round(4)}')
    #df.loc[(df['curr'] > (mean - var*3)) & (df['curr'] < (mean + var*3)), 'result'] = 1
    #df.loc[df['result'] != 1, 'result'] = 0
    sns.scatterplot(data=new_df, x='datetime', y='mean', alpha=1, s=5, hue='result')
    #sns.scatterplot(data=df_c, x='datetime', y='curr', alpha=1, s=5)
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)