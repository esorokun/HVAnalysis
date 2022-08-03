import matplotlib.pyplot as plt
import conf
import pandas as pd
import logging


class Plotter:
    def __init__(self, df_wrapper_1, df_wrapper_2=None):
        if df_wrapper_2 is not None:
            self.df_wrapper = pd.merge(df_wrapper_1.data_frame, df_wrapper_2.data_frame, on='timestamp')
            logging.info(f'HeinzWrapper.data_frame =\n{self.df_wrapper}')
        else:
            self.df_wrapper = df_wrapper_1.data_frame

    def plot(self, saver):
        self.df_wrapper.plot(y=['resistance', 'avgcurr', 'avgvolt'])
        plt.show()
        if saver == 1: plt.savefig(f'{conf.output_folder}/plot.png')

    def plot_separate(self, name, savename=None):
        self.df_wrapper.plot(y=[name])
        plt.xlabel("timeset")
        plt.ylabel("Value of " + name)
        plt.show()
        if savename is not None: plt.savefig(f'{conf.output_folder}/{savename}.png')

    def histogram(self, name, savename=None):
        range = None
        if name == 'resistance': range = [-2000, 3000]
        _ = plt.hist(self.df_wrapper[name], bins=60, range=range)
        plt.xlabel(name)
        plt.ylabel("Num")
        plt.show()
        if savename is not None: plt.savefig(f'{conf.output_folder}/{savename}.png')

    def plot_scatter(self, name_x='avgcurr', name_y='avgvolt', savename=None):
        self.df_wrapper.plot.scatter(y=[name_y], x=[name_x], alpha=0.05, s=0.1)
        plt.xlabel(name_x)
        plt.ylabel(name_y)
        plt.show()
        if savename is not None: plt.savefig(f'{conf.output_folder}/{savename}.png')
