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
    volt_wrapper = HeinzWrapper(conf.volt_file_names, 'volt')
    comb_wrapper = ResistanceWrapper(volt_wrapper, curr_wrapper)

    df = curr_wrapper.data_frame
    df['timeset'] = (df.index.astype('uint64') / 1_000_000_000).astype(np.int64)
    df['datetime'] = df.index
    n = 100000
    df = df.head(n)
    x = df['curr'].values
    y = df['timeset'].values
    corr = np.abs((np.corrcoef(x=x, y=y))[0][1])
    var = np.sqrt(np.var(x))
    mean = np.mean(x)
    print(f'corr = {corr.round(4)}')
    print(f'var = {var.round(4)}')
    df.loc[(df['curr'] > (mean - var*3)) & (df['curr'] < (mean + var*3)), 'result'] = 1
    df.loc[df['result'] != 1, 'result'] = 0
    sns.scatterplot(data=df, x='datetime', y='curr', alpha=1, s=5, hue='result')
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)