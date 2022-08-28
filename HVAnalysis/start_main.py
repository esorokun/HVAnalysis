import numpy as np
from ML import MLDataFrame, PlotBuilder
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
    df = mldf.data_frame

    resdf = mldf.curr_for_ml()
    pyod_model = CBLOF(contamination=0.2)
    pyod_sktime_annotator_curr = PyODAnnotator(pyod_model)
    pyod_sktime_annotator_curr.fit(resdf)
    list_result = pyod_sktime_annotator_curr.predict(resdf)

    ml_plot = PlotBuilder(df, list_result)
    ml_plot.build_datetime_plot_ml('avgcurr')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)