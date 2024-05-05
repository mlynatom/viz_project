import math
from pkgutil import iter_modules
import random
import sys
import numpy as np

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import (QAction, QBrush, QColor, QKeySequence, QPainter,
                           QPen, QSurfaceFormat, QTransform)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import (QApplication, QGraphicsScene, QGraphicsView,
                               QHBoxLayout, QHeaderView, QMainWindow, QMenuBar,
                               QSizePolicy, QWidget, QGraphicsEllipseItem, QGraphicsItem)
from PySide6.QtCore import Qt, QRectF, Signal
    
class VisGraphicsScene(QGraphicsScene):
    def __init__(self):
        super(VisGraphicsScene, self).__init__()
        self.selection = None
        self.wasDragg = False
        self.pen_docs = QPen(Qt.black, 0.5)
        self.pen_docs_selected = QPen(Qt.red,0.5)
        self.pen_compass = QPen(Qt.black, 2)
        self.compass = None
        self.selected_docs = [] #TODO store selected documents
        self.doc_elipses = [] #store elipses of documents

    def mouseReleaseEvent(self, event): 
        if(self.wasDragg):
            return
        if(self.selection and self.selection is not self.compass):
            self.selection.setPen(self.pen_docs)

        #check what was clicked
        item = self.itemAt(event.scenePos(), QTransform())
        if item is self.compass:
            print("Compass clicked")
        elif(item):
            item.setPen(self.pen_docs_selected)
            self.selection = item

    def generateAndMapData(self, document_coords, doc_topic, brush):
        #remap the results to the screen
        x = document_coords[:, 0]
        y = document_coords[:, 1]
        x_min = np.min(x)
        x_max = np.max(x)
        y_min = np.min(y)
        y_max = np.max(y)

        x_min_max_scaled = (x - x_min) / (x_max - x_min)
        y_min_max_scaled = (y - y_min) / (y_max - y_min)

        #rescale minmaxed to the screen TODO better alignment with the space!
        width = 800
        height = 600
        x = x_min_max_scaled * width
        y = y_min_max_scaled * height
        c = doc_topic #get colors

        #Map data to graphical elements
        self.doc_elipses = []
        for i in range(0, x.shape[0]):
            d = 3
            ellipse = self.addEllipse(x[i], y[i], d,d, self.pen_docs, brush[c[i]])
            self.doc_elipses.append(ellipse)

        #TODO add the compass (ellipse with transparent background)
        self.init_compass(width, height)

    def get_ellipses_inside_compass(self):
        #TODO not working?
        ellipses_inside_area = []
        target_rect = self.compass.boundingRect()

        for item in self.items():
            if isinstance(item, QGraphicsEllipseItem) and item != self.compass:
                item_rect = item.boundingRect()
                if target_rect.contains(item_rect):
                    ellipses_inside_area.append(item)

        return ellipses_inside_area


    def init_compass(self, w, h):
        self.compass = QGraphicsEllipseItem(w/2,h/2,50,50)
        self.compass.setBrush(QColor(0, 0, 0, 0))
        self.compass.setPen(self.pen_compass)
        self.compass.setFlag(QGraphicsEllipseItem.ItemIsMovable, True) #set that this item can be moved
        self.compass.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges, True)
        self.addItem(self.compass)
            


class VisGraphicsView(QGraphicsView):
    def __init__(self, scene, parent):
        super(VisGraphicsView, self).__init__(scene, parent)
        self.startX = 0.0
        self.startY = 0.0
        self.distance = 0.0
        self.myScene = scene
        self.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

    def wheelEvent(self, event):
        zoom = 1 + event.angleDelta().y()*0.001;
        self.scale(zoom, zoom)
        
    def mousePressEvent(self, event):
        self.startX = event.position().x()
        self.startY = event.position().y()
        self.myScene.wasDragg = False

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        endX = event.position().x()
        endY = event.position().y()
        deltaX = endX - self.startX
        deltaY = endY - self.startY
        distance = math.sqrt(deltaX*deltaX + deltaY*deltaY)
        if(distance > 5):
            self.myScene.wasDragg = True

        super().mouseReleaseEvent(event)