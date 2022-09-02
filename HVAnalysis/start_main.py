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
    '''
    df['checker_30sec'] = np.abs((df['avgcurr'].shift(-15) - df['avgcurr'].shift(15)) / 60)
    df['checker_60sec'] = np.abs((df['avgcurr'].shift(-30) - df['avgcurr'].shift(30))/120)
    df['checker_120sec'] = np.abs((df['avgcurr'].shift(-60) - df['avgcurr'].shift(60)) / 240)
    df['checker_240sec'] = np.abs((df['avgcurr'].shift(-120) - df['avgcurr'].shift(120)) / 480)
    df['checker'] = np.sqrt((df['checker_30sec']**2*2 + df['checker_60sec']**2*4
                     + df['checker_120sec']**2*8 + df['checker_240sec']**2*16)/30)
    '''

    #df['checker_long'] = np.abs((df['avgcurr'].shift(-600) - df['avgcurr'].shift(600)) / 2400)

    new_df = df.copy()
    new_df['datetime'] = new_df.index
    new_df = new_df.reset_index()
    new_df['num'] = new_df.index
    new_df = new_df.loc[new_df['num'] % 120 == 0]
    new_df['checker'] = np.abs((new_df['avgcurr'].shift(-1) - new_df['avgcurr'].shift(1)) / 240)
    new_df = new_df.set_index('datetime')
    df = df.join(new_df[['checker']])
    df = df.ffill(axis=0)
    df = df.bfill(axis=0)
    print(df)
    df.loc[np.abs(df['checker']) < 0.001, 'result_curr'] = 0
    df.loc[df['result_curr'] != 0, 'result_curr'] = 1
    df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(-1) * 1.01), 'result_curr'] = 1
    df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(1) * 1.01), 'result_curr'] = 1
    print(df['result_curr'].sum())
    print(df['result_curr'])

    '''
    #df['checker_30sec'] = np.abs((df['avgvolt'].shift(-15) - df['avgvolt'].shift(15)) / 60)
    df['checker_60sec'] = np.abs((df['avgvolt'].shift(-30) - df['avgvolt'].shift(30)) / 120)
    df['checker_120sec'] = np.abs((df['avgvolt'].shift(-60) - df['avgvolt'].shift(60)) / 240)
    df['checker_240sec'] = np.abs((df['avgvolt'].shift(-120) - df['avgvolt'].shift(120)) / 480)
    df['checker_480sec'] = np.abs((df['avgvolt'].shift(-240) - df['avgvolt'].shift(240)) / 960)
    df['checker'] = np.sqrt((df['checker_60sec'] ** 2 * 2 + df['checker_120sec'] ** 2 * 4
                             + df['checker_240sec'] ** 2 * 8 + df['checker_480sec'] ** 2 * 16) / 30)
    df.loc[df['checker'] < 0.25, 'result_volt'] = 0
    df.loc[df['result_volt'] != 0, 'result_volt'] = 1
    df.loc[np.abs(df['avgvolt']) > np.abs(df['avgvolt'].shift(-1) * 1.05), 'result_volt'] = 1
    df.loc[np.abs(df['avgvolt']) > np.abs(df['avgvolt'].shift(1) * 1.05), 'result_volt'] = 1
    '''

    #df['result'] = df['result_volt']
    df.loc[df['result_curr'] == 1, 'result'] = 1
    df['datetime'] = df.index
    length = int(len(df))
    unstable = int(df['result_curr'].sum())
    perc = np.round(unstable/length, 2)
    print(str(perc) + "%\n" + str(100 - perc) + "%")
    sns.jointplot(x='datetime', y='avgcurr', data=df, alpha=1, s=5, hue='result_curr')
    plt.show()
    #ml_plot = PlotBuilder(df, df['result'])
    #ml_plot.build_scatter_plot()'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)