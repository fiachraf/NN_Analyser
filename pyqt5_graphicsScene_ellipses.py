import math
from PyQt5 import QtCore, QtGui, QtWidgets

def getLights():
    #returns a dict of 10 strings
    return [{"name": str(i)} for i in range(10)]

class CallbackEllipse(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, light, *args, **kwargs):
        super(CallbackEllipse, self).__init__(*args, **kwargs)
        #light property, will be unique number for the light
        self._light = light

    #when clicked performs these actions
    def mouseReleaseEvent(self, event):
        color = QtGui.QColor(QtCore.Qt.lightGray)
        brush = QtGui.QBrush(color)
        self.setBrush(brush)
        print(self._light["name"])
        super(CallbackEllipse, self).mouseReleaseEvent(event)

class MyFrame(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super(MyFrame, self).__init__(parent)

        #setting details for the scene
        self.setScene(QtWidgets.QGraphicsScene(self))
        self.setBackgroundBrush(QtGui.QColor(QtCore.Qt.darkGray))
        self.setRenderHints(self.renderHints() | QtGui.QPainter.Antialiasing  | QtGui.QPainter.SmoothPixmapTransform)

        #dict of 10 strings 0 to 9
        arLights = getLights()


        theta = math.radians(360)

        #filter_lights is the same as arLights, can apply a filter if desired I guess
        filter_lights = list(filter(None, arLights))
        num_of_columns = len(filter_lights)
        #gets angular distance between each ellipse
        delta = theta/num_of_columns
        #intial 0,0 coords
        circX, circY = 0, 0
        #details for ellipse shape
        w, h, x, y = 100, 100, 100, 100

        #sets colours for ellipses
        pen = QtGui.QPen(QtGui.QColor(QtCore.Qt.lightGray).darker(50))
        brush = QtGui.QBrush(QtGui.QColor(QtCore.Qt.lightGray))

        #for each object in the list
        for i, light in enumerate(filter_lights):
            # position in scene
            angle = i*delta
            circX = (w + x) * math.cos(angle)
            circY = (h + y) * math.sin(angle)
            #item is produced on graphics scene and is not kept track of in python list but instead is being stored in some othe array under the hood, however each ellipse is interactable and has its own different properties in this case a different number
            #light is a dict entry
            item = CallbackEllipse(light, circX, circY, w, h)
            item.setAcceptHoverEvents(True)
            item.setPen(pen)
            item.setBrush(brush)
            item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
            #adds the ellipse item to the scene
            self.scene().addItem(item)

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = MyFrame()
    w.show()
    sys.exit(app.exec_())
