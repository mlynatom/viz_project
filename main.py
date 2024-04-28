import math
import random
import sys
import numpy as np
from typing import Union, Literal

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import (QAction, QBrush, QColor, QKeySequence, QPainter,
                           QPen, QSurfaceFormat, QTransform)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import (QApplication, QGraphicsScene, QGraphicsView,
                               QHBoxLayout, QHeaderView, QMainWindow, QMenuBar,
                               QSizePolicy, QWidget,QComboBox)

from src.doc_landscape import VisGraphicsScene, VisGraphicsView
from src.data_utils import DocumentData

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


    def reload_data(self, name:str ="kos", dimred:Union[Literal["pca"], Literal["umap"], Literal["tsne"]]="pca"):
        #TODO load all data
        self.scene.clear()
        self.document = DocumentData(data_path="data/bag+of+words", name=name)
        self.document_coords = self.document.fit_transform(dimred)
        self.doc_topic, self.topic = self.document.nmf(n_components=12, num_topic_words=5)

        #add data
        self.generateAndMapData()

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

        #rescale minmaxed to the screen TODO better alignment with the space!
        width = 800
        height = 600
        x = x_min_max_scaled * width
        y = y_min_max_scaled * height
        c = self.doc_topic #get colors

        #Map data to graphical elements
        for i in range(0, x.shape[0]):
            d = 3
            ellipse = self.scene.addEllipse(x[i], y[i], d,d, self.scene.pen, self.brush[c[i]])


class MainWindow(QMainWindow):
    """
    The main window of the application.
    """
    def __init__(self, central_widget: CentralWidget):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Document Corpus Visualization')

        #window dimensions
        geometry = self.screen().availableGeometry()
        #self.setFixedSize(geometry.width() * 0.8, geometry.height() * 0.7)
        self.setMinimumSize(geometry.width() * 0.5, geometry.height() * 0.4)
      
        #set central widget
        self.central_widget = central_widget
        self.setCentralWidget(self.central_widget)

        #status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready, to load a file go to File -> Open -> Kos/Nips/Enron/Nytimes/Pubmed", timeout=500000)

        #menu
        self.init_menu()
        
        #toolbar
        self.init_toolbar()

        #load default file
        self.loaded_file = None #to remember which file was las loaded
        self.open_file_action("kos")

        self.show()

    def open_file_action(self, name:str):
        self.loaded_file = name
        self.status_bar.showMessage(f"Loading data {name}")
        self.central_widget.reload_data(name, dimred=self.dimred_literals[self.dimred_combo.currentIndex()])
        self.status_bar.showMessage(f"Data {name} loaded and plotted")

    def dimred_combo_action(self, index:int):
        dimred = self.dimred_literals[index]
        self.central_widget.reload_data(self.loaded_file, dimred)
        self.status_bar.showMessage(f"Data {self.loaded_file} loaded and plotted with {dimred}")

    def init_menu(self):
        #menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        #open menu
        self.file_menu_open = self.file_menu.addMenu("Load Dataset")
        #add alternatives to the menu to let user choose one from kos, nips, enron
        self.file_menu_open_kos = self.file_menu_open.addAction("KOS")
        self.file_menu_open_nips = self.file_menu_open.addAction("NIPS")
        self.file_menu_open_enron = self.file_menu_open.addAction("Enron")
        self.file_menu_open_nytimes = self.file_menu_open.addAction("NYTimes")
        self.file_menu_open_pubmed = self.file_menu_open.addAction("PubMed")
        #connect the actions for kos and nips
        self.file_menu_open_kos.triggered.connect(lambda: self.open_file_action("kos"))
        self.file_menu_open_nips.triggered.connect(lambda: self.open_file_action("nips"))
        #TODO connect the actions for enron, nytimes, pubmed

        #exit action
        self.file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)

    def init_toolbar(self):
        self.toolbar = self.addToolBar("Toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setAllowedAreas(Qt.ToolBarArea.TopToolBarArea)
        self.dimred_combo = QComboBox()
        self.dimred_combo.addItems(["PCA", "UMAP", "t-SNE"])
        self.dimred_combo.setAccessibleName("Dimensionality Reduction")
        self.dimred_literals = ["pca", "umap", "tsne"]
        self.dimred_combo.currentIndexChanged.connect(self.dimred_combo_action)
        self.dimred_action = self.toolbar.addWidget(self.dimred_combo)
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    central_widget = CentralWidget()
    ex = MainWindow(central_widget=central_widget)
    sys.exit(app.exec())
