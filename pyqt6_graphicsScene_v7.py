from PyQt6 import QtCore, QtGui, QtWidgets

#QtWidgets contains QGraphicsScene and QGraphicsView
#QtGui contains QBrush QPen, QPainter
#QtCore contains Qt
import sys
from time import sleep
import analyser_backend_v2
import traceback
import numpy as np

#layout functions to arrange nodes evenly in the QGraphicsScene space
def hLayout(number_nodes, l_side=0, r_side=1912, node_size=10, node_spacing=30):
    l_side += (5 + node_size)
    r_side -= (5 + node_size)
    center = ((r_side - l_side) / 2) + l_side

    #it can automatically manage higher numbers of nodes than can fit on screen and will add scroll bars automatically
    if number_nodes % 2 == 0:
        #if even number of nodes
        l_node = center - (((number_nodes/2) -1/2) * node_spacing)
        x_coords = [l_node]
        for node_index in range(1, number_nodes):
            x_coords.append(l_node + (node_index * node_spacing))
        return x_coords
    else:
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

    # QGraphicsItems can't emit signals so all click events are handled by scene and this class will simply exist to hold data that will be accessed

    def __init__(self, neuron, *args, **kwargs):
        super(CustomNode, self).__init__(*args, **kwargs)
        self.neuron = neuron
        self._brush = QtGui.QBrush(QtGui.QColor("light gray"))

    def setBrush(self, brush_color):
        self._brush = QtGui.QBrush(brush_color)
        self.update()

    def paint(self, painter=None, style=None, widget=None):
        painter.fillRect(self.boundingRect(), self._brush)
    # when clicked performs these actions
    def mousePressEvent(self, event):
        print("mousePressEvent")
        print(f"self.neuron.mean: {self.neuron.mean}")
        print(f"self.neuron.max: {self.neuron.max}")
        print(f"self.neuron.min: {self.neuron.min}")
        print(f"self.neuron.num_inputs: {self.neuron.num_inputs}")
        for key in self.neuron.labels_dict:
            print(f"label: {key}, self.neuron.labels_dict[key].mean: {self.neuron.labels_dict[key].mean}")
            print(f"label: {key}, self.neuron.labels_dict[key].max: {self.neuron.labels_dict[key].max}")
            print(f"label: {key}, self.neuron.labels_dict[key].min: {self.neuron.labels_dict[key].min}")
            print(f"label: {key}, self.neuron.labels_dict[key].num_inputs: {self.neuron.labels_dict[key].num_inputs}")




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

#need custom scene to get signals from objects when clicked, as the QGraphicsItems can't emit signals
class CustScene(QtWidgets.QGraphicsScene):

    node_clicked = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(CustScene, self).__init__(*args, **kwargs)
        self.initScene()

    def initScene(self):
        self.clear()

    #could create a QObject in lieu of this but as usual the documentation for this module is dogshit
    #Could also try creating a cutom QEvent but those don't seem to actually be added to the event queue when they're custom
    @QtCore.pyqtSlot()
    def mousePressEvent(self,event):
        #if the mouse is clicked on the scene and the click position corresponds to a Node on the scene then emit the signal
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.point_2 = self.itemAt(event.scenePos(), QtGui.QTransform())
            if self.point_2 != None:
                self.node_clicked.emit()


#left hand panel, has layer names across from the layers displayed in the central panel
# TODO: labels are slightly off, need to set position of text while taking into account text center, also not perfect when scrolled to top or bottom of view, becomes slightly more offset
class Left_GraphPanel(Panel):
    def __init__(self, *args, **kwargs):
        super(Left_GraphPanel, self).__init__(*args, **kwargs)

        self.createGraphicView()

        # TODO: change this so the border looks nicer
        self.setFrameShape(QtWidgets.QFrame.Shape(6))

        self.minwidth = 200
        self.minheight = 400
        self.setBaseSize(self.minwidth, self.minheight)
        self.resize(self.minwidth, self.minheight)


    def match_scroll(self, scroll_index):
        #match scrolling of central panel and left panel, connected using singals in MainWindow
        self.graphicView.verticalScrollBar().setValue(scroll_index)

    def createGraphicView(self):
        #initial setup for the left panel
        #generates a QGraphicsScene which the QGraphicsView will be "looking at"
        self.scene = QtWidgets.QGraphicsScene()
        #QGraphicsView of the QGraphicsScene
        self.graphicView = QtWidgets.QGraphicsView(self.scene, self)
        #set size of graphics view initially, gets changed when window is resized
        self.graphicView.setGeometry(0, 0, 200, 400)

    def addlines(self, NN_struct):
        self.scene.clear()
        num_lines = len(NN_struct.layer_list)
        y_coords = vLayout(num_lines)
        for j, layer_y in enumerate(NN_struct.layer_list):
            rect_1 = QtWidgets.QGraphicsRectItem(0, y_coords[j], 10, 10)
            item = QtWidgets.QGraphicsSimpleTextItem(f"{layer_y.layer_type}", rect_1)
            item.setPos(0,y_coords[j])
            self.scene.addItem(item)


#top panel that should act like a tool bar

class Top_Panel(Panel):

    NN_struct = QtCore.pyqtSignal(list)
    NN_Name = QtCore.pyqtSignal(str)
    file_dir = QtCore.pyqtSignal(str)
    start_analysis = QtCore.pyqtSignal(bool)
    metric_change = QtCore.pyqtSignal(str)
    label_change = QtCore.pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(Top_Panel, self).__init__(*args, **kwargs)
        self.layout_1 = QtWidgets.QVBoxLayout()
        self.layout_2 = QtWidgets.QHBoxLayout()
        self.layout_3 = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout_1)

        self.layout_1.addLayout(self.layout_2)
        self.layout_1.addLayout(self.layout_3)
        self.minwidth = 600
        self.minheight = 100
        self.setBaseSize(self.minwidth, self.minheight)
        self.resize(self.minwidth, self.minheight)


        # TODO:
        # grey out/make unselectable the buttons so you can only press them in order left to right
        #add stop button
        #make progress bar better to include time for colour calculations
        self.layout_2.addWidget(QtWidgets.QPushButton("Choose Neural Network", clicked = lambda: self.NN_button()))
        self.layout_2.addWidget(QtWidgets.QPushButton("Choose Files to test", clicked = lambda: self.files_button()))

        #added as an attribute so it can be accessed by the mainwindow widget
        self.confirm_button = QtWidgets.QPushButton("Start Analysis", clicked = lambda: self.confirmed())
        self.layout_2.addWidget(self.confirm_button)
        self.metric_dropdown = QtWidgets.QComboBox(self)
        self.label_dropdown = QtWidgets.QComboBox(self)

        self.layout_2.addWidget(self.metric_dropdown)
        self.layout_2.addWidget(self.label_dropdown)

        self.metric_dropdown.addItem("mean")
        self.metric_dropdown.addItem("max")
        self.metric_dropdown.addItem("min")
        self.label_dropdown.addItem("Overall")

        self.prog_bar = QtWidgets.QProgressBar()
        self.layout_3.addWidget(self.prog_bar)
        self.prog_label = QtWidgets.QLabel("")
        self.layout_3.addWidget(self.prog_label)

        #combo box changes connected to functions in MainWindow


    def update_progress(self, progress):
        if progress[-1] == "analysing":
            self.prog_label.setText("Analysing inputs")
        elif progress[-1] == "coloring":
            self.prog_label.setText("Coloring Plot")
        self.prog_bar.setRange(0, progress[1])
        self.prog_bar.setValue(progress[0])
        if progress[0] == progress[1]:
            self.prog_label.setText("")


    def confirmed(self):
        self.start_analysis.emit(True)

    #QFileDialog.getOpenFileName returns a tuple, [0] is the name, [1] is the file type filter selected by the user using the dropdown box in the bottom rigth corner of the window
    def NN_button(self):
        print("choose /home/fiachra/atom_projects/meteorml/keras/meteorml_20220220_4.h5")
        N_N_name = QtWidgets.QFileDialog.getOpenFileName(self, "Choose Neural Network", "/home/fiachra/atom_projects/meteorml/keras/", "h5 files (*.h5)")
        #only emit if file chosen
        if N_N_name:
            self.NN_Name.emit(N_N_name[0])
    def files_button(self):
        print("choose /home/fiachra/Downloads/Meteor_Files/20210131_pngs")
        file_dir_name = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose File Directory", "/home/fiachra/Downloads/Meteor_Files/20210131_pngs")
        if file_dir_name:
            self.file_dir.emit(file_dir_name)

        # self.setFrameShape(QtWidgets.QFrame.Shape(6))


#right hand panel where details of the selected node will be displayed
class Right_Panel(Panel):

    right_panel_big = QtCore.pyqtSignal()

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
        self.button_2 = QtWidgets.QPushButton("resize")
        self.layout.addWidget(self.button_2)
        self.button_2.clicked.connect(self.resize_panel)

        #has button added in the main window that resizes the column it is in, to be bigger or smaller
        self.big=False

    @QtCore.pyqtSlot()
    def resize_panel(self):
        self.right_panel_big.emit()


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

    def match_scroll(self, scroll_index):
        #match scrolling of central panel and left panel, connected using singals in MainWindow
        self.graphicView.verticalScrollBar().setValue(scroll_index)

    def createGraphicView(self):
        #initial setup for the central pane
        #generates a QGraphicsScene which the QGraphicsView will be "looking at"
        self.scene = CustScene()
        #QGraphicsView of the QGraphicsScene
        self.graphicView = QtWidgets.QGraphicsView(self.scene, self)
        #set size of graphics view initially, gets changed when window is resized
        self.graphicView.setGeometry(0, 0, 300, 400)
        #set view to move when dragged with mouse
        self.graphicView.setDragMode(QtWidgets.QGraphicsView.DragMode(1))

        # TODO: Add parameters to self. for brush and pen etc.

        self.pen = QtGui.QPen(QtGui.QColor("dark gray"))
        self.brush = QtGui.QBrush(QtGui.QColor("lightGray"))


    #add Nodes to the scene
    def addCustomNodes(self, cust_NN_class):
        #clear the grapics scene so that whenever this function is called it starts with a blank slate
        self.scene.clear()

        y_coords = vLayout(len(cust_NN_class.layer_list))
        #for each layer/line
        for j, layer_y in enumerate(cust_NN_class.layer_list):
            x_coords = hLayout(len(layer_y.neuron_list))
            #for each neuron/node in the layer/line
            for i, node_x in enumerate(layer_y.neuron_list):
                item = CustomNode(node_x, x_coords[i], y_coords[j], 20, 20)
                item.setAcceptHoverEvents(True)
                item.setPen(self.pen)
                item.setBrush(self.brush)
                self.scene.addItem(item)

#Worker class for handling progress bar updates
class Worker(QtCore.QObject):

    finished = QtCore.pyqtSignal()
    analyse_progress = QtCore.pyqtSignal(object)

    def __init__(Workerself, Neural_Net):
        super(Worker, Workerself).__init__()
        Workerself.Neural_Net = Neural_Net

    def run(Workerself):
        old_progress = Workerself.Neural_Net.progress[0]
        while Workerself.Neural_Net.progress[0] < Workerself.Neural_Net.progress[1]:
            sleep(0.5)
            new_progress = Workerself.Neural_Net.progress
            if old_progress < new_progress[0]:
                Workerself.analyse_progress.emit((new_progress[0], new_progress[1], "analysing"))
                old_progress = new_progress[0]
        new_progress = Workerself.Neural_Net.progress
        if old_progress < new_progress[0]:
            Workerself.analyse_progress.emit((new_progress[0], new_progress[1], "analysing"))
            old_progress = new_progress[0]
        Workerself.finished.emit()



#Main Window to be displayed

class MainWindow(QtWidgets.QWidget):

    coloring_prog = QtCore.pyqtSignal(object)

    def __init__(self):
        super(MainWindow, self).__init__()

        self.InitUI()
        self.show()
        #makes it full window
        self.showMaximized()


    def InitUI(self):
        self.setWindowTitle("Custom GUI")
        self.setMinimumSize(700,500)

        #add panels to MainWindow widget
        self.left_panel = Left_GraphPanel(self)
        # self.left_panel.add_lines(3)
        self.right_panel = Right_Panel(self)
        self.top_panel = Top_Panel(self)
        self.graph_panel = Graphics_Panel(self)

        #doing manual initial posistioning
        self.top_panel.move(0,0)
        self.left_panel.move(0, self.top_panel.height())
        self.graph_panel.move(self.left_panel.width(), self.top_panel.height())
        self.right_panel.move((self.width() - self.right_panel.width()), self.top_panel.height())

        #syncing scroll for left graph panel and graph panel
        self.graph_panel.graphicView.verticalScrollBar().valueChanged.connect(self.left_panel.match_scroll)
        self.left_panel.graphicView.verticalScrollBar().valueChanged.connect(self.graph_panel.match_scroll)

        #connect resize buttons to resize function
        self.right_panel.right_panel_big.connect(self.expand_right_panel)
        self.graph_panel.scene.node_clicked.connect(self.node_click_func)

        #connect file/directory names to function to generate proper weighting on display
        self.top_panel.NN_Name.connect(self.layout_nodes)
        self.top_panel.file_dir.connect(self.set_file_directory)
        self.top_panel.start_analysis.connect(self.start)

        self.top_panel.metric_dropdown.currentTextChanged.connect(self.update_metric_colors)
        self.top_panel.label_dropdown.currentTextChanged.connect(self.update_label_colors)

        self.coloring_prog.connect(self.top_panel.update_progress)




        self.file_dir = None
        self.Neural_Network = None

    #could probably condense these two update functions to 1
    def update_metric_colors(self):
        new_metric = self.top_panel.metric_dropdown.currentText()
        graph_items_list = self.graph_panel.scene.items()
        for graph_item in graph_items_list:
            if isinstance(graph_item, CustomNode) == True:
                if self.top_panel.label_dropdown.currentText() == "Overall":
                    new_brush = graph_item.neuron.colors[new_metric]
                    graph_item.setBrush(new_brush)
                else:
                    self.update_label_colors()



    def update_label_colors(self):
        new_label = self.top_panel.label_dropdown.currentText()
        new_metric = self.top_panel.metric_dropdown.currentText()
        graph_items_list = self.graph_panel.scene.items()
        if new_label == "Overall":
            self.update_metric_colors()
        else:
            for graph_item in graph_items_list:
                if isinstance(graph_item, CustomNode) == True:
                    new_brush = graph_item.neuron.labels_dict[str(new_label)].colors[new_metric]
                    graph_item.setBrush(new_brush)

    def node_click_func(self):
        if self.right_panel.big == False:
            self.expand_right_panel()
            # TODO: get graphics scene to focus on node when clicked and change outline colour to highlight it

    def assign_colours(self):
        #colour is black if value == 0, blue if value within 5% of rang +- of layer mean, green if greater than mean and red if less than mean
        #np.mean() is used to get average of attributes to compare values from the 2D layers
        def overall_coloring(layer, neuron, comp_metric):
        #comp metric = mean, min or max
            layer_range = np.mean(layer_to_colour.max) - np.mean(layer_to_colour.min)
            #for comparisons it is; neuron mean vs layer mean, neuron max vs layer avg max, neuron min vs layer avg min
            if comp_metric == "max" or comp_metric == "min":
                layer_metric = getattr(layer, f"avg_{comp_metric}")
            else:
                layer_metric = getattr(layer, comp_metric)

            neuron_metric = getattr(neuron, comp_metric)
            if np.mean(neuron_metric) == 0.0:
                neuron.colors[comp_metric] = QtGui.QColor("black")
            elif np.mean(neuron_metric) > np.mean(layer_metric) - ((5/100) * layer_range) and np.mean(neuron_metric) < np.mean(layer_metric) + ((5/100) * layer_range):
                neuron.colors[comp_metric] = QtGui.QColor("blue")
            elif np.mean(neuron_metric) > np.mean(layer_metric):
                neuron.colors[comp_metric] = QtGui.QColor("green")
            elif np.mean(neuron_metric) < np.mean(layer_metric):
                neuron.colors[comp_metric] = QtGui.QColor("red")

        def label_coloring(subneuron, comp_metric):
        #comp metric = avg, min or max
            neuron_range = np.mean(subneuron.parent_neuron.max) - np.mean(subneuron.parent_neuron.min)
            parent_neuron_metric = getattr(subneuron.parent_neuron, comp_metric)
            subneuron_metric = getattr(subneuron, comp_metric)
            #should really replace the np.mean in this test for better one
            if np.mean(subneuron_metric) == 0.0:
                subneuron.colors[comp_metric] = QtGui.QColor("black")
            elif np.mean(subneuron_metric) > np.mean(parent_neuron_metric) - ((5/100) * neuron_range) and np.mean(subneuron_metric) < np.mean(parent_neuron_metric) + ((5/100) * neuron_range):
                subneuron.colors[comp_metric] = QtGui.QColor("blue")
            elif np.mean(subneuron_metric) > np.mean(parent_neuron_metric):
                subneuron.colors[comp_metric] = QtGui.QColor("green")
            elif np.mean(subneuron_metric) < np.mean(parent_neuron_metric):
                subneuron.colors[comp_metric] = QtGui.QColor("red")


        for color_prog_index, layer_to_colour in enumerate(self.Neural_Network.layer_list):
            for color_prog_index_1, neuron_to_colour in enumerate(layer_to_colour.neuron_list):

                #mean compared to layer mean
                overall_coloring(layer_to_colour, neuron_to_colour, "mean")
                #max compared to layer mean
                overall_coloring(layer_to_colour, neuron_to_colour, "max")
                #min compared to layer mean
                overall_coloring(layer_to_colour, neuron_to_colour, "min")
                #for each label
                for label in neuron_to_colour.labels_dict:
                    label_coloring(neuron_to_colour.labels_dict[label], "mean")
                    label_coloring(neuron_to_colour.labels_dict[label], "max")
                    label_coloring(neuron_to_colour.labels_dict[label], "min")
            self.coloring_prog.emit((color_prog_index, len(self.Neural_Network.layer_list) - 1, "coloring"))
        self.update_metric_colors()



    def set_file_directory(self, directory_name):
        self.file_dir = directory_name

    def layout_nodes(self, NN_name):
        self.Neural_Network = analyser_backend_v2.Neural_Net(NN_name)
        self.graph_panel.addCustomNodes(self.Neural_Network)
        self.left_panel.addlines(self.Neural_Network)

    def start(self, started):
        # TODO: add option to stop analysis part way through if cancel button clicked
        try:
            self.Neural_Network.set_file_dir(self.file_dir)
            self.Neural_Network.get_all_layers_activations()

            #creating QThread to check the progress of analysis for the progress bar
            self.prog_thread = QtCore.QThread()
            self.worker = Worker(self.Neural_Network)
            self.worker.moveToThread(self.prog_thread)
            self.prog_thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.prog_thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.finished.connect(self.prog_thread.deleteLater)

            #assigning worker signals to additional functions
            self.worker.analyse_progress.connect(self.top_panel.update_progress)
            self.worker.finished.connect(self.assign_colours)
            self.worker.finished.connect(self.update_labels_box)
            #start thread
            self.prog_thread.start()

        except AttributeError:
            print("please choose a model and/or file directory")
        except Exception:
            print(traceback.format_exc())
            sys.exit()

    def update_labels_box(self):
        ref_labels_dict = self.Neural_Network.layer_list[-1].neuron_list[0].labels_dict

        for key in ref_labels_dict:
            self.top_panel.label_dropdown.addItem(str(key))

    def resizeEvent(self, event):
        QtWidgets.QWidget.resizeEvent(self, event)

        #change left graph panel height
        self.left_panel.resize(self.left_panel.width(), self.height() - self.top_panel.height())
        #change left graph_panel view
        self.left_panel.graphicView.setGeometry(0, 0, self.left_panel.width(), self.left_panel.height())
        #change top_panel width, and right_panel position and height
        self.top_panel.resize(self.width(), self.top_panel.height())
        self.right_panel.resize(self.right_panel.width(), self.height() - self.top_panel.height())
        self.right_panel.move((self.width() - self.right_panel.width()), self.top_panel.height())
        #change graph_panel size
        self.graph_panel.resize(self.width() - (self.left_panel.width() + self.right_panel.width()), self.height() - self.top_panel.height())
        #change graph_panel view
        self.graph_panel.graphicView.setGeometry(0, 0, self.graph_panel.width(), self.graph_panel.height())

    #handles expanding the right panel
    def expand_right_panel(self):
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
