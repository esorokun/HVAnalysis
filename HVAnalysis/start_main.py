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
from var_corr import VarCorr, Poly1d
from num_diff import NumDiff, CurrNumDiff, VoltNumDiff, ResNumDiff
from plotting import Plotter
import datetime
#from pycaret.anomaly
from pyod.models.cblof import CBLOF
from sktime.annotation.adapters import PyODAnnotator

def main(args):

    conf.configure_from_args(args)
    curr_wrapper = HeinzWrapper(conf.curr_file_names, 'curr')
    c = curr_wrapper.resample_count('S')
    df1 = curr_wrapper.resample_value('S')
    df1 = df1.join(c)
    df1 = df1.loc[df1['ncurr'] != 0]
    df1['avgcurr'] = df1['sumcurr'] / df1['ncurr']
    df1.loc[df1.index, 'datetime'] = df1.index

    wrapper = HeinzWrapper(conf.GroundPlanes_Ch14, 'curr')
    c = wrapper.resample_count('S')
    df = wrapper.resample_value('S')
    df = df.join(c)
    df['avgcurr'] = df['sumcurr']/df['ncurr']
    df = df.loc[df['ncurr'] != 0]
    df = df.loc[np.abs(df['avgcurr']) > 3.7]
    df.loc[df.index, 'datetime'] = df.index

    df_o = df1.join(df, lsuffix='_original', rsuffix='_called')
    df_o.loc[df_o['datetime_called'] == df_o['datetime_original'], 'result'] = 1
    df_o.loc[df_o['datetime_called'] != df_o['datetime_original'], 'result'] = 0
    #df1.loc[df['datetime'] == df1['datetime'], 'result'] = 1
    print(df)
    print(df1)
    print(df_o)
    # df_curr.loc[df_curr['datetime'] == df['datetime'], 'result'] = 'unstable'
    # df_curr.loc[df_curr['result'] != 'unstable', 'result'] = 'stable'
    sns.scatterplot(data=df_o, x='datetime_original', y='avgcurr_original', alpha=1, s=5, hue='result')
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)