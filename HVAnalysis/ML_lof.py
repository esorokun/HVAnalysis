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
from pyod.models.sod import SOD
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
    df = ernest_writer.fill_nan()
    print(df)
    scaler = MinMaxScaler(feature_range=(0, 1))
    df[['binavgcurr', 'binavgvolt', 'binresistance']] = scaler.fit_transform(df[['avgcurr', 'avgvolt', 'resistance']])
    X = df['binavgcurr'].values.reshape(-1, 1)
    Y = df['binavgvolt'].values.reshape(-1, 1)
    R = df['binresistance'].values.reshape(-1, 1)
    XY = np.concatenate((X, Y, R), axis=1)
    clf_name = 'KNN'
    clf = KNN(method='mean', n_neighbors=50, contamination=0.05)

    clf.fit(XY)
    pred = clf.labels_
    scores = clf.decision_scores_
    print('prediction : ' + str(sum(pred)) + ' / ' + str(len(pred)))
    print(pred)
    print('scores')
    print(scores)
    MyFile = open('data/output/output.txt', 'w')
    for element in pred:
        MyFile.write(str(element))
        MyFile.write('\n')
    MyFile.close()
    df['result'] = pred
    print(df['result'])
    sns.jointplot(x='avgcurr', y='avgvolt', data=df, alpha=1, s=5, hue='result')
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)
