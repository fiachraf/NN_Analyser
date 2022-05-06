from PyQt5 import QtCore, QtGui, QtWidgets

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        #set Title
        self.setWindowTitle("Custom")

        #set layout to vertical layout
        self.setLayout(QtWidgets.QVBoxLayout())

        #Create a label
        my_label = QtWidgets.QLabel("TEST LABEL")
        #change font
        my_label.setFont(QtGui.QFont("Times New Roman", 18))
        self.layout().addWidget(my_label)




        #opens the window once everything wlse has finished
        self.show()

#needs empty python list passed as argument. IDK Y
app = QtWidgets.QApplication([])
mw = MainWindow()
#runs the application
app.exec_()
