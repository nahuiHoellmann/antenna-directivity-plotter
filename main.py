from PyQt5.QtWidgets import QApplication
from mainwindow import MainWindow

from argparse import ArgumentParser

if __name__ == '__main__':

    parser = ArgumentParser(description='Display a GUi for atools.py')
    parser.add_argument('--debug', '-d', help='open the application in debug mode', action='store_true')
    args = parser.parse_args()

    app = QApplication([])
    window = MainWindow(debug=args.debug)
    window.show()
    app.exec_()
