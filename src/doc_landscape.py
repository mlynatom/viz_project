import math

import numpy as np
from PySide6.QtCore import QRectF, QSize, Qt, Signal, QObject
from PySide6.QtGui import (QAction, QBrush, QColor, QKeySequence, QPainter,
                           QPen, QSurfaceFormat, QTransform,QFont)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import (QApplication, QGraphicsEllipseItem,
                               QGraphicsItem, QGraphicsScene, QGraphicsView,
                               QHBoxLayout, QHeaderView, QMainWindow, QMenuBar,
                               QSizePolicy, QWidget, QLabel, QGraphicsTextItem)

class Compass(QGraphicsEllipseItem, QObject):
    #define signal for position change
    positionChanged = Signal()

    def __init__(self, *args, **kwargs) -> None:
        QGraphicsEllipseItem.__init__(self, *args, **kwargs)
        QObject.__init__(self)
    
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            self.positionChanged.emit() #emit signal when position changes

        return super().itemChange(change, value)
    
class DocumentEllipse(QGraphicsEllipseItem):
    def __init__(self, x, y, w, h, pen, brush, id:str) -> None:
        super(DocumentEllipse, self).__init__(x,y,w,h)
        self.setPen(pen)
        self.setBrush(brush)
        self.id = id

        # Enable hover events
        self.setAcceptHoverEvents(True)

        self.label_clicked = False
        self.compass_over = False

        self.label = QGraphicsTextItem(id, self)
        font = QFont()
        font.setPointSize(3)  # Set the font size
        self.label.setFont(font)

        self.label.setDefaultTextColor(Qt.black)
        self.label.setVisible(False)
        
        label_height = self.label.boundingRect().height()
        label_x = self.rect().right()
        label_y = self.rect().top()
        self.label.setPos(label_x, label_y - label_height/2)

        

    def mousePressEvent(self, event):
        self.label_clicked = not self.label_clicked
        self.label.setVisible(self.label_clicked)
        super().mousePressEvent(event)

    def hoverEnterEvent(self, event):
        self.label.setVisible(True)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        if not self.label_clicked and not self.compass_over:
            self.label.setVisible(False)
        super().hoverLeaveEvent(event)

    def compassOver(self):
        self.label.setVisible(True)
        self.compass_over = True

    def compassNotOver(self):
        self.compass_over = False
        self.label.setVisible(False)



class VisGraphicsScene(QGraphicsScene):
    #define signal for selection change
    selectionChanged = Signal()

    def __init__(self):
        super(VisGraphicsScene, self).__init__()
        self.selection = None
        self.wasDragg = False
        self.pen_docs = QPen(Qt.black, 0.5)
        self.pen_docs_selected = QPen(Qt.red,0.5)
        self.pen_compass = QPen(Qt.black, 2)
        self.compass = None
        self.selected_docs = [] #store selected documents
        self.elipse2id = {} #store mapping from elipse to document id

    def mouseReleaseEvent(self, event): 
        if(self.wasDragg):
            return
        if(self.selection and self.selection is not self.compass):
            self.selection.setPen(self.pen_docs)

        #check what was clicked
        item = self.itemAt(event.scenePos(), QTransform())
        if item is self.compass:
            pass
            # print("Compass clicked")
        elif isinstance(item, DocumentEllipse):
            item.setPen(self.pen_docs_selected)
            self.selection = item
        else:
            pass
            

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
            ellipse = DocumentEllipse(x[i], y[i], d,d, self.pen_docs, brush[c[i]], str(i))
            # ellipse = self.addEllipse(x[i], y[i], d,d, self.pen_docs, brush[c[i]])
            self.addItem(ellipse)
            self.elipse2id[ellipse] = i

        #TODO add the compass (ellipse with transparent background)
        self.init_compass(width, height)

    def get_ellipses_ids_inside_compass(self):
        # print("Compass moved", self.compass.scenePos())
        ellipses_inside_area = []
        target_rect = self.compass.sceneBoundingRect()

        for item in self.items():
            if isinstance(item, QGraphicsEllipseItem) and item != self.compass:
                item_rect = item.sceneBoundingRect()
                if target_rect.contains(item_rect):
                    item.compassOver()
                    ellipses_inside_area.append(self.elipse2id[item])
                else:
                    item.compassNotOver()

        if ellipses_inside_area != self.selected_docs:
            self.selected_docs = ellipses_inside_area
            self.selectionChanged.emit()

            
        


    def init_compass(self, w, h):
        self.compass = Compass(0,0,50,50)
        self.compass.setPos(w/2, h/2)
        self.compass.setBrush(QColor(0, 0, 0, 0))
        self.compass.setPen(self.pen_compass)
        self.compass.setFlag(QGraphicsEllipseItem.ItemIsMovable, True) #set that this item can be moved
        self.compass.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges, True)
        self.compass.positionChanged.connect(self.get_ellipses_ids_inside_compass)
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
        # print("Mouse press event", self.startX, self.startY)

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