import argparse
import conf
from dfwrapper import HeinzWrapper, ResistanceWrapper
from plotting import Plotter


def main(args):
    conf.configure_from_args(args)
    curr_wrapper = HeinzWrapper(conf.curr_file_names, 'curr')
    volt_wrapper = HeinzWrapper(conf.volt_file_names, 'volt')
    comb_wrapper = ResistanceWrapper(curr_wrapper, volt_wrapper)
    my_plotter = Plotter(comb_wrapper)
    '''
    my_plotter.plotseparate('resistance')
    my_plotter.plotseparate('avgvolt')
    my_plotter.plotseparate('avgcurr')
    my_plotter.histogram('resistance')
    my_plotter.histogram('avgvolt')
    my_plotter.histogram('avgcurr')
    '''
    my_plotter.plotscatter()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datelist", nargs="+", default=None, help="dates to consider")
    parser.add_argument("--loglvl", type=int, default=0, help="0: warning, 1: info, 2: debug")
    parser.add_argument("--outputfolder", type=str, default="data/output/",
                        help="name of output file")
    args = parser.parse_args()
    main(args)