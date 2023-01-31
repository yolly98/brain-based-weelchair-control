import os
from matplotlib import pyplot as plt

from utility.logging import trace


class GradientDescentPlotGenerator:

    def __init__(self) -> None:
        self._image_path = os.path.join(os.path.abspath('..'), 'data', 'gradient_descent_plot.png')

    def generate_plot(self, losses: list) -> None:
        # plot
        plt.plot(range(1, len(losses) + 1), losses)
        plt.xlabel('Iterations')
        plt.ylabel('Loss Function')

        # save plot as PNG
        plt.savefig(self._image_path, dpi=300)
        trace('Gradient Descent Plot exported')

        # show the plot
        # plt.show()
