import argparse
import conf
from dfwrapper import HeinzWrapper, ResistanceWrapper
from writing import LinosWriter, ErnestsWriter


def main(args):
    conf.configure_from_args(args)

    curr_wrapper = HeinzWrapper(conf.curr_file_names, 'curr')
    volt_wrapper = HeinzWrapper(conf.volt_file_names, 'volt')
    comb_wrapper = ResistanceWrapper(curr_wrapper, volt_wrapper)

    linos_writer = LinosWriter(comb_wrapper, f'{args.outputfolder}/linos_unstable_periods.csv')
    linos_periods = linos_writer.get_unstable_periods()
    linos_writer.write_unstable_periods(linos_periods)

    ernests_writer = ErnestsWriter(comb_wrapper, f'{args.outputfolder}/ernests_unstable_periods.csv')
    ernests_periods = ernests_writer.get_unstable_periods()
    ernests_writer.write_unstable_periods(ernests_periods)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None,
                        help="dates to consider. Default considers all dates in folder.")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)