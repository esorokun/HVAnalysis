import argparse
import logging
import conf
from dfwrapper import HeinzWrapper, ResistanceWrapper
from plotting import Plotter


def main(args):
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.WARNING)
    curr_file_names = conf.FileNames.curr(args.datelist)
    volt_file_names = conf.FileNames.volt(args.datelist)
    curr_wrapper = HeinzWrapper(curr_file_names, 'curr')
    volt_wrapper = HeinzWrapper(volt_file_names, 'volt')
    comb_wrapper = ResistanceWrapper(curr_wrapper, volt_wrapper)
    print(f'curr_wrapper.data_frame =\n{curr_wrapper.data_frame}')
    print(f'volt_wrapper.data_frame =\n{volt_wrapper.data_frame}')
    print(f'comb_wrapper.data_frame =\n{comb_wrapper.data_frame}')
    curr_plotter = Plotter(curr_wrapper)
    my_plotter.plot()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--debug", default=False, action="store_true", help="activate debug level logging")
    parser.add_argument("--output", type=str, default="data/output/resistance_plot.png",
                        help="name of output file")
    args = parser.parse_args()
    main(args)