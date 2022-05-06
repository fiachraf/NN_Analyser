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



#adding my own custom panels to organise everything

class Panel(QtWidgets.QFrame):
    attributes = None
    layout = None

    def __init__(self, *args, **kwargs):
        super(Panel, self).__init__(*args, **kwargs)
        self.InitUI()

    def InitUI(self):
        self.setMinimumSize(20,30)
        self.setFrameShape(QtWidgets.QFrame.Shape(1))
        # cb = QtWidgets.QCheckBox("Show Title", self)
        #can add layout if desired
        # self.layout = QtWidgets.QVBoxLayout()
        # self.layout.addWidget(cb)

#left hand panel, want it to have the names of the layers arranged horizontally across from their respective layers,
# TODO:
#will need to implement some scrolling functionality for larger networks, might be able to link scroll bars of graphics panel and this one, might need to base it off mouse positioning in the graphics view triggered on a mousePressEvent, might need to make it an additional graphics view of a different part/layer of the graphics scene so that the dragging will affect both
class Left_Panel(Panel):
    def __init__(self, *args, **kwargs):
        super(Left_Panel, self).__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.setFrameShape(QtWidgets.QFrame.Shape(6))

        self.minwidth = 200
        self.minheight = 400
        self.setBaseSize(self.minwidth, self.minheight)
        self.resize(self.minwidth, self.minheight)

    def add_line(self, text):
        self.layout.addWidget(QtWidgets.QLabel(f"line_{text}"))

    def add_lines(self, num_lines):
        for i in range(num_lines):
            self.add_line(i)


#top panel that should act like a tool bar
# TODO:
#Want it to have file dialogs for selecting neural network and also input files, stop/go button, progress bar
class Top_Panel(Panel):

    NN_struct = QtCore.pyqtSignal(list)

    def __init__(self, *args, **kwargs):
        super(Top_Panel, self).__init__(*args, **kwargs)
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        self.minwidth = 600
        self.minheight = 100
        self.setBaseSize(self.minwidth, self.minheight)
        self.resize(self.minwidth, self.minheight)



        self.layout.addWidget(QtWidgets.QLabel("Enter your deisred structure as a list of numbers, e.g. 40,10,1 where layer 0 has 40 neurons and layer 2 has 1 neuron"))

        # TODO:
        #adds entry box and enter button, should eventually be replaced by a QFileDialog
        entry_box = QtWidgets.QLineEdit()
        entry_box.setObjectName("structure field")
        entry_box.setText("")
        self.layout.addWidget(entry_box)

        #added as an attribute so it can be accessed by the mainwindow widget
        self.confirm_button = QtWidgets.QPushButton("Press me when you have entered your desired structure", clicked = lambda: confirmed())
        self.layout.addWidget(self.confirm_button)

        def confirmed():
            # print("test")
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

            #emit signal that has structure of NN as list, signal will then be connected to another function in the main window
            self.NN_struct.emit(list_1)


        # self.layout.addWidget(QtWidgets.QFileDialog())
        # self.setFrameShape(QtWidgets.QFrame.Shape(6))


#right hand panel where details of the selected node will be displayed
class Right_Panel(Panel):
    def __init__(self, *args, **kwargs):
        super(Right_Panel, self).__init__(*args, **kwargs)

        self.minwidth = 100
        self.minheight = 400
        self.setBaseSize(self.minwidth, self.minheight)
        self.resize(self.minwidth, self.minheight)


        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(QtWidgets.QLabel("right panel"))
        # self.setFrameShape(QtWidgets.QFrame.Shape(6))
        button_2 = QtWidgets.QPushButton("butt 2")
        self.layout.addWidget(button_2)
        #has button added in the main window that resizes the column it is in, to be bigger or smaller
        self.big=False
#create custom QGraphicsView class to take advantage of event handles/functions

class CustView(QtWidgets.QGraphicsView):
    def __init__(self, *args, **kwargs):
        super(CustView, self).__init__(*args, **kwargs)
        # print("test")
        # self.setDragMode(QtWidgets.QGraphicsView.DragMode(1))
        # print(f"Drag Mode : {self.DragMode(1)}")

        # item = CustomNode(f"cunt{j,i}", node_x, line_y, 20, 20)
        # item.setAcceptHoverEvents(True)
        # # item.setPen(pen)
        # # item.setBrush(brush)
        # # item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        # self.scene.addItem(item)
    #for tracking movement of view
    def dragMoveEvent(self,event):
        print("test")

    def mousePressEvent(self, event):
        print("test66")

class CustScene(QtWidgets.QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super(CustScene, self).__init__(*args, **kwargs)
        print("test")
        # self.setDragMode(QtWidgets.QGraphicsView.DragMode(1))
        # print(f"Drag Mode : {self.DragMode(1)}")

        # item = CustomNode(f"cunt{j,i}", node_x, line_y, 20, 20)
        # item.setAcceptHoverEvents(True)
        # # item.setPen(pen)
        # # item.setBrush(brush)
        # # item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        # self.scene.addItem(item)
        self.sceneRectChanged.connect(self.test_func_1)

    #for tracking movement of view
    def dragMoveEvent(self,event):
        #I think this applies to objects being dragged in the scene and not the view/scene being dragged
        print("test39")

    def mousePressEvent(self, event):
        print("test67")

    # def mouseMoveEvent(self, event):
        # print("test68")


    def test_func_1(self, rect):
        print("test99")

#central panel where the structure of the neural network will be displayed
class Graphics_Panel(Panel):
    def __init__(self, *args, **kwargs):
        super(Graphics_Panel, self).__init__(*args, **kwargs)




        self.createGraphicView()

        # TODO: change this so the border looks nicer
        self.setFrameShape(QtWidgets.QFrame.Shape(6))

        self.minwidth = 400
        self.minheight = 400
        self.setBaseSize(self.minwidth, self.minheight)
        self.resize(self.minwidth, self.minheight)

        self.graphicView.rubberBandChanged.connect(self.test_func_2)
        self.graphicView.verticalScrollBar().valueChanged.connect(self.test_func_4)
        self.test_func_3()
    def test_func_2(self, rect, p1, p2):
        print("test77")

    def test_func_3(self):
        # if self.graphicView.isTranformed == True:
            # print("fuck")
        pass
    def test_func_4(self, scroll_index):
        print("fuck2")
    def createGraphicView(self):
        #initial setup for the central pane

        #generates a QGraphicsScene which the QGraphicsView will be "looking at"
        self.scene = CustScene()
        #QGraphicsView of the QGraphicsScene
        self.graphicView = QtWidgets.QGraphicsView(self.scene, self)

        #IDK if this line is needed. it is not
        # self.graphicView.setScene(self.scene)

        #set size of graphics view initially, gets changed when window is resized
        self.graphicView.setGeometry(0, 0, 300, 400)

        #set view to move when dragged with mouse
        # self.graphicView.setDragMode(QtWidgets.QGraphicsView.DragMode(1))
        # print(f"Drag Mode : {self.graphicView.DragMode(1)}")

        self.graphicView.setDragMode(QtWidgets.QGraphicsView.DragMode(1))


        # TODO: Add parameters to self. for brush and pen etc.

        # node_shape should be a list, len(node_shape) is the number of lines/layers in the network, node_shape[i] is the number of nodes in layer i.
        node_shape = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,400]
        self.addCustomNodes(node_shape)

    #add Nodes to the scene
    def addCustomNodes(self, network_shape):
        #clear the grapics scene so that whenever this function is called it starts with a blank slate
        self.scene.clear()


        y_coords = vLayout(len(network_shape))
        #for each layer/line
        for j, line_y in enumerate(y_coords):
            x_coords = hLayout(network_shape[j])
            #for each neuron/node in the layer/line
            for i, node_x in enumerate(x_coords):
                item = CustomNode(f"cunt{j,i}", node_x, line_y, 20, 20)
                item.setAcceptHoverEvents(True)
                # item.setPen(pen)
                # item.setBrush(brush)
                # item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
                self.scene.addItem(item)


#Main Window to be displayed

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.InitUI()
        self.show()
        #makes it full window
        self.showMaximized()

    def resizeEvent(self, event):
        QtWidgets.QWidget.resizeEvent(self, event)

        #change left panel height
        self.left_panel.resize(self.left_panel.width(), self.height() - self.top_panel.height())
        #change top_panel width, and right_panel position and height
        self.top_panel.resize(self.width(), self.top_panel.height())
        self.right_panel.resize(self.right_panel.width(), self.height() - self.top_panel.height())
        self.right_panel.move((self.width() - self.right_panel.width()), self.top_panel.height())
        #change graph_panel size
        self.graph_panel.resize(self.width() - (self.left_panel.width() + self.right_panel.width()), self.height() - self.top_panel.height())
        #change graph_panel view
        self.graph_panel.graphicView.setGeometry(0, 0, self.graph_panel.width(), self.graph_panel.height())

    def InitUI(self):
        self.setWindowTitle("Custom GUI")
        self.setMinimumSize(700,500)

        #add panels to MainWindow widget
        self.left_panel = Left_Panel(self)
        self.left_panel.add_lines(3)
        self.right_panel = Right_Panel(self)
        self.top_panel = Top_Panel(self)
        self.graph_panel = Graphics_Panel(self)

        #doing manual initial posistioning
        self.top_panel.move(0,0)
        self.left_panel.move(0, self.top_panel.height())
        self.graph_panel.move(self.left_panel.width(), self.top_panel.height())
        self.right_panel.move((self.width() - self.right_panel.width()), self.top_panel.height())

        #adds resize button for right panel
        self.right_resize_button()

        #handling input from the top_panel
        self.top_panel.NN_struct.connect(self.disp_NN_struct)

    #function used to get signal emitted from top panel function to grahpics view panel to generate the required shapes
    def disp_NN_struct(self, NN_struct):
        print("6test")
        self.graph_panel.addCustomNodes(NN_struct)

    #adding button to resize the right hand column
    def right_resize_button(self):
        resize_button = QtWidgets.QPushButton("Resize", clicked = lambda: resize_click())
        self.right_panel.layout.addWidget(resize_button)

        def resize_click():
            if self.right_panel.big == False:
                #move and resize right_panel
                self.right_panel.resize(400, self.height() - self.top_panel.height())
                self.right_panel.move((self.width() - self.right_panel.width()), self.top_panel.height())

                self.right_panel.big = True

                #resize graph_panel
                self.graph_panel.resize(self.width() - (self.left_panel.width() + self.right_panel.width()), self.height() - self.top_panel.height())
                #change graph_panel view
                self.graph_panel.graphicView.setGeometry(0, 0, self.graph_panel.width(), self.graph_panel.height())

            else:
                #move and resize right_panel
                self.right_panel.resize(self.right_panel.minwidth, self.height() - self.top_panel.height())
                self.right_panel.move((self.width() - self.right_panel.width()), self.top_panel.height())


                self.right_panel.big = False

                #resize graph_panel
                self.graph_panel.resize(self.width() - (self.left_panel.width() + self.right_panel.width()), self.height() - self.top_panel.height())
                #change graph_panel view
                self.graph_panel.graphicView.setGeometry(0, 0, self.graph_panel.width(), self.graph_panel.height())



#needs empty python list passed as argument. IDK Y. Can also pass sys.argv as argument to take command line inputs
app = QtWidgets.QApplication([])
mw = MainWindow()

#runs the application, windwo will only open after this line
app.exec()

# sleep(5)
# screen_1 = mw.geometry()
# print(f"screen_1: {screen_1}")
