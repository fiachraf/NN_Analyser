from PyQt6 import QtCore, QtGui, QtWidgets

#QtWidgets contains QGraphicsScene and QGraphicsView
#QtGui contains QBrush QPen, QPainter
#QtCore contains Qt
import sys
from time import sleep


def hLayout(number_nodes, l_side=0, r_side=1912, node_size=10, node_spacing=30):
    l_side += (5 + node_size)
    r_side -= (5 + node_size)
    center = ((r_side - l_side) / 2) + l_side
    print(f"center: {center}")
    # if (node_size + node_spacing) * number_nodes > (r_side - l_side):
    #     print("ERROR ERROR\ntoo many nodes in a line\nneed to upgrade code")
    #     # TODO: change to throw an exception that I can then handle
    #     return None
    #it can automatically manage higher numbers of nodes than can fit on screen and will add scroll bars automatically
    if number_nodes % 2 == 0:
        #if even number of nodes
        l_node = center - (((number_nodes/2) -1/2) * node_spacing)
        print(f"l_node = {center} -2.5 * ({node_spacing} * 0.5 * {number_nodes})")
        x_coords = [l_node]
        for node_index in range(1, number_nodes):
            x_coords.append(l_node + (node_index * node_spacing))
        return x_coords
    else:
        print(f"l_node = {center} -2 * ({node_spacing} * 0.5 * {number_nodes})")
        l_node = center - (((number_nodes/2) -1/2) * node_spacing)
        x_coords = [l_node]
        for node_index in range(1, number_nodes):
            x_coords.append(l_node + (node_index * node_spacing))
        return x_coords


def vLayout(number_lines, t_side=0, b_side=890, node_size=15):
    # TODO: Fix top and bottom indenting from edges
    t_side += (10 + node_size)
    b_side -= (10 + node_size)

    line_spacing = node_size + 25
    y_coords = [t_side]
    for line_index in range(1, number_lines):
        y_coords.append(y_coords[0] + (line_index * line_spacing))
    return y_coords





class CustomNode(QtWidgets.QGraphicsRectItem):
    def __init__(self, name, *args, **kwargs):
        super(CustomNode, self).__init__(*args, **kwargs)
        #light property, will be unique number for the light
        self._name = name
        print(f"name = {name}")

    # when clicked performs these actions
    # def mouseReleaseEvent(self, event):
    #     print("mouseReleaseEvent")
    def mousePressEvent(self, event):
        print("Mouse Press Event")
        print(self._name)

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.title = "Custom"
        self.left = 500
        self.top = 200
        self.width = 1000
        self.height = 1000
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

        self.showMaximized()
        self.show()
        # sleep(10)


        #might need to put this in other section
        #set layout to vertical layout
        # self.setLayout(QtWidgets.QVBoxLayout())

        #Create a label
        # my_label = QtWidgets.QLabel("TEST LABEL")
        #change font
        # my_label.setFont(QtGui.QFont("Times New Roman", 18))
        # self.layout().addWidget(my_label)





    def createGraphicView(self):
        self.width = self.frameGeometry().width()
        print(f"current width: {self.width}")
        self.scene = QtWidgets.QGraphicsScene()

        self.greenBrush = QtGui.QBrush(QtGui.QColor("green"))
        #programs are written with American English
        self.grayBrush = QtGui.QBrush(QtGui.QColor("gray"))
        self.pen = QtGui.QPen(QtGui.QColor("red"))

        graphicView = QtWidgets.QGraphicsView(self.scene, self)
        # TODO: change to be a variable size which will be the max size of the monitor
        graphicView.setGeometry(0, 0, 1912, 980)

        #this works to add squares to the view but then there is no way to get interactions from these squares
        # for i in range(10):
            #self.scene.addRect(i * 100, i * 100, 10, 10, self.pen )



        #create object to be in list so that all squares can be indexed later
        # class node:
        #     def __init__(nodeself, x_pos, y_pos, width, height):
        #         self.scene.addRect(x_pos,y_pos,width,height,self.pen)
        # test_list = []
        # for i in range(10):
        #     test_list.append(node(i * 100, i * 100, 10, 10))

        #sets colours for ellipses
        pen = QtGui.QPen(QtGui.QColor("dark gray"))
        brush = QtGui.QBrush(QtGui.QColor("lightGray"))

        def addCustomNodes(network_shape):
            y_coords = vLayout(len(network_shape))
            print(f"y_coords: {y_coords}")
            for j, line_y in enumerate(y_coords):
                x_coords = hLayout(network_shape[j])
                print(f"x_coords: {x_coords}")
                for i, node_x in enumerate(x_coords):
                    item = CustomNode(f"cunt{j,i}", node_x, line_y, 20, 20)
                    item.setAcceptHoverEvents(True)
                    item.setPen(pen)
                    item.setBrush(brush)
                    # item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
                    self.scene.addItem(item)

        #node_shape should be a list, len(node_shape) is the number of lines/layers in the network, node_shape[i] is the number of nodes in layer i.
        node_shape = [16, 17, 40, 1]
        addCustomNodes(node_shape)
        #call function to create shapes
        # self.shapes()

    # def shapes(self):
    #     #generates ellipse, has green filling and red outside edge
    #     ellipse = self.scene.addEllipse(20,20,200,200, self.pen, self.greenBrush)
    #
    #     rect = self.scene.addRect(-100,-100,200,200, self.pen, self.grayBrush)



#needs empty python list passed as argument. IDK Y. Can also pass sys.argv as argument to take command line inputs
app = QtWidgets.QApplication([])
mw = MainWindow()
#runs the application
app.exec()
