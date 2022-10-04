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
    volt_wrapper = HeinzWrapper(conf.volt_file_names, 'volt')
    res_wrapper = ResistanceWrapper(volt_wrapper, curr_wrapper)
    df_curr = res_wrapper.data_frame
    df_curr = df_curr.loc[df_curr['ncurr'] != 0]
    df_curr['datetime'] = df_curr.index
    wrapper = HeinzWrapper(conf.GroundPlanes_Ch06, 'curr')
    c = wrapper.resample_count('S')
    df = wrapper.resample_value('S')
    df = df.join(c)
    df['avgcurr'] = df['sumcurr']/df['ncurr']
    df = df.loc[df['ncurr'] != 0]
    df = df.loc[np.abs(df['avgcurr']) > 0.001]
    df['datetime'] = df.index
    print(df)
    print(df_curr)
    df1 = df_curr.copy()
    print(df_curr.merge(df, how='inner', on='datetime'))
    print(df_curr[''])
    # df_curr.loc[df_curr['datetime'] == df['datetime'], 'result'] = 'unstable'
    # df_curr.loc[df_curr['result'] != 'unstable', 'result'] = 'stable'
    # sns.scatterplot(data=df_curr, x='datetime', y='avgcurr', alpha=1, s=5, hue='result')
    # plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)