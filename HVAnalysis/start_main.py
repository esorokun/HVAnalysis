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
    df = curr_wrapper.data_frame.copy()
    df['datetime'] = df.index
    df['timedelta'] = df['datetime'] - df['datetime'].shift(+1)
    df['res'] = df['timedelta'] >= datetime.timedelta(seconds=59)
    df = df[df['res']]
    print(df)
    # mldf = MLDataFrame(comb_wrapper.data_frame)
    # df = mldf.data_frame
    #
    # curr = CurrNumDiff(df)
    # curr_l = curr.get_result_list()
    # volt = VoltNumDiff(df)
    # volt_l = volt.get_result_list()
    #
    # volt_l.loc[curr_l['result'] == 1, 'result'] = 1
    # df['result'] = volt_l['result']
    #
    sns.scatterplot(data=df, x='datetime', y='curr', alpha=1, s=10, hue='res')
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)