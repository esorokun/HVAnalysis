import matplotlib.pyplot as plt
import conf


class Plotter:
    def __init__(self, df_wrapper):
        self.df_wrapper = df_wrapper

    def plot(self):
        self.df_wrapper.data_frame.plot(y=['resistance', 'avgcurr', 'avgvolt'])
        plt.show()
        plt.savefig(f'{conf.output_folder}/plot.png')

    def plotcurr(self):
        self.df_wrapper.data_frame.plot(y=['curr'])
        plt.show()
        plt.savefig(f'{conf.output_folder}/plotcurr.png')