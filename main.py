from PyQt5.QtWidgets import QApplication
from MainWindow import MainWindow

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()


# def loc_phi(deg, df):
#   return df.iloc[range(x, 65341 + x, 361)]

# def loc_theta(deg, df):
#   return df[x*360 +x: (x +1) * 360 + x +1]

# def sample(io, loc,)