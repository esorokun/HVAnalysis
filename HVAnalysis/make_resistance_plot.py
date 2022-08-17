import argparse
import conf
import pandas as pd
from dfwrapper import HeinzWrapper, ResistanceWrapper
from plotting import Plotter
from writing import LinosWriter, ErnestsWriter
from color_plot import ColorDF, BuildColorPlots


def main(args):
    conf.configure_from_args(args)
    volt_wrapper = HeinzWrapper(conf.Heinz_V_volt_file_names, 'volt')
    curr_wrapper = HeinzWrapper(conf.Heinz_I_curr_file_names, 'curr')
    volt_r_wrapper = HeinzWrapper(conf.Heinz_V_Raw_volt_file_names, 'volt')
    curr_f_wrapper = HeinzWrapper(conf.Heinz_I_Filtered_curr_file_names, 'curr')
    volt_c_wrapper = HeinzWrapper(conf.Heinz_V_Cathode_volt_file_names, 'volt')
    comb_wrapper_1 = ResistanceWrapper(curr_wrapper, volt_wrapper)
    comb_wrapper_2 = ResistanceWrapper(curr_wrapper, volt_r_wrapper)
    comb_wrapper_3 = ResistanceWrapper(curr_f_wrapper, volt_r_wrapper)
    comb_wrapper_4 = ResistanceWrapper(curr_f_wrapper, volt_wrapper)
    comb_wrapper_5 = ResistanceWrapper(curr_wrapper, volt_c_wrapper)
    comb_wrapper_6 = ResistanceWrapper(curr_f_wrapper, volt_c_wrapper)
    comb_wrapper_1.add_marker_column('V(I)')
    comb_wrapper_2.add_marker_column('V_Raw(I)')
    comb_wrapper_3.add_marker_column('V_Raw(I_Filtered)')
    comb_wrapper_4.add_marker_column('V(I_Filtered)')
    comb_wrapper_5.add_marker_column('V_Cathode(I)')
    comb_wrapper_6.add_marker_column('V_Cathode(I_Filtered)')
    new_df = pd.concat([comb_wrapper_1.data_frame,
                        comb_wrapper_2.data_frame,
                        comb_wrapper_3.data_frame,
                        comb_wrapper_4.data_frame,
                        comb_wrapper_5.data_frame,
                        comb_wrapper_6.data_frame
                        ])
    plotter = Plotter(new_df)
    plotter.plot_scatter('avgcurr', 'avgvolt')

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