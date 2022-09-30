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

    wrapper_curr = HeinzWrapper(conf.curr_file_names, 'curr')
    df = wrapper_curr.data_frame
    mel = Poly1d(df, 'curr', 3600)
    mel.mean_filtering()

    #sns.scatterplot(data=df_n, x='datetime', y='curr', alpha=1, s=5, hue='skrat')
    #plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)