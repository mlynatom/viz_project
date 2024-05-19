import sys

from PySide6.QtCore import Signal
from PySide6.QtGui import QPen, Qt, QTransform, QBrush, QSurfaceFormat, QColor
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QGraphicsScene, \
    QGraphicsEllipseItem, QTextEdit, QGraphicsView
from src.doc_landscape import VisGraphicsView

class WorldcloudScene(QGraphicsScene):
    #define signal for selection change
    selectionChanged = Signal()

    def __init__(self):
        super(WorldcloudScene, self).__init__()
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
        elif(item):
            item.setPen(self.pen_docs_selected)
            self.selection = item

    # def generateAndMapData(self, document_coords, doc_topic, brush):
    #     #remap the results to the screen
    #     x = document_coords[:, 0]
    #     y = document_coords[:, 1]
    #     x_min = np.min(x)
    #     x_max = np.max(x)
    #     y_min = np.min(y)
    #     y_max = np.max(y)
    #
    #     x_min_max_scaled = (x - x_min) / (x_max - x_min)
    #     y_min_max_scaled = (y - y_min) / (y_max - y_min)
    #
    #     #rescale minmaxed to the screen TODO better alignment with the space!
    #     width = 800
    #     height = 600
    #     x = x_min_max_scaled * width
    #     y = y_min_max_scaled * height
    #     c = doc_topic #get colors
    #
    #     #Map data to graphical elements
    #     self.doc_elipses = []
    #     for i in range(0, x.shape[0]):
    #         d = 3
    #         ellipse = self.addEllipse(x[i], y[i], d,d, self.pen_docs, brush[c[i]])
    #         self.elipse2id[ellipse] = i
    #
    #     #TODO add the compass (ellipse with transparent background)
    #     self.init_compass(width, height)

    def get_ellipses_ids_inside_compass(self):
        print("Compass moved", self.compass.scenePos())
        ellipses_inside_area = []
        target_rect = self.compass.sceneBoundingRect()

        for item in self.items():
            if isinstance(item, QGraphicsEllipseItem) and item != self.compass:
                item_rect = item.sceneBoundingRect()
                if target_rect.contains(item_rect):
                    ellipses_inside_area.append(self.elipse2id[item])

        if ellipses_inside_area != self.selected_docs:
            self.selected_docs = ellipses_inside_area
            self.selectionChanged.emit()

class WordCloudWindow(QWidget):
    def __init__(self):
        super().__init__()

        #Set it as window
        self.setWindowTitle("Wordcloud Window")

        geometry = self.screen().availableGeometry()
        # self.setFixedSize(geometry.width() * 0.8, geometry.height() * 0.7)
        self.setMinimumSize(geometry.width() * 0.5*0.7, geometry.height() * 0.4*0.7)


        # set widget
        self.scene = WorldcloudScene()
        #self.scene.selectionChanged.connect(self.generateTable)  # connect selection change to table update
        self.brush = [QBrush(Qt.yellow), QBrush(Qt.green), QBrush(Qt.blue), QBrush(Qt.red), QBrush(Qt.cyan),
                      QBrush(Qt.magenta), QBrush(Qt.gray), QBrush(Qt.darkYellow), QBrush(Qt.darkGreen),
                      QBrush(Qt.darkBlue), QBrush(Qt.darkRed), QBrush(Qt.darkCyan)]

        format = QSurfaceFormat()
        format.setSamples(4)

        gl = QOpenGLWidget()
        gl.setFormat(format)
        gl.setAutoFillBackground(True)

        self.view = VisGraphicsView(self.scene, self)
        self.view.setViewport(gl)
        self.view.setBackgroundBrush(QColor(255, 255, 255))


        self.layout = QVBoxLayout()

        # left layout
        self.view.setGeometry(0, 0, 800*2, 600*2)
        self.layout.addWidget(self.view)


        # set the layout to the widget
        #self.setLayout(self.layout)

        #self.layout.addWidget(QPushButton("Close", clicked=self.close))
        # Create a QLabel widget
        label1 = QLabel('Worlcloud generated from selected documents!', self)

        # Set the position and size of the label
        label1.setGeometry(50, 50, 200, 50)
        self.layout.addWidget(label1)


        #self.setLayout(self.layout)


        """
        text field
        
        # Create a QVBoxLayout instance
        layout = QVBoxLayout()

        # Create a QTextEdit widget
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText('This text scales with the window size.')

        # Add the QTextEdit to the layout
        layout.addWidget(self.text_edit)

        # Set the layout for the central widget
        self.setLayout(layout)
        """



        # Create a QVBoxLayout instance
        layout = QVBoxLayout()

        # Create a QGraphicsView widget
        self.graphics_view = QGraphicsView()

        # Create a QGraphicsScene and set it to the QGraphicsView
        self.scene = QGraphicsScene()
        self.graphics_view.setScene(self.scene)

        # Add some items to the scene (optional)
        self.scene.addText("Hello, QGraphicsView!")

        # Add the QGraphicsView to the layout
        layout.addWidget(self.graphics_view)

        # Set the layout for the central widget
        self.setLayout(layout)


