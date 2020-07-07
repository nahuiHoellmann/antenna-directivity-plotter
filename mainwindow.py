from PyQt5 import uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QMainWindow
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure

import antools
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


class MainWindow(QMainWindow):
    def __init__(self, debug=False):
        QMainWindow.__init__(self)
        uic.loadUi("mainwindow.ui", self)
        self.setup_gui()
        self.init_settings()

        if debug:
            self.fastTestSetUp()

    def setup_gui(self):
        """
        Initializes the gui
        -Add the plotting canvas to the gui
        -Delegate registering signals
        """
        self.setWindowTitle("[ No open file ]")

        # Add the matplotlib canvas to the window
        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.horizontalLayout.replaceWidget(self.placeholder, self.canvas)

        # The matplotlib Axes to draw to i.e. ax.plot()
        self.ax = self.canvas.figure.add_axes([0.05, 0.2, 0.9, 0.7], projection=None, polar=True)
        self.register_signals()

    def register_signals(self):

        self.choose_file_btn.clicked.connect(
            # Don't change to self.set_file!
            lambda _: self.set_file()
        )

        self.plot_btn.clicked.connect(
            lambda _: self.plot()
        )

        self.lock_input.textEdited.connect(
            self.validate_degree_input
        )

        self.freq_selector.currentTextChanged.connect(
            self.set_freq
        )

        self.plot_theta_btn.toggled.connect(
            lambda selected: self.set_lock_var("Phi" if selected else "Theta")
        )

        self.set_e_phi.stateChanged.connect(
            lambda state: self.update_polarization('E-Phi', state)
        )

        self.set_e_theta.stateChanged.connect(
            lambda state: self.update_polarization('E-Theta', state)
        )

        self.save_btn.clicked.connect(
            self.save_plot
        )

        self.min_constraint_input.textEdited.connect(
            lambda text: self.validate_constraint_input(text, constr='min')
        )

        self.max_constraint_input.textEdited.connect(
            lambda text: self.validate_constraint_input(text, constr='max')
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
        self.plot_visible = False
        self.constraint = {
            'min': None,
            'max': None
        }

        self.valid_degree_input = False
        self.valid_constraint_input = {
            'min': False,
            'max': False
        }

        # The user needs to specify a file first
        self.plot_controls.setEnabled(False)
        # The user needs to draw a plot first
        self.save_btn.setEnabled(False)

    def update_gui(self):
        """
        Activate and deactivate gui elements depending on wether the current plot setting are valid
        This function is mainly called by the updates_setting wraper to update the gui each time the user interacts
        with it
        if no file is chosen only the open file button is active
        the plot button is active as long as all plot setting have a valid value
        """
        if self.file_did_finish_loading:
            self.plot_controls.setEnabled(True)

            plot_prequesites = all([
                self.lock_var,
                self.lock_deg is not None,  # 0 is falsy value but a valid degree
                self.polarization,
                self.freq,
                len(self.polarization) > 0
            ])

            self.plot_btn.setEnabled(plot_prequesites)

        else:
            self.plot_controls.setEnabled(False)

    @updates_setting
    def plot(self):
        """
        Call the antools api to plot the user specified graph into the canvas
        """
        df = self.xl[self.freq]

        try:
            antools.Plotter.io_plot(
                df,
                lock=(self.lock_var, self.lock_deg),
                polarization=list(self.polarization),
                freq=self.freq,
                ax=self.ax,
                constr_min=self.constraint['min'],
                constr_max=self.constraint['max']
            )
        except TypeError or IndexError:
            mb = QMessageBox(
                text="The file you specified seems to be in the wrong format"
            )
            mb.exec()
        else:
            self.ax.figure.canvas.draw_idle()

            if not self.plot_visible:
                self.plot_visible = True
                self.save_btn.setEnabled(True)
                self.save_btn.repaint()  # For some reason the button stays grayed out if not repainted manualy

    @updates_setting
    def validate_degree_input(self, text):

        deg = None

        if text:
            try:
                deg = int(text)
            except ValueError:
                self.lock_deg = None
            else:
                if self.lock_var == "Theta":
                    deg_max = 180
                else:
                    deg_max = 360

                if 0 <= deg <= deg_max:
                    self.lock_deg = deg
                else:
                    self.lock_deg = None
        else:
            self.lock_deg = None

        inputIsValid = (text == "" or self.lock_deg is not None)

        if inputIsValid and not self.valid_degree_input:
            self.valid_degree_input = True
            self.lock_input.setStyleSheet("")
        elif not inputIsValid and self.valid_degree_input:
            self.valid_degree_input = False
            self.lock_input.setStyleSheet(
                f"QLineEdit {'{'} background: rgb(255,178,174); selection-background-color: rgb(233, 99, 0); {'}'}"
            )

    def validate_constraint_input(self, text, constr=''):

        if constr == 'min':
            widget = self.min_constraint_input
        elif constr == 'max':
            widget = self.max_constraint_input
        else:
            raise ValueError

        num = None

        if text:

            try:
                num = float(text)
            except ValueError:
                self.constraint[constr] = None
            else:
                self.constraint[constr] = num
        else:
            self.constraint[constr] = None
            num = True

        if num and not self.valid_constraint_input[constr]:
            self.valid_constraint_input[constr] = True
            widget.setStyleSheet("")
        elif not num and self.valid_constraint_input[constr]:
            self.valid_constraint_input[constr] = False
            widget.setStyleSheet(
                f"QLineEdit {'{'} background: rgb(255,178,174); selection-background-color: rgb(233, 99, 0); {'}'}"
            )

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
        self.label_lock.setText(f'{var} =')

        self.validate_degree_input.__wrapped__(self, self.lock_input.text())

    @updates_setting
    def set_file(self):
        filename = QFileDialog.getOpenFileName(self, filter="*.xlsx *.xls")[0]

        if filename:

            self.filename = filename
            self.setWindowTitle("Loading file...")
            self.file_did_finish_loading = False
            QTimer.singleShot(20, self.load_file)

    @updates_setting
    def load_file(self):

        self.xl = antools.read_excel(self.filename, sheet_name=None)
        self.freq_selector.clear()
        self.freq_selector.addItems(sheetname for sheetname in self.xl)
        self.setWindowTitle(self.filename)
        self.file_did_finish_loading = True

    def save_plot(self):
        filename = QFileDialog.getSaveFileName(self, filter="*.png *.svg *.pdf")[0]
        if filename:
            self.canvas.figure.savefig(filename)

    def fastTestSetUp(self):
        df = pd.read_pickle('debug/testdf.pickle')
        self.xl = {
            '10000 MHz': df
        }
        self.setWindowTitle("DEBUG MODE")
        self.lock_deg = 45
        self.polarization = set(["E-Theta", "E-Phi"])
        self.lock_input.setText("45")
        self.freq = "10000 MHz"
        self.file_did_finish_loading = True
        self.freq_selector.addItems(["10000 MHz"])
        self.set_e_phi.setCheckState(2)
        self.set_e_theta.setCheckState(2)
        self.update_gui()
