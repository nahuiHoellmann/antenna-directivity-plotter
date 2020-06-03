from PyQt5 import uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QTimer
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

        self.register_signals()

    def register_signals(self):

        self.window.choose_file_btn.clicked.connect(
            # Don't change to self.set_file!
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
        self.file_did_finish_loading = False
        self.lock_deg = None
        self.polarization = set()
        self.freq = None
        self.filename = None

        # The user needs to specify a file first
        self.window.plot_controls.setEnabled(False)

    def update_gui(self):
        """
        Activate and deactivate gui elements depending on wether the current plot setting are valid
        This function is mainly called by the updates_setting wraper to update the gui each time the user interacts
        with it
        if no file is chosen only the open file button is active
        the plot button is active as long as all plot setting have a valid value
        """
        if self.file_did_finish_loading:
            self.window.plot_controls.setEnabled(True)

            plot_prequesites = all([
                self.lock_var,
                self.lock_deg is not None,  # 0 is falsy value but a valid degree
                self.polarization,
                self.freq,
                len(self.polarization) > 0
            ])

            self.window.plot_btn.setEnabled(plot_prequesites)

        else:
            self.window.plot_controls.setEnabled(False)

    def show(self):
        self.window.show()

    def plot(self):
        """
        Call the antools api to plot the user specified graph into the canvas
        """
        df = self.xl.parse(self.freq)

        try:
            Plotter.io_plot(
                df,
                lock=(self.lock_var, self.lock_deg),
                polarization=list(self.polarization),
                freq=self.freq,
                ax=self.ax
            )
        except TypeError or IndexError:
            mb = QMessageBox(
                text="The file you specified seems to be in the wrong format"
            )
            mb.exec()
        else:
            self.ax.figure.canvas.draw_idle()

    @updates_setting
    def parse_degree_input(self):

        try:
            deg = int(self.window.lock_input.text())
        except ValueError:
            pass
        else:
            if self.lock_var == "Theta":
                deg_max = 180
            else:
                deg_max = 360

            if 0 > deg:
                self.lock_deg = 0
            elif deg > deg_max:
                self.lock_deg = deg_max
            else:
                self.lock_deg = deg

        new_text = str(self.lock_deg) if self.lock_deg is not None else ""
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
        self.window.label_lock.setText(f'Lock {var} at:')

    @updates_setting
    def set_file(self):
        filename = QFileDialog.getOpenFileName(self.window, filter="*.xlsx")[0]

        if filename:

            self.filename = filename
            self.window.setWindowTitle("Loading file...")
            self.file_did_finish_loading = False
            QTimer.singleShot(20, self.load_file)

    @updates_setting
    def load_file(self):

        self.xl = pd.ExcelFile(self.filename)
        self.window.freq_selector.clear()
        self.window.freq_selector.addItems(self.xl.sheet_names)
        self.window.setWindowTitle(self.filename)
        self.file_did_finish_loading = True
