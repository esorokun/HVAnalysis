import matplotlib.pyplot as plt
import conf

class Plotter:
    def __init__(self, df_wrapper):
        self.df_wrapper = df_wrapper

    def plot(self, saver):
        self.df_wrapper.data_frame.plot(y=['resistance', 'avgcurr', 'avgvolt'])
        plt.show()
        if saver == 1: plt.savefig(f'{conf.output_folder}/plot.png')

    def plotseparate(self, name, saver):
        self.df_wrapper.data_frame.plot(y=[name])
        plt.show()
        if saver == 1: plt.savefig(f'{conf.output_folder}/plot.png')

    def gistogram(self, name, saver):
        _ = plt.hist(self.df_wrapper.data_frame[name], bins=40, range=[-50000000, 50000000])
        plt.xlabel(name)
        plt.ylabel("Num")
        plt.show()
        if saver == 1: plt.savefig(f'{conf.output_folder}/plot.png')