import matplotlib.pyplot as plt
import conf
import seaborn as sns

class Plotter:
    def __init__(self, df_wrapper):
        self.df_wrapper = df_wrapper

    def plot(self, saver):
        self.df_wrapper.data_frame.plot(y=['resistance', 'avgcurr', 'avgvolt'])
        plt.show()
        if saver == 1: plt.savefig(f'{conf.output_folder}/plot.png')

    def plotseparate(self, name, savename=None):
        self.df_wrapper.data_frame.plot(y=[name])
        plt.xlabel("timeset")
        plt.ylabel("Value of " + name)
        plt.show()
        if savename is not None: plt.savefig(f'{conf.output_folder}/{savename}.png')

    def histogram(self, name, savename=None):
        range = None
        if name == 'resistance': range = [-2000, 3000]
        _ = plt.hist(self.df_wrapper.data_frame[name], bins=60, range = range)
        plt.xlabel(name)
        plt.ylabel("Num")
        plt.show()
        if savename is not None: plt.savefig(f'{conf.output_folder}/{savename}.png')

    def plotscatter(self, name_x='avgcurr', name_y='avgvolt', savename=None):
        self.df_wrapper.data_frame.plot.scatter(y=[name_y], x=[name_x])
        plt.xlabel(name_x)
        plt.ylabel(name_y)
        plt.show()
        if savename is not None: plt.savefig(f'{conf.output_folder}/{savename}.png')