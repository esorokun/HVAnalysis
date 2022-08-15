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

    writer = ErnestsWriter(comb_wrapper, f'{args.outputfolder}/ernests_unstable_periods_remove.csv')
    writer.write_unstable_periods(writer.get_unstable_periods(), 2)
    '''writer = LinosWriter(comb_wrapper, f'{args.outputfolder}/linos_unstable_periods_2.csv')
    writer.write_unstable_periods(writer.get_unstable_periods(), 2)'''


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)