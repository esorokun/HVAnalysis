import argparse
import conf
from dfwrapper import HeinzWrapper, ResistanceWrapper
from writing import LinosWriter, ErnestsWriter
from color_plot import ColorPlots, beam_on_df

def main(args):
    conf.configure_from_args(args)
    curr_wrapper = HeinzWrapper(conf.curr_file_names, 'curr')
    volt_wrapper = HeinzWrapper(conf.volt_file_names, 'volt')
    comb_wrapper = ResistanceWrapper(curr_wrapper, volt_wrapper)

    writer = ErnestsWriter(comb_wrapper, f'{args.outputfolder}/ernests_unstable_periods.csv')
    periods_df = writer.new_df_unstable_periods()
    plot_data = ColorPlots(periods_df)
    colored_data = plot_data.bool_in_color_df()
    beam_on_colored_data = plot_data.beam_on_filter(colored_data)
    plot_data.build_color_scatter_plot(beam_on_colored_data)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)