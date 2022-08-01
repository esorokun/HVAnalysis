import matplotlib.pyplot as plt
import conf
import numpy as np

class Plotter:
    def __init__(self, df_wrapper):
        self.df_wrapper = df_wrapper

    def plot(self, saver):
        self.df_wrapper.data_frame.plot(y=['resistance', 'avgcurr', 'avgvolt'])
        plt.show()
        if saver == 1: plt.savefig(f'{conf.output_folder}/plot.png')

    def plotcurr(self, saver):
        self.df_wrapper.data_frame.plot(y=['avgcurr'])
        plt.show()
        if saver == 1: plt.savefig(f'{conf.output_folder}/plot.png')

    def plotvolt(self, saver):
        self.df_wrapper.data_frame.plot(y=['avgvolt'])
        plt.show()
        if saver == 1: plt.savefig(f'{conf.output_folder}/plot.png')

    def plotresist(self, saver):
        self.df_wrapper.data_frame.plot(y=['resistance'])
        plt.show()
        if saver == 1: plt.savefig(f'{conf.output_folder}/plot.png')

    def plotall(self, saver):
        self.df_wrapper.data_frame.plot(y=['avgcurr'])
        self.df_wrapper.data_frame.plot(y=['resistance'])
        self.df_wrapper.data_frame.plot(y=['avgvolt'])
        plt.show()
        if saver == 1:
            plt.savefig(f'{conf.output_folder}/plot.png')

    def gistogram(self, name, saver):
        _ = plt.hist(self.df_wrapper.data_frame[name], bins=40)
        plt.show()
        if saver == 1: plt.savefig(f'{conf.output_folder}/plot.png')