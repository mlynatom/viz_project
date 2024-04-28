import math
import random
import sys
import numpy as np

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import (QAction, QBrush, QColor, QKeySequence, QPainter,
                           QPen, QSurfaceFormat, QTransform)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import (QApplication, QGraphicsScene, QGraphicsView,
                               QHBoxLayout, QHeaderView, QMainWindow, QMenuBar,
                               QSizePolicy, QWidget)

from src.doc_landscape import VisGraphicsScene, VisGraphicsView
from src.data_utils import DocumentData


class MainWindow(QMainWindow):
    """
    The main window of the application.
    """
    def __init__(self, central_widget: QWidget):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Document Corpus Visualization')

        #window dimensions
        geometry = self.screen().availableGeometry()
        #self.setFixedSize(geometry.width() * 0.8, geometry.height() * 0.7)
        self.setMinimumSize(geometry.width() * 0.5, geometry.height() * 0.4)
      
        #set central widget
        self.setCentralWidget(central_widget)

        #menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        #exit qaction
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)

        #status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Data loaded and plotted")

        
        self.show()

class CentralWidget(QWidget):
    """
    Class for holding the central widget of our application.
    """
    def __init__(self) -> None:
        QWidget.__init__(self)

        #init subwidget
        self.scene = VisGraphicsScene()
        self.brush = [QBrush(Qt.yellow), QBrush(Qt.green), QBrush(Qt.blue), QBrush(Qt.red), QBrush(Qt.cyan), QBrush(Qt.magenta), QBrush(Qt.gray), QBrush(Qt.darkYellow), QBrush(Qt.darkGreen), QBrush(Qt.darkBlue), QBrush(Qt.darkRed), QBrush(Qt.darkCyan)]
        
        format = QSurfaceFormat()
        format.setSamples(4)
        
        gl = QOpenGLWidget()
        gl.setFormat(format)
        gl.setAutoFillBackground(True)
        
        self.view = VisGraphicsView(self.scene, self)
        self.view.setViewport(gl)
        self.view.setBackgroundBrush(QColor(255, 255, 255))

        #TODO load all data
        self.document = DocumentData(data_path="data/bag+of+words", name="kos")
        self.document_coords = self.document.fit_transform("pca")
        self.doc_topic, self.topic = self.document.nmf(n_components=12, num_topic_words=5)

        #add data
        self.generateAndMapData()

        #init subwidget TODO change to table
        self.scene2 = VisGraphicsScene()
        
        format2 = QSurfaceFormat()
        format2.setSamples(4)
        
        gl2 = QOpenGLWidget()
        gl2.setFormat(format2)
        gl2.setAutoFillBackground(True)
        
        self.view2 = VisGraphicsView(self.scene2, self)
        self.view2.setViewport(gl2)
        self.view2.setBackgroundBrush(QColor(255, 255, 255))

        #add data
        #self.generateAndMapData()
        
        #set layout for table right and visualization left
        self.main_layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)


        #left layout
        size.setHorizontalStretch(4)
        self.view.setGeometry(0, 0, 800, 600)
        self.view.setSizePolicy(size)
        self.main_layout.addWidget(self.view)

        #right layout
        size.setHorizontalStretch(1)
        self.view2.setSizePolicy(size)
        self.main_layout.addWidget(self.view2)

        #set the layout to the widget
        self.setLayout(self.main_layout)

    def generateAndMapData(self):
        #Generate random data
        # count = 100
        # x = []
        # y = []
        # r = []
        # c = []
        # for i in range(0, count):
        #     x.append(random.random()*600)
        #     y.append(random.random()*400)
        #     r.append(random.random()*50)
        #     c.append(random.randint(0, 2))

        # #Map data to graphical elements
        # for i in range(0, count):
        #     d = 2*r[i]
        #     ellipse = self.scene.addEllipse(x[i], y[i], d, d, self.scene.pen, self.brush[c[i]])
        
        width = self.scene.width()
        height = self.scene.height()
        print(width)
        print(height)

        #Generate random data
        #remap the result of pca to the screen
        x = self.document_coords[:, 0]
        y = self.document_coords[:, 1]
        x_min = np.min(x)
        x_max = np.max(x)
        y_min = np.min(y)
        y_max = np.max(y)

        x_min_max_scaled = (x - x_min) / (x_max - x_min)
        y_min_max_scaled = (y - y_min) / (y_max - y_min)

        #rescale minmaxed to the screen
        width = 800
        height = 600
        x = x_min_max_scaled * width
        y = y_min_max_scaled * height
        c = self.doc_topic #get colors

        #Map data to graphical elements
        for i in range(0, x.shape[0]):
            d = 3
            ellipse = self.scene.addEllipse(x[i], y[i], d,d, self.scene.pen, self.brush[c[i]])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    central_widget = CentralWidget()
    ex = MainWindow(central_widget=central_widget)
    sys.exit(app.exec())
