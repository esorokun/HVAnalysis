import numpy as np
from ML import MLDataFrame
from dfwrapper import HeinzWrapper, ResistanceWrapper
import argparse
import conf
from plotting import Plotter
import datetime
#from pycaret.anomaly

def main(args):
    conf.configure_from_args(args)

    curr_wrapper = HeinzWrapper(conf.curr_file_names, 'curr')
    volt_wrapper = HeinzWrapper(conf.volt_file_names, 'volt')
    comb_wrapper = ResistanceWrapper(volt_wrapper, curr_wrapper)
    mldf = MLDataFrame(comb_wrapper.data_frame)
    mldf.transform_data()
    mldf.add_log10_params()
    mldf.add_unix_time_from_index(mldf.log10_df)
    print(mldf.log10_df)

    '''test_df = df.reset_index()[['timestamp', 'resistance']].\
                        rename({'timestamp': 'ds', 'resistance': 'y'}, axis='columns')
    m = Prophet(changepoint_range=0.8)
    m.fit(df)'''
    #plotting = Plotter(comb_wrapper.data_frame)
    #plotting.plot_separate('avgcurr')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)