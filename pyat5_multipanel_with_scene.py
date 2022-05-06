#Program Stucture
'''
-Main Widget
   |
    - drawing Area
   |
    - Attributes pannel
              |
               - Attributes based on selected node
'''

#import code mods
import sys
from PyQt4 import QtGui, QtCore
from array import *



'''
Check Click events on the scene Object
Also Stores the node data
Not related to issue but needed for demonstration
'''
class Scene(QtGui.QGraphicsScene):

    nodes = []
    connections = []
    selectedNodeID = None

    def __init__(self, x, y, w, h, p):
        super(Scene, self).__init__()
        self.width = w
        self.height = h
        print 'scene created'

    def mousePressEvent(self, e):
        #print("Scene got mouse press event")
        #print("Event came to us accepted: %s"%(e.isAccepted(),))
        QtGui.QGraphicsScene.mousePressEvent(self, e)

    def mouseReleaseEvent(self, e):
        #print("Scene got mouse release event")
        #print("Event came to us accepted: %s"%(e.isAccepted(),))
        QtGui.QGraphicsScene.mouseReleaseEvent(self, e)

    def dragMoveEvent(self, e):
        QtGui.QGraphicsScene.dragMoveEvent(self, e)


'''
This widget acts as a container for user options. I have added a check box for testing
'''
class sidePannel(QtGui.QWidget):

    attributes = None
    layout = None

    def __init__(self):
        super(sidePannel, self).__init__()
        self.initUI()

    def initUI(self):
        self.setMinimumSize(1, 30)
        self.layout = QtGui.QVBoxLayout()

        cb = QtGui.QCheckBox('Show title', self)
        self.layout.addWidget(cb)


'''
Main contanier for the scene and sidePannel
'''

class mainWindowWidget(QtGui.QWidget):
    view = None
    scene = None
    appSidePannel = None

    leftFrame = None
    rightFrame = None

    layout = None

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.initScene()
        self.show()

    def initScene(self):


        #This is what I want but will not work....
        self.scene = Scene(0, 0, 50, 50, self)
        self.view = QtGui.QGraphicsView()
        self.view.setScene(self.scene)
        self.layout = QtGui.QHBoxLayout(self)
        self.setLayout(self.layout)

        '''
        #What works to check. This gives me the correct layout. want to use a QGraphicsView instead of QPushButton
        self.view = QtGui.QPushButton("Button 1", self)
        '''



        self.appSidePannel = sidePannel()

        self.layout = QtGui.QHBoxLayout(self)

        self.leftFrame = self.view
        self.rightFrame = self.appSidePannel

        self.layout.addWidget(self.leftFrame)
        self.layout.addWidget(self.rightFrame)




class MainWindowUi(QtGui.QMainWindow):
    def __init__(self):

        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle('RIS RIB Generator')

        screen = QtGui.QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, screen.width()/2, screen.height()/2)

        mainwindowwidget = mainWindowWidget()
        self.setCentralWidget(mainwindowwidget)

        exitAction = QtGui.QAction(QtGui.QIcon('exit24.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        self.statusBar()
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')

        fileMenu.addAction(exitAction)

'''
Start Point
'''
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    win = MainWindowUi()
    win.show()
    sys.exit(app.exec_())
