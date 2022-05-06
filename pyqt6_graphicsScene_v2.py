from PyQt6 import QtCore, QtGui, QtWidgets

#QtWidgets contains QGraphicsScene and QGraphicsView
#QtGui contains QBrush QPen, QPainter
#QtCore contains Qt
import sys
from time import sleep

#layout functions to arrange nodes evenly in the QGraphicsScene space
def hLayout(number_nodes, l_side=0, r_side=1912, node_size=10, node_spacing=30):
    l_side += (5 + node_size)
    r_side -= (5 + node_size)
    center = ((r_side - l_side) / 2) + l_side
    # print(f"center: {center}")
    # if (node_size + node_spacing) * number_nodes > (r_side - l_side):
    #     print("ERROR ERROR\ntoo many nodes in a line\nneed to upgrade code")
    #     # TODO: change to throw an exception that I can then handle
    #     return None
    #it can automatically manage higher numbers of nodes than can fit on screen and will add scroll bars automatically
    if number_nodes % 2 == 0:
        #if even number of nodes
        l_node = center - (((number_nodes/2) -1/2) * node_spacing)
        # print(f"l_node = {center} -2.5 * ({node_spacing} * 0.5 * {number_nodes})")
        x_coords = [l_node]
        for node_index in range(1, number_nodes):
            x_coords.append(l_node + (node_index * node_spacing))
        return x_coords
    else:
        # print(f"l_node = {center} -2 * ({node_spacing} * 0.5 * {number_nodes})")
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
        # print(f"name = {name}")

    # when clicked performs these actions
    # def mouseReleaseEvent(self, event):
    #     print("mouseReleaseEvent")
    # def mousePressEvent(self, event):
        # print("Mouse Press Event")
        # print(self._name)

# class NodeScene(QtWidgets.QGraphicsScene):
#     def __init__(self, s, y, w, h):
#         super(NodeScene, self).__init__()
#         self.width = w
#         self.height = h
#
#         print("scene created")











#adding my own custom panels to organise everything

class Panel(QtWidgets.QFrame):
    attributes = None
    layout = None

    def __init__(self):
        super(Panel, self).__init__()
        self.InitUI()

    def InitUI(self):
        self.setMinimumSize(20,30)
        # self.setFrameShape(QtWidgets.QFrame.Shape(1))
        # cb = QtWidgets.QCheckBox("Show Title", self)
        #can add layout if desired
        # self.layout = QtWidgets.QVBoxLayout()
        # self.layout.addWidget(cb)

#left hand panel, want it to have the names of the layers arranged horizontally across from their respective layers,
# TODO:
#will need to implement some scrolling functionality for larger networks, might be able to link scroll bars of graphics panel and this one, might need to base it off mouse positioning in the graphics view triggered on a mousePressEvent, might need to make it an additional graphics view of a different part/layer of the graphics scene so that the dragging will affect both
class Left_Panel(Panel):
    def __init__(self):
        super(Left_Panel, self).__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.setFrameShape(QtWidgets.QFrame.Shape(6))

        self.minwidth = 100
        self.minheight = 400
        self.width = self.minwidth
        self.height = self.minheight

    def add_line(self, text):
        self.layout.addWidget(QtWidgets.QLabel(f"line_{text}"))

    def add_lines(self, num_lines):
        for i in range(num_lines):
            self.add_line(i)

#top panel that should act like a tool bar
# TODO:
#Want it to have file dialogs for selecting neural network and also input files, stop/go button, progress bar
class Top_Panel(Panel):
    def __init__(self):
        super(Top_Panel, self).__init__()
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        self.minwidth = 600
        self.minheight = 100
        self.width = self.minwidth
        self.height = self.minheight



        self.layout.addWidget(QtWidgets.QLabel("Enter your deisred structure as a list of numbers, e.g. 40,10,1 where layer 0 has 40 neurons and layer 2 has 1 neuron"))

        # TODO:
        #adds entry box and enter button, should eventually be replaced by a QFileDialog
        entry_box = QtWidgets.QLineEdit()
        entry_box.setObjectName("structure field")
        entry_box.setText("")
        self.layout.addWidget(entry_box)

        confirm_button = QtWidgets.QPushButton("Press me when you have entered your desired structure", clicked = lambda: confirmed())
        self.layout.addWidget(confirm_button)

        def confirmed():
            struct = entry_box.text()
            list_1 = []
            temp = ""
            for inde_1, charac in enumerate(struct):
                if inde_1 == len(struct) - 1:
                    temp = temp + charac
                    list_1.append(int(temp))
                if charac == "," or charac == "":
                    list_1.append(int(temp))
                    temp = ""
                else:
                    temp = temp + charac
            #add new parameter that gives overall structure of neural network
            self.NN_struct = list_1


        # self.layout.addWidget(QtWidgets.QFileDialog())
        # self.setFrameShape(QtWidgets.QFrame.Shape(6))


#right hand panel where details of the selected node will be displayed
# TODO:
#want to make this collapsible
class Right_Panel(Panel):
    def __init__(self):
        super(Right_Panel, self).__init__()

        self.minwidth = 100
        self.minheight = 400
        self.width = self.minwidth
        self.height = self.minheight


        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(QtWidgets.QLabel("right panel"))
        # self.setFrameShape(QtWidgets.QFrame.Shape(6))
        button_2 = QtWidgets.QPushButton("butt 2")
        self.layout.addWidget(button_2)
        #has button added in the main window that resizes the column it is in, to be bigger or smaller
        self.big=False

    # def change_size(self, parent, size):
    #     if self.big == False:
    #         parent.layout().setColumnMinimumWidth(11, 80)
    #     else:
    #         parent.layout().setColumnMinimumWidth(11, 40)


#central panel where the structure of the neural network will be displayed
class Graphics_Panel(Panel):
    def __init__(self):
        super(Graphics_Panel, self).__init__()
        self.createGraphicView()
        # self.layout = QtWidgets.QVBoxLayout()
        # self.setLayout(self.layout)
        # TODO: change this so the border looks nicer
        self.setFrameShape(QtWidgets.QFrame.Shape(6))

        self.minwidth = 400
        self.minheight = 400

        self.width = self.minwidth
        self.height = self.minheight

    def createGraphicView(self):
        # self.width = self.frameGeometry().width()
        #try this to get geometry inside frame
        # self.width = self.Geometry().width()
        # print(f"current width: {self.width}")
        #generates a QGraphicsScene which the QGraphicsView will be "looking at"
        self.scene = QtWidgets.QGraphicsScene()

        # self.greenBrush = QtGui.QBrush(QtGui.QColor("green"))
        #programs are written with American English
        # self.grayBrush = QtGui.QBrush(QtGui.QColor("gray"))
        # self.pen = QtGui.QPen(QtGui.QColor("red"))

        graphicView = QtWidgets.QGraphicsView(self.scene, self)
        # TODO: change to be a variable size which will be the max size of the monitor
        graphicView.setGeometry(0, 0, 1910, 1000)

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
        # pen = QtGui.QPen(QtGui.QColor("dark gray"))
        # brush = QtGui.QBrush(QtGui.QColor("lightGray"))



        def addCustomNodes(network_shape):
            y_coords = vLayout(len(network_shape))
            # print(f"y_coords: {y_coords}")
            for j, line_y in enumerate(y_coords):
                x_coords = hLayout(network_shape[j])
                # print(f"x_coords: {x_coords}")
                for i, node_x in enumerate(x_coords):
                    item = CustomNode(f"cunt{j,i}", node_x, line_y, 20, 20)
                    item.setAcceptHoverEvents(True)
                    # item.setPen(pen)
                    # item.setBrush(brush)
                    # item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
                    self.scene.addItem(item)

        # node_shape should be a list, len(node_shape) is the number of lines/layers in the network, node_shape[i] is the number of nodes in layer i.
        node_shape = [16, 17, 40, 1]
        addCustomNodes(node_shape)



class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.InitUI()
        self.show()

    def resizeEvent(self, event):
        print("Winodw resized")
        QtWidgets.QWidget.resizeEvent(self, event)
        screen = self.geometry()
        print(f"screen: {screen}")

    def InitUI(self):
        self.setWindowTitle("Custom")
        self.setMinimumSize(1000,30)
        #makes it full screen
        self.showMaximized()
        # screen = QtWidgets.QDesktopWidget().screenGeometry()
        screen = self.geometry()
        print(f"screen: {screen}")
        # self.setGeometry(0, 0, screen.width()/2, screen.height()/2)

        # TODO:
        #changing from a grid layout to a combo of horizontal, vertical and grid layout may allow me to have the top panel remain unchanged when I am changing the right panel and could also give me more control over the size of the right panel. Could also implement a more manula approach to it too
        self.setLayout(QtWidgets.QGridLayout())



        self.left_panel = Left_Panel()
        self.left_panel.add_lines(3)
        self.right_panel = Right_Panel()
        self.top_panel = Top_Panel()
        self.graph_panel = Graphics_Panel()
        # button_2 = QtWidgets.QPushButton("Butt 2")

        #number rows, number columns
        grid_size = (12, 12)

        #addWidget(Widget to be added, row position, column position, rows to span, columns to span)
        # -2 needed as indexes start at 0 so to be away from edge need to -2
        self.layout().addWidget(self.left_panel, 1, 0, grid_size[0] - 2, 1)
        self.layout().addWidget(self.right_panel, 1, grid_size[1]-1, grid_size[0] - 2, 1 )
        self.layout().addWidget(self.top_panel, 0,0, 1, grid_size[1])
        self.layout().addWidget(self.graph_panel, 1, 1, grid_size[0] -2, grid_size[1] - 3)

        #trying to make left panel a consistent size
        # self.layout().setColumnMinimumWidth(0, 120)
        QtWidgets.QWidget.resize(self.left_panel, 200, 200)


        self.right_resize_button()

    #adding button to resize the right hand column
    def right_resize_button(self):
        resize_button = QtWidgets.QPushButton("Resize", clicked = lambda: resize_click())
        self.right_panel.layout.addWidget(resize_button)

        def resize_click():
            if self.right_panel.big == False:
                # self.layout().setColumnMaximumWidth(11, 401)
                self.layout().setColumnMinimumWidth(11, 400)
                # self.layout().setColumnStretch(11, 1)
                self.right_panel.big = True

            else:
                # self.layout().setColumnStretch(11, 0)
                self.right_panel.big = False
                #minimum width is not necessarily the size of the column, would need to make other columns bigger to force this column to become very small, otherwise it will become the width that the Layout gives it
                self.layout().setColumnMinimumWidth(11, 5)
                # self.layout().setColumnMaximumWidth(11, 41)



        #changing some frame details
        # right_panel = QtWidgets.QFrame()
        # right_panel.setFrameShape(QtWidgets.QFrame.Shape(1))
        # widget = QtWidgets.QWidget()
        # widget.setLayout(layout)
        # self.setCentralWidget(widget)

        # screen = QtWidgets.QDesktopWidget().screenGeometry()
        # self.setGeometry(0, 0, screen.width()/2, screen.height()/2)
        # self.show()



#needs empty python list passed as argument. IDK Y. Can also pass sys.argv as argument to take command line inputs
app = QtWidgets.QApplication([])
mw = MainWindow()

#runs the application
app.exec()

# sleep(5)
# screen_1 = mw.geometry()
# print(f"screen_1: {screen_1}")
