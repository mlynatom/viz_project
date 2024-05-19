import math

import numpy as np
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import (QColor, QPainter,
                           QPen, QTransform, QFont)
from PySide6.QtWidgets import (QGraphicsEllipseItem,
                               QGraphicsItem, QGraphicsScene, QGraphicsView,
                               QGraphicsTextItem)


class Compass(QGraphicsEllipseItem, QObject):
    # define signal for position change
    positionChanged = Signal()

    def __init__(self, *args, **kwargs) -> None:
        QGraphicsEllipseItem.__init__(self, *args, **kwargs)
        QObject.__init__(self)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            self.positionChanged.emit()  # emit signal when position changes

        return super().itemChange(change, value)


class DocumentEllipse(QGraphicsEllipseItem):
    def __init__(self, x, y, w, h, brush, id: str) -> None:
        super(DocumentEllipse, self).__init__(x, y, w, h)
        self.pen_unselected = QPen(Qt.black, 0.5)
        self.pen_selected = QPen(Qt.red, 0.5)
        self.setPen(self.pen_unselected)
        self.setBrush(brush)
        self.id = id
        self.selected = False

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
        self.label.setPos(label_x, label_y - label_height / 2)

    def mousePressEvent(self, event):
        self.label_clicked = not self.label_clicked
        if not self.selected:
            self.selectionHandler()
        else:
            self.unselectionHandler()

        super().mousePressEvent(event)

    def hoverEnterEvent(self, event):
        self.label.setVisible(True)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        if not self.label_clicked and not self.compass_over:
            self.label.setVisible(False)
        super().hoverLeaveEvent(event)

    def compassOver(self):
        self.compass_over = True
        self.selectionHandler()

    def compassNotOver(self):
        self.compass_over = False
        self.unselectionHandler()

    def selectionHandler(self):
        self.selected = True
        self.setSelected(True)
        self.setPen(self.pen_selected)
        self.label.setVisible(True)

    def unselectionHandler(self):
        self.selected = False
        self.setSelected(False)
        self.setPen(self.pen_unselected)
        self.label.setVisible(False)


class VisGraphicsScene(QGraphicsScene):
    # define signal for selection change
    selectionChanged = Signal()


    def __init__(self, global_event):
        super(VisGraphicsScene, self).__init__()
        self.global_event = global_event
        self.wasDragg = False
        self.pen_compass = QPen(Qt.black, 2)
        self.compass = None
        self.selected_docs = []  # store selected documents
        self.elipse2id = {}  # store mapping from elipse to document id
        self.ctrl_pressed = False


    def mouseReleaseEvent(self, event):
        if (self.wasDragg):
            return
        # check what was clicked
        item = self.itemAt(event.scenePos(), QTransform())
        self.handle_item_click(item)

    def handle_item_click(self, item):
        if item is self.compass:
            pass
            # print("Compass clicked")
        elif isinstance(item, DocumentEllipse):
            if self.elipse2id.get(item) in self.selected_docs:
                self.selected_docs.remove(self.elipse2id.get(item))
                self.selectionChanged.emit()
            else:
                if not self.global_event.ctrl_pressed:
                    for elipseid in self.selected_docs:
                        self.doc_elipses[elipseid].unselectionHandler()
                    self.selected_docs = [self.elipse2id.get(item)]
                else:
                    self.selected_docs.append(self.elipse2id.get(item))
                item.selectionHandler()
                self.selectionChanged.emit()


    def generateAndMapData(self, document_coords, doc_topic, brush):
        # remap the results to the screen
        x = document_coords[:, 0]
        y = document_coords[:, 1]
        x_min = np.min(x)
        x_max = np.max(x)
        y_min = np.min(y)
        y_max = np.max(y)

        x_min_max_scaled = (x - x_min) / (x_max - x_min)
        y_min_max_scaled = (y - y_min) / (y_max - y_min)

        # rescale minmaxed to the screen TODO better alignment with the space!
        width = 800
        height = 600
        x = x_min_max_scaled * width
        y = y_min_max_scaled * height
        c = doc_topic  # get colors

        # Map data to graphical elements
        self.doc_elipses = []
        for i in range(0, x.shape[0]):
            d = 3
            ellipse = DocumentEllipse(x[i], y[i], d, d, brush[c[i]], str(i))
            # ellipse = self.addEllipse(x[i], y[i], d,d, self.pen_docs, brush[c[i]])
            self.addItem(ellipse)
            self.elipse2id[ellipse] = i
            self.doc_elipses.append(ellipse)

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
                elif not self.global_event.ctrl_pressed:
                    item.compassNotOver()

        if ellipses_inside_area != self.selected_docs:
            if not self.global_event.ctrl_pressed:
                self.selected_docs = ellipses_inside_area
            else:
                for item in ellipses_inside_area:
                    if item not in self.selected_docs:
                        self.selected_docs.append(item)
                        self.doc_elipses[item].selectionHandler()
            self.selectionChanged.emit()


    def init_compass(self, w, h):
        self.compass = Compass(0, 0, 50, 50)
        self.compass.setPos(w / 2, h / 2)
        self.compass.setBrush(QColor(0, 0, 0, 0))
        self.compass.setPen(self.pen_compass)
        self.compass.setFlag(QGraphicsEllipseItem.ItemIsMovable, True)  # set that this item can be moved
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
        zoom = 1 + event.angleDelta().y() * 0.001;
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
        distance = math.sqrt(deltaX * deltaX + deltaY * deltaY)
        if (distance > 5):
            self.myScene.wasDragg = True

        super().mouseReleaseEvent(event)
