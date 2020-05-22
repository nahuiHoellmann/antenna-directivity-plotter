from PyQt5 import uic
from PyQt5.QtWidgets import QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure

from antools import Plotter
import pandas as pd
from functools import wraps


def updates_setting(f):
    """
    Make sure that after the user changes the plot settings the gui is updated accordingly
    """
    @wraps(f)
    def wrapper(self, *args):
        f(self, *args)
        self.update_gui()
    return wrapper


class MainWindow:
    def __init__(self):
        import os
        print(os.getcwd())
        window = uic.loadUi("mainwindow.ui")
        self.window = window
        self.setup_gui()

        self.init_settings()

    def setup_gui(self):
        """
        Initializes the gui
        -Add the plotting canvas to the gui
        -Delegate registering signals
        """
        self.window.setWindowTitle("[ No open file ]")

        # Add the matplotlib canvas to the window
        canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.window.horizontalLayout.replaceWidget(self.window.placeholder, canvas)

        # The matplotlib Axes to draw to i.e. ax.plot()
        self.ax = canvas.figure.subplots(subplot_kw=dict(polar=True))

        # This widgets will be deactivated if no file is specified
        self.requires_file = [
            self.window.plot_phi_btn,
            self.window.plot_theta_btn,
            self.window.set_e_phi,
            self.window.set_e_theta,
            self.window.plot_btn,
            self.window.lock_input,
            self.window.freq_selector
        ]

        self.register_signals()

    def register_signals(self):

        self.window.choose_file_btn.clicked.connect(
            # Don't change!
            # self.set_file
            lambda _: self.set_file()
        )

        self.window.plot_btn.clicked.connect(
            self.plot
        )

        self.window.lock_input.returnPressed.connect(
            self.parse_degree_input
        )

        self.window.freq_selector.currentTextChanged.connect(
            self.set_freq
        )

        self.window.plot_theta_btn.toggled.connect(
            lambda selected: self.set_lock_var("Phi" if selected else "Theta")
        )

        self.window.set_e_phi.stateChanged.connect(
            lambda state: self.update_polarization('E-Phi', state)
        )

        self.window.set_e_theta.stateChanged.connect(
            lambda state: self.update_polarization('E-Theta', state)
        )

    def init_settings(self):
        """
        Set the default settings and update gui accordingly
        """

        self.lock_var = "Theta"
        self.lock_deg = None
        self.polarization = set()
        self.freq = None
        self.filename = None

        self.update_gui()

    def update_gui(self):
        """
        Activate and deactivate gui elements depending on wether the current plot setting are valid
        This function is mainly called by the updates_setting wraper to update the gui each time the user interacts
        with it
        if no file is chosen only the open file button is active
        the plot button is active as long as all plot setting have a valid value
        """
        if not self.filename:
            for widget in self.requires_file:
                widget.setEnabled(False)
            return
        else:
            for widget in self.requires_file:
                widget.setEnabled(True)

        plot_prequesites = all([
            self.lock_var,
            self.lock_deg is not None,
            self.polarization,
            self.freq,
            len(self.polarization) > 0
        ])

        self.window.plot_btn.setEnabled(plot_prequesites)

    def show(self):
        self.window.show()

    def plot(self):
        """
        Call the antools api to plot the user specified graph into the canvas
        """
        df = self.xl.parse(self.freq)
        Plotter.io_plot(df, lock=(self.lock_var, self.lock_deg), polarization=list(self.polarization), freq=self.freq, ax=self.ax)
        self.ax.figure.canvas.draw_idle()

    @updates_setting
    def parse_degree_input(self):
        try:
            self.lock_deg = int(self.window.lock_input.text())
        except ValueError:
            pass

        if self.lock_deg is not None:
            new_text = str(self.lock_deg)
        else:
            new_text = ""

        self.window.lock_input.setText(new_text)

    @updates_setting
    def update_polarization(self, pol_name, state):
        if state == 0:
            self.polarization.remove(pol_name)
        elif state == 2:
            self.polarization.add(pol_name)

    @updates_setting
    def set_freq(self, freq):
        self.freq = freq

    @updates_setting
    def set_lock_var(self, var):
        self.lock_var = var

    @updates_setting
    def set_file(self):
        filename = QFileDialog.getOpenFileName(self.window)[0]

        if not filename:
            return

        self.xl = pd.ExcelFile(filename)
        self.filename = filename

        self.window.setWindowTitle(self.filename)
        self.window.freq_selector.clear()
        self.window.freq_selector.addItems(self.xl.sheet_names)
