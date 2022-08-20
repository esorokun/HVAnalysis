import argparse

from matplotlib import pyplot as plt

import conf
import pandas as pd
from dfwrapper import HeinzWrapper, ResistanceWrapper
from plotting import Plotter
from writing import LinosWriter, ErnestsWriter
from color_plot import ColorDF, BuildColorPlots
import seaborn as sns


def main(args):
    conf.configure_from_args(args)

    curr_wrapper = HeinzWrapper(conf.curr_file_names, 'curr')
    volt_wrapper = HeinzWrapper(conf.volt_file_names, 'volt')
    comb_wrapper = ResistanceWrapper(volt_wrapper, curr_wrapper)
    ernest_writer = ErnestsWriter(comb_wrapper, f'{args.outputfolder}/ernests_unstable_periods_remove.csv')
    ernest_writer.fill_nan()
    df = ernest_writer.df_wrapper.data_frame
    sns.jointplot(x='avgcurr', y='avgvolt', data=df, alpha=1, s=5)
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)