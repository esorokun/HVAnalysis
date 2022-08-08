import argparse
import conf
from dfwrapper import HeinzWrapper, ResistanceWrapper
from plotting import Plotter
from original_writing import Writer
from new_writing import NewWriter , hv_filter_data_in_csv
from filtering import Filter
import pandas as pd
from datetime import datetime

def main(args):
    conf.configure_from_args(args)
    curr_wrapper = HeinzWrapper(conf.curr_file_names, 'curr')
    volt_wrapper = HeinzWrapper(conf.volt_file_names, 'volt')
    comb_wrapper = ResistanceWrapper(curr_wrapper, volt_wrapper)

    my_new_writer = NewWriter(comb_wrapper, 'data/output/new_unstable_periods.csv')
    filtered_data = Filter(my_new_writer)
    df_bool = my_new_writer.new_df_unstable_periods()
    df_color = filtered_data.bool_in_color_df(df_bool)
    filtered_data.build_color_data_plot(df_color)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)