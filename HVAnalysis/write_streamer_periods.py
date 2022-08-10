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
    print(f'linos_periods = {linos_periods}')
    linos_writer.write_unstable_periods(linos_periods)

    ernests_writer = ErnestsWriter(comb_wrapper, f'{args.outputfolder}/ernests_unstable_periods.csv')
    ernests_periods = ernests_writer.get_unstable_periods()
    print(f'ernests_periods = {linos_periods}')
    ernests_writer.write_unstable_periods(ernests_periods)

    print(f'linos_periods == ernests_periods = {linos_periods==ernests_periods}')
    print(f'len(linos_periods) = {len(linos_periods)}')
    print(f'len(ernests_periods) = {len(ernests_periods)}')
    for i in range(len(linos_periods)):
        p1 = linos_periods[i]
        p2 = ernests_periods[i]
        print(f'i={i}, p1={p1}, p2={p2}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None,
                        help="dates to consider. Default considers all dates in folder.")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)