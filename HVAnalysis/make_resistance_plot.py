import argparse
import conf
from dfwrapper import HeinzWrapper, ResistanceWrapper
from plotting import Plotter
from writing import Writer


def main(args):
    conf.configure_from_args(args)
    curr_wrapper = HeinzWrapper(conf.curr_file_names, 'curr')
    volt_wrapper = HeinzWrapper(conf.volt_file_names, 'volt')
    comb_wrapper = ResistanceWrapper(curr_wrapper, volt_wrapper)
    my_plotter = Plotter(comb_wrapper)
    #my_plotter.histogram('avgvolt')
    #my_writer = Writer(comb_wrapper)
    #my_writer.write_streamer_periods('data/output/unstable_periods.csv')
    my_plotter.plot_scatter()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)