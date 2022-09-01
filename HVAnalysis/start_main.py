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

    mldf = MLDataFrame(comb_wrapper.data_frame)
    mldf.normal_dist_data()
    df = mldf.data_frame
    #df['checker'] = np.abs((df['avgcurr'].shift(-30) - df['avgcurr'].shift(30)) / 120)
    #df['checker_10sec'] = np.abs((df['avgcurr'].shift(-5) - df['avgcurr'].shift(5)) / 20)
    df['checker_30sec'] = np.abs((df['avgcurr'].shift(-15) - df['avgcurr'].shift(15)) / 60)
    df['checker_60sec'] = np.abs((df['avgcurr'].shift(-30) - df['avgcurr'].shift(30))/120)
    df['checker_120sec'] = np.abs((df['avgcurr'].shift(-60) - df['avgcurr'].shift(60)) / 240)
    df['checker_240sec'] = np.abs((df['avgcurr'].shift(-120) - df['avgcurr'].shift(120)) / 480)
    df['checker'] = np.sqrt((df['checker_30sec']**2*2 + df['checker_60sec']**2*4
                     + df['checker_120sec']**2*8 + df['checker_240sec']**2*16)/30)
    #df.loc[df['checker'] > 100, 'checker'] = 100
    #df.loc[df['checker'] < 0.001, 'checker'] = 0.001
    df.loc[df['checker'] < 0.005, 'result'] = 0
    #df.loc[(1.006 > df['checker'])*(df['checker'] > 0.994), 'result'] = 0
    df.loc[df['result'] != 0, 'result'] = 1
    df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(-1)*1.006), 'result'] = 1
    df['datetime'] = df.index
    print(df)
    sns.scatterplot(x='datetime', y='avgcurr', data=df, alpha=1, s=5, hue='result')
    plt.show()
    #ml_plot = PlotBuilder(df, res)
    #ml_plot.build_scatter_plot()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)