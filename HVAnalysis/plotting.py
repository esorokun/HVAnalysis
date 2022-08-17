import matplotlib.pyplot as plt
import conf
import pandas as pd
import logging
import seaborn as sns


class Plotter:
    def __init__(self, df_wrapper_1):
        self.df_wrapper = df_wrapper_1

    def plot(self, saver):
        self.df_wrapper.plot(y=['resistance', 'avgcurr', 'avgvolt'])
        plt.show()
        if saver == 1: plt.savefig(f'{conf.output_folder}/plot.png')

    def plot_separate(self, name):
        self.df_wrapper.plot(y=[name])
        plt.xlabel("timeset")
        plt.ylabel("Value of " + name)
        plt.show()

    def histogram(self, name):
        range = None
        if name == 'resistance': range = [-2000, 3000]
        _ = plt.hist(self.df_wrapper[name], bins=60, range=range)
        plt.xlabel(name)
        plt.ylabel("Num")
        plt.show()

    def plot_scatter(self, name_x, name_y, colourmap='blue'):
        sns.scatterplot(x=name_x, y=name_y, data=self.df_wrapper, alpha=1, s=12, hue='marker')
        #self.df_wrapper.plot.scatter(y=[name_y], x=[name_x], alpha=0.05, s=0.1, c=[colourmap])
        plt.show()
