from PyQt5 import uic
from PyQt5.QtWidgets import QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure

import numpy as np


class MainWindow:
    def __init__(self):
        window = uic.loadUi("mainwindow.ui")
        window.setWindowTitle("[ No open file ]")

        # Add the matplotlib canvas to the window
        canvas = FigureCanvas(Figure(figsize=(5, 3)))
        window.horizontalLayout.replaceWidget(window.placeholder, canvas)

        # The matplotlib Axes to draw to i.e. ax.plot()
        self.ax = canvas.figure.subplots(subplot_kw=dict(polar=True))

        self.plot_settings = {}
        self.data_frames = {}  # Will store the dfs for each frequency
        self.filename = None

        # Register the actions for the gui events
        window.choose_file_btn.clicked.connect(self.set_file)
        # window.file_input.returnPressed.connect(partial(self.set_file, line_input=True))
        window.plot_btn.clicked.connect(self.plot)
        window.plot_theta_btn.toggled.connect(
                lambda selected: self.update_plot_settings({"var": "theta" if selected else "phi"})
            )
        window.lock_input.returnPressed.connect(
                lambda: self.update_plot_settings({"locked_degree": window.lock_input.text()})
            )

        window.freq_selector.addItems([str(x) + " MHz" for x in [100, 1000, 10000]])

        window.freq_selector.currentTextChanged.connect(
            lambda freq: self.update_plot_settings({"freq": freq})
        )

        window.lock_input.setText("49")
        self.plot_settings["locked_degree"] = 49
        self.window = window

    def show(self):
        self.window.show()

    def plot(self):
        r = np.arange(0, -2, -0.01)
        theta = 2 * np.pi * r

        phi = -2 * np.pi * r

        self.ax.clear()
        self.ax.plot(theta, r, label="Theta")
        self.ax.plot(phi, r, label="Phi")
        self.ax.set_rmin(-2)
        self.ax.set_rticks([-0.5, -1, -1.5, -2])  # less radial ticks
        self.ax.set_rlabel_position(22.5)  # get radial labels away from plotted line
        self.ax.grid(True)
        self.ax.set_title("A line plot on a polar axis", va='bottom')
        self.ax.legend(loc='lower left', bbox_to_anchor=(-0.2, -0.15, 1, 1), ncol=2)

        self.ax.figure.canvas.draw_idle()

    def set_file(self):
        filename = QFileDialog.getOpenFileName(self.window)[0]

        if filename:
            self.filename = filename
            self.window.setWindowTitle(self.filename)

    def load(self, freq=None):
        pass

    def update_plot_settings(self, settings):
        for key, val in settings.items():

            if key == "locked_degree":

                # The input value is parsed to int if parsing fails
                # the last value is kept and the input field is reset

                deg = None

                try:
                    deg = int(float(val))
                except ValueError:
                    pass

                if deg:
                    self.plot_settings[key] = deg
                self.window.lock_input.setText(str(self.plot_settings[key]))
                continue

            # for all other keys
            if key == "var":
                other = "theta" if val == "phi" else "phi"
                puffer = " " * (5 - len(val))
                self.window.lock_label.setText(f"Lock {other} at:{puffer}")

            self.plot_settings[key] = val
