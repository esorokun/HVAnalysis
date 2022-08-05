import argparse
import conf
from dfwrapper import HeinzWrapper, ResistanceWrapper
from original_writing import LinosWriter


def main(args):
    conf.configure_from_args(args)

    curr_wrapper = HeinzWrapper(conf.curr_file_names, 'curr')
    volt_wrapper = HeinzWrapper(conf.volt_file_names, 'volt')
    comb_wrapper = ResistanceWrapper(curr_wrapper, volt_wrapper)

    my_writer = LinosWriter(comb_wrapper, f'{args.outputfolder}/linos_unstable_periods.csv')
    my_writer.write_streamer_periods()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None,
                        help="dates to consider. Default considers all dates in folder.")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)