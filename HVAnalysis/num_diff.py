import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

import conf
from dfwrapper import HeinzWrapper, ResistanceWrapper
from ML import MLDataFrame


def first(df):
    new_df = df.copy()
    new_df['datetime'] = new_df.index
    new_df = new_df.reset_index()
    new_df['num'] = new_df.index
    new_df = new_df.loc[new_df['num'] % 600 == 0]
    new_df['checker'] = np.abs((new_df['avgcurr'].shift(-1) - new_df['avgcurr'].shift(1)) / 1200)
    new_df = new_df.set_index('datetime')
    df = df.join(new_df[['checker']])
    df = df.ffill(axis=0)
    df = df.bfill(axis=0)
    print(df)
    df.loc[np.abs(df['checker']) < 0.001, 'result_curr'] = 0
    df.loc[df['result_curr'] != 0, 'result_curr'] = 1

    df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(-1) * 1.007), 'result_curr'] = 1
    df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(1) * 1.007), 'result_curr'] = 1

    print(df['result_curr'].sum())
    print(df['result_curr'])

    # df['result'] = df['result_volt']
    df.loc[df['result_curr'] == 1, 'result'] = 1
    df.loc[df['result'] != 1, 'result'] = 0
    df['datetime'] = df.index
    length = int(len(df))
    unstable = int(df['result_curr'].sum())
    perc = np.round(unstable / length, 2)
    print(str(perc) + "%\n" + str(100 - perc) + "%")

    df['datetime'] = df.index
    sns.scatterplot(x='datetime', y='avgcurr', data=df, alpha=1, s=5, hue='result')
    plt.show()

def second(df):
    df_res = df.copy()
    new_df = df.copy()
    new_df['datetime'] = new_df.index
    new_df = new_df.reset_index()
    new_df['num'] = new_df.index

    new_df = new_df.loc[new_df['num'] % 60 == 0]
    new_df = new_df.drop([0])
    datelist = new_df['datetime']

    new_df = new_df.set_index('datetime')
    df = df.join(new_df[['num']])
    df = df.ffill(axis=0)
    df = df.bfill(axis=0)

    df['datetime'] = df.index
    '''
    df = df.loc[np.abs(df['avgcurr']) < np.abs(df['avgcurr'].shift(-1) * 1.05)]
    df = df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(-1) * 0.95)]
    df = df.loc[np.abs(df['avgcurr']) < np.abs(df['avgcurr'].shift(1) * 1.05)]
    df = df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(1) * 0.95)]
    df = df.loc[np.abs(df['avgcurr']) < np.abs(df['avgcurr'].shift(-10) * 1.05)]
    df = df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(-10) * 0.95)]
    df = df.loc[np.abs(df['avgcurr']) < np.abs(df['avgcurr'].shift(10) * 1.05)]
    df = df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(10) * 0.95)]
    df = df.loc[np.abs(df['avgcurr']) < np.abs(df['avgcurr'].shift(-20) * 1.05)]
    df = df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(-20) * 0.95)]
    df = df.loc[np.abs(df['avgcurr']) < np.abs(df['avgcurr'].shift(20) * 1.05)]
    df = df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(20) * 0.95)]
    df = df.loc[np.abs(df['avgcurr']) < np.abs(df['avgcurr'].shift(-30) * 1.05)]
    df = df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(-30) * 0.95)]
    df = df.loc[np.abs(df['avgcurr']) < np.abs(df['avgcurr'].shift(30) * 1.05)]
    df = df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(30) * 0.95)]
    '''
    df = df.loc[np.abs(df['avgcurr']) < np.abs(df['avgcurr'].shift(1) * 1.05)]
    df = df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(1) * 0.95)]
    df = df.loc[np.abs(df['avgcurr']) < np.abs(df['avgcurr'].shift(-1) * 1.05)]
    df = df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(-1) * 0.95)]
    df = df.loc[np.abs(df['avgcurr']) < np.abs(df['avgcurr'].shift(120) * 1.05)]
    df = df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(120) * 0.95)]
    df = df.loc[np.abs(df['avgcurr']) < np.abs(df['avgcurr'].shift(-120) * 1.05)]
    df = df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(-120) * 0.95)]
    new_df = df.groupby(['num']).mean()
    new_df = new_df.join(datelist)

    new_df['checker_left'] = np.abs((new_df['avgcurr'].shift(-1) - new_df['avgcurr']) / 60)
    new_df['checker_right'] = np.abs((new_df['avgcurr'].shift(1) - new_df['avgcurr']) / 60)
    new_df['checker_sides'] = np.abs((new_df['avgcurr'].shift(-1) - new_df['avgcurr'].shift(1)) / 120)
    new_df['checker'] = \
        (np.abs(new_df['checker_left']) + np.abs(new_df['checker_right']))/2
    new_df = new_df.set_index('datetime')
    df = df_res
    df = df.join(new_df[['checker']])
    new_df = new_df.rename(columns={"avgcurr": "meancurr"})
    df = df.join(new_df[['meancurr']])
    df = df.ffill(axis=0)
    df = df.bfill(axis=0)
    print(df)
    df.loc[np.abs(df['checker']) < 0.01, 'result_curr'] = 0
    df.loc[df['result_curr'] != 0, 'result_curr'] = 1
    df.loc[np.abs(df['avgcurr']) > np.abs(df['meancurr'] * 1.025), 'result_curr'] = 1
    df.loc[np.abs(df['avgcurr']) < np.abs(df['meancurr'] * 0.975), 'result_curr'] = 1
    '''
    df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(-1) * 1.05), 'result_curr'] = 1
    df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(1) * 1.05), 'result_curr'] = 1
    df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(-10) * 1.05), 'result_curr'] = 1
    df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(10) * 1.05), 'result_curr'] = 1
    df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(-20) * 1.05), 'result_curr'] = 1
    df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(20) * 1.05), 'result_curr'] = 1
    df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(-30) * 1.05), 'result_curr'] = 1
    df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(30) * 1.05), 'result_curr'] = 1
    '''

    # df['result'] = df['result_volt']
    df.loc[df['result_curr'] == 1, 'result'] = 1
    df.loc[df['result'] != 1, 'result'] = 0
    df['datetime'] = df.index
    length = int(len(df))
    unstable = int(df['result_curr'].sum())
    perc = np.round(unstable / length, 2)
    print(str(perc) + "%\n" + str(100 - perc) + "%")

    df['datetime'] = df.index
    sns.scatterplot(x='datetime', y='avgcurr', data=df, alpha=1, s=5, hue='result')
    plt.show()


def third(df):
    df_res = df.copy()
    new_df = df.copy()
    new_df['datetime'] = new_df.index
    new_df = new_df.reset_index()
    new_df['num'] = new_df.index

    new_df = new_df.loc[new_df['num'] % 600 == 0]
    new_df = new_df.drop([0])
    datelist = new_df['datetime']

    new_df = new_df.set_index('datetime')
    df = df.join(new_df[['num']])
    df = df.ffill(axis=0)
    df = df.bfill(axis=0)

    df['datetime'] = df.index

    df = df.loc[np.abs(df['avgcurr']) < np.abs(df['avgcurr'].shift(1) * 1.2)]
    df = df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(1) * 0.8)]
    df = df.loc[np.abs(df['avgcurr']) < np.abs(df['avgcurr'].shift(-1) * 1.2)]
    df = df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(-1) * 0.8)]
    df = df.loc[np.abs(df['avgcurr']) < np.abs(df['avgcurr'].shift(60) * 1.2)]
    df = df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(60) * 0.8)]
    df = df.loc[np.abs(df['avgcurr']) < np.abs(df['avgcurr'].shift(-60) * 1.2)]
    df = df.loc[np.abs(df['avgcurr']) > np.abs(df['avgcurr'].shift(-60) * 0.8)]
    new_df = df.groupby(['num']).mean()
    new_df = new_df.join(datelist)

    new_df['checker'] = np.abs((new_df['avgcurr'].shift(-1) - new_df['avgcurr'].shift(1)) / 1200)
    new_df = new_df.set_index('datetime')
    df = df_res
    df = df.join(new_df[['checker']])
    new_df = new_df.rename(columns={"avgcurr": "meancurr"})
    df = df.join(new_df[['meancurr']])
    df = df.ffill(axis=0)
    df = df.bfill(axis=0)
    print(df)
    df.loc[np.abs(df['checker']) < 0.01, 'result_curr'] = 0
    df.loc[df['result_curr'] != 0, 'result_curr'] = 1
    df.loc[np.abs(df['avgcurr']) > np.abs(df['meancurr'] * 1.025), 'result_curr'] = 1
    df.loc[np.abs(df['avgcurr']) < np.abs(df['meancurr'] * 0.975), 'result_curr'] = 1

    df.loc[df['result_curr'] == 1, 'result'] = 1
    df.loc[df['result'] != 1, 'result'] = 0
    df['datetime'] = df.index
    length = int(len(df))
    unstable = int(df['result_curr'].sum())
    perc = np.round(unstable / length, 2)
    print(str(perc) + "%\n" + str(100 - perc) + "%")

    df['datetime'] = df.index
    sns.scatterplot(x='datetime', y='avgcurr', data=df, alpha=1, s=5, hue='result')
    plt.show()


def main(args):
    conf.configure_from_args(args)

    curr_wrapper = HeinzWrapper(conf.curr_file_names, 'curr')
    volt_wrapper = HeinzWrapper(conf.volt_file_names, 'volt')
    comb_wrapper = ResistanceWrapper(volt_wrapper, curr_wrapper)

    mldf = MLDataFrame(comb_wrapper.data_frame)
    mldf.normal_dist_data()
    df = mldf.data_frame
    second(df)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)


