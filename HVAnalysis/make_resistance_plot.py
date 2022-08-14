import argparse
import conf
from dfwrapper import HeinzWrapper, ResistanceWrapper
from writing import LinosWriter, ErnestsWriter
from color_plot import ColorDF, BuildColorPlots


def main(args):
    conf.configure_from_args(args)
    curr_wrapper = HeinzWrapper(conf.curr_file_names, 'curr')
    volt_wrapper = HeinzWrapper(conf.volt_file_names, 'volt')
    comb_wrapper = ResistanceWrapper(curr_wrapper, volt_wrapper)

    writer = ErnestsWriter(comb_wrapper, f'{args.outputfolder}/ernests_unstable_periods.csv')
    writer.fill_nan()
    periods_df = writer.df_avgvolt_cut_unstable_periods()
    plot_data = BuildColorPlots(periods_df)
    #plot_data.filter_df_by_beam_mom()
    plot_data.build_color_histogram_plot()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)