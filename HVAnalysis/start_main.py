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
from var_corr import VarCorr
from num_diff import NumDiff, CurrNumDiff, VoltNumDiff, ResNumDiff
from plotting import Plotter
import datetime
#from pycaret.anomaly
from pyod.models.cblof import CBLOF
from sktime.annotation.adapters import PyODAnnotator

def main(args):

    conf.configure_from_args(args)

    wrapper_curr = HeinzWrapper(conf.curr_file_names, 'curr')
    df = wrapper_curr.data_frame
    mel = VarCorr(df, 'curr', 300)
    df_n = mel.mean_filtering()
    df_n = df_n.reset_index()
    df_n['avgsec'] = df_n.index
    i = 5
    k = 0
    num = 0
    lvi = df_n.last_valid_index()
    while lvi >= i:
        x = df_n.loc[(df_n.index <= i)*(df_n.index >= k), 'curr'].values
        y = df_n.loc[(df_n.index <= i)*(df_n.index >= k), 'avgsec'].values
        if np.abs((np.corrcoef(x=x, y=y))[0][1]) < 0.1:
            df_n.loc[(df_n.index <= i) * (df_n.index >= k), 'skrat'] = num
            if num == 0:
                num = 1
            else:
                num = 0
            if np.sqrt(np.var(x)) <= 1.56687:
                df_n.loc[(df_n.index <= i)*(df_n.index >= k), 'result'] = 'blue'
            else:
                df_n.loc[(df_n.index <= i) * (df_n.index >= k), 'result'] = 'red'
            k = i
        i += 1
    sns.scatterplot(data=df_n, x='datetime', y='curr', alpha=1, s=5, hue='skrat')
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)