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
    wrapper = ResistanceWrapper(volt_wrapper, curr_wrapper)
    df = wrapper.data_frame
    df = df.loc[(df['nvolt'] != 0) & (df['ncurr'] != 0)]
    df['datetime'] = (df.index.astype('uint64') / 1_000_000_000).astype(np.int64)
    df['datetime_next'] = df['datetime'].shift(+1)
    df = df.bfill(axis=0)
    df['timedelta'] = df['datetime'] - df['datetime_next']
    print(df)
    #sns.scatterplot(data=df_o, x='datetime_original', y='avgcurr_original', alpha=1, s=5, hue='result')
    #plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)