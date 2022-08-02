import matplotlib.pyplot as plt
import conf
import seaborn as sb
import numpy as np
import pandas as pd


class Plotter:
    def __init__(self, df_wrapper_1, df_wrapper_2=None):
        #if df_wrapper_2 is not None:self.df_wrapper = pd.merge(df_wrapper_1, df_wrapper_2, on='timestamp')
        #else: self.df_wrapper = df_wrapper_1
        self.df_wrapper = df_wrapper_1

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
        _ = plt.scatter(y=self.df_wrapper([name_y]), x=self.df_wrapper([name_x]), alpha=0.05, s=0.1)
        plt.xlabel(name_x)
        plt.ylabel(name_y)
        plt.show()
        if savename is not None: plt.savefig(f'{conf.output_folder}/{savename}.png')
