import matplotlib
import numpy as np
import pandas as pd
import logging
import argparse
from ML import MLDataFrame
from sktime.transformations.panel.summarize import PlateauFinder

from writing import LinosWriter, ErnestsWriter
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from dfwrapper import HeinzWrapper, ResistanceWrapper
import conf
from sktime.annotation.adapters import PyODAnnotator
from scipy import stats
# Import models
from pyod.models.copod import COPOD
from pyod.models.cblof import CBLOF
from pyod.models.hbos import HBOS
from pyod.models.iforest import IForest
from pyod.models.knn import KNN

from sklearn.preprocessing import MinMaxScaler


def main(args):
    conf.configure_from_args(args)

    curr_wrapper = HeinzWrapper(conf.curr_file_names, 'curr')
    volt_wrapper = HeinzWrapper(conf.volt_file_names, 'volt')
    comb_wrapper = ResistanceWrapper(volt_wrapper, curr_wrapper)
    mldf = MLDataFrame(comb_wrapper.data_frame)
    mldf.transform_data()
    currdf = mldf.curr_for_ml()
    voltdf = mldf.volt_for_ml()
    resdf = mldf.resistance_for_ml()
    currdf['binavgvolt'] = voltdf['binavgvolt']
    df = mldf.data_frame
    pyod_model = CBLOF(contamination=0.2)
    pyod_sktime_annotator_curr = PyODAnnotator(pyod_model)
    pyod_sktime_annotator_curr.fit(resdf)
    currdf['result'] = pyod_sktime_annotator_curr.predict(resdf)
    currdf['datetime'] = currdf.index
    df['result'] = currdf['result']
    #df_red = currdf.loc[currdf['result'] != 0]
    #df_blue = currdf.loc[currdf['result'] == 0]
    #fig, axes = plt.subplots(1, 2)
    #fig = sns.scatterplot(x='datetime', y='binresistance', data=df_red, s=2, color='r', ax=axes[0])
    #axes = sns.scatterplot(x='datetime', y='binresistance', s=2, data=df_blue, color='b', ax=axes[1])
    sns.jointplot(x='avgcurr', y='avgvolt', data=df, alpha=0.2, s=5, hue='result')
    plt.show()
    '''g = sns.jointplot(x='avgcurr', y='avgvolt', data=df, alpha=1, s=5, hue='result', palette=['b', 'r'])
    mybins = 30
    df_r = df.loc[df['result'] == 1]
    _ = g.ax_marg_x.hist(df_r['avgcurr'], color='r', alpha=.6, bins=mybins * 2)
    _ = g.ax_marg_y.hist(df_r['avgvolt'], color='r', alpha=.6, bins=mybins * 2, orientation="horizontal")
    df_b = df.loc[df['result'] == 0]
    _ = g.ax_marg_x.hist(df_b['avgcurr'], color='b', alpha=.6, bins=mybins)
    _ = g.ax_marg_y.hist(df_b['avgvolt'], color='b', alpha=.6, bins=mybins, orientation="horizontal")
    plt.show()'''

    '''df['time_to_stamp'] = (df.index.astype('uint64') / 1_000_000_000).astype(np.int64)
    df['logcurr'] = np.log10(df['avgcurr']*df['avgvolt'])
    df['logvolt'] = np.log10(df['avgvolt'])
    df['logcurr'] = df['logcurr'].ffill(axis=0)
    df['logvolt'] = df['logvolt'].ffill(axis=0)
    scaler = MinMaxScaler(feature_range=(0, 1))
    df[['binavgcurr', 'binavgvolt', 'binresistance', 'bintime', 'binlogcurr', 'binlogvolt']] = scaler.fit_transform(
                    df[['avgcurr', 'avgvolt', 'resistance', 'time_to_stamp', 'logcurr', 'logvolt']])
    X = df['binavgcurr'].values.reshape(-1, 1)
    Y = df['binavgvolt'].values.reshape(-1, 1)
    R = df['binresistance'].values.reshape(-1, 1)
    T = df['bintime'].values.reshape(-1, 1)
    LI = df['binlogcurr'].values.reshape(-1, 1)
    #LV = df['binlogvolt'].values.reshape(-1, 1)
    XY = np.concatenate((X, Y, R, LI), axis=1)
    
    clf = CBLOF()

    clf.fit(XY)
    pred = clf.labels_
    scores = clf.decision_scores_
    print('prediction')
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
    g = sns.jointplot(x='avgcurr', y='avgvolt', data=df, alpha=1, s=5, hue='result')
    mybins = 30
    df_r = df.loc[df['result'] == 1]
    _ = g.ax_marg_x.hist(df_r['avgcurr'], color='r', alpha=.6, bins=mybins * 2)
    _ = g.ax_marg_y.hist(df_r['avgvolt'], color='r', alpha=.6, bins=mybins * 2, orientation="horizontal")
    df_b = df.loc[df['result'] == 0]
    _ = g.ax_marg_x.hist(df_b['avgcurr'], color='b', alpha=.6, bins=mybins)
    _ = g.ax_marg_y.hist(df_b['avgvolt'], color='b', alpha=.6, bins=mybins, orientation="horizontal")
    plt.show()'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)
