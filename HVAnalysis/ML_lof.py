import matplotlib
import numpy as np
import pandas as pd
import logging
import argparse
from writing import LinosWriter, ErnestsWriter
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from dfwrapper import HeinzWrapper, ResistanceWrapper
import conf
from scipy import stats
# Import models
from pyod.models.abod import ABOD
from pyod.models.cblof import CBLOF
from pyod.models.hbos import HBOS
from pyod.models.iforest import IForest
from pyod.models.knn import KNN
from pyod.models.lof import LOF
from sklearn.preprocessing import MinMaxScaler


def main(args):
    conf.configure_from_args(args)

    curr_wrapper = HeinzWrapper(conf.curr_file_names, 'curr')
    volt_wrapper = HeinzWrapper(conf.volt_file_names, 'volt')
    comb_wrapper = ResistanceWrapper(volt_wrapper, curr_wrapper)
    ernest_writer = ErnestsWriter(comb_wrapper, f'{args.outputfolder}/ernests_unstable_periods_remove.csv')
    ernest_writer.fill_nan()
    df = ernest_writer.df_wrapper.data_frame
    scaler = MinMaxScaler(feature_range=(0, 1))
    df[['avgcurr', 'avgvolt']] = scaler.fit_transform(df[['avgcurr', 'avgvolt']])
    X = df['avgcurr'].values.reshape(-1, 1)
    Y = df['avgvolt'].values.reshape(-1, 1)
    XY = np.concatenate((X, Y), axis=1)
    clf_name = 'LOF'
    clf = LOF()

    clf.fit(X)
    pred = clf.labels_
    scores = clf.decision_scores_
    print('prediction')
    print(pred)
    print('scores')
    print(scores)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)
