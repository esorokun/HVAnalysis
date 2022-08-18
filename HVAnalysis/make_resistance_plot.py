import argparse
import conf
import pandas as pd
from dfwrapper import HeinzWrapper, ResistanceWrapper
from plotting import Plotter
from writing import LinosWriter, ErnestsWriter
from color_plot import ColorDF, BuildColorPlots


def main(args):
    conf.configure_from_args(args)
    curr_f_wrapper = HeinzWrapper(conf.Heinz_I_Filtered_curr_file_names, 'curr')
    curr_wrapper = HeinzWrapper(conf.Heinz_I_curr_file_names, 'curr')
    volt_r_wrapper = HeinzWrapper(conf.Heinz_V_Raw_volt_file_names, 'volt')
    volt_wrapper = HeinzWrapper(conf.Heinz_V_volt_file_names, 'volt')
    volt_c_wrapper = HeinzWrapper(conf.Heinz_V_Cathode_volt_file_names, 'volt')
    curr_f_wrapper.add_marker_column('I_Filtered')
    curr_wrapper.add_marker_column('I')
    volt_r_wrapper.add_marker_column('V_Raw')
    volt_wrapper.add_marker_column('V')
    volt_c_wrapper.add_marker_column('V_Cathode')

    new_df_V = pd.concat([volt_c_wrapper.data_frame, volt_wrapper.data_frame, volt_r_wrapper.data_frame])
    new_df_I = pd.concat([curr_wrapper.data_frame, curr_f_wrapper.data_frame])
    plotter_V = Plotter(new_df_V)
    plotter_I = Plotter(new_df_I)
    plotter_V.plot_scatter('timestamp', 'volt')

    #writer = ErnestsWriter(comb_wrapper, f'{args.outputfolder}/ernests_unstable_periods_remove.csv')
    #writer.write_unstable_not_overlapping_periods(writer.get_unstable_periods(), 2)
    #writer = LinosWriter(comb_wrapper, f'{args.outputfolder}/linos_unstable_periods_2.csv')
    #writer.write_unstable_periods(writer.get_unstable_periods(), 2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)