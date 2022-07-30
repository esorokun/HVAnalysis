import matplotlib.pyplot as plt


class Plotter:
    def __init__(self, df_wrapper, output_folder='data/output/plots'):
        self.df_wrapper = df_wrapper
        self.output_folder = output_folder

    def plot(self):
        self.df_wrapper.data_frame.plot()
        plt.show()