from PyQt5 import QtCore, QtGui, QtWidgets

#QtWidgets contains QGraphicsScene and QGraphicsView
#QtGui contains QBrush QPen, QPainter
#QtCore contains Qt
import sys



class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.title = "Custom"
        self.left = 500
        self.top = 200
        self.width = 600
        self.height = 500
        #self.iconName = "home.png"

        #need to be function calls
        # DON'T FORGET THE BRACKETS AT THE ENDS
        self.createGraphicView()
        self.InitUI()


    def InitUI(self):
        #set Title
        self.setWindowTitle("Custom")
        #set window Icon
        #self.setWindowIcon(QtGui.QIcon(self.iconName))

        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()


        #might need to put this in other section
        #set layout to vertical layout
        # self.setLayout(QtWidgets.QVBoxLayout())

        #Create a label
        # my_label = QtWidgets.QLabel("TEST LABEL")
        #change font
        # my_label.setFont(QtGui.QFont("Times New Roman", 18))
        # self.layout().addWidget(my_label)

    def createGraphicView(self):
        self.scene = QtWidgets.QGraphicsScene()

        self.greenBrush = QtGui.QBrush(QtCore.Qt.green)
        #programs are written with American English
        self.grayBrush = QtGui.QBrush(QtCore.Qt.gray)
        self.pen = QtGui.QPen(QtCore.Qt.red)

        graphicView = QtWidgets.QGraphicsView(self.scene, self)
        graphicView.setGeometry(0, 0, 600, 500)

        #call function to create shapes
        self.shapes()

    def shapes(self):
        #generates ellipse, has green filling and red outside edge
        ellipse = self.scene.addEllipse(20,20,200,200, self.pen, self.greenBrush)

        rect = self.scene.addRect(-100,-100,200,200, self.pen, self.grayBrush)



#needs empty python list passed as argument. IDK Y. Can also pass sys.argv as argument it seems
app = QtWidgets.QApplication([])
mw = MainWindow()
#runs the application
sys.exit(app.exec_())
