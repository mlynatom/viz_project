import sys

from PySide6.QtCore import Signal, QRectF
from PySide6.QtGui import QPen, Qt, QTransform, QBrush, QSurfaceFormat, QColor
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QGraphicsScene, \
    QGraphicsEllipseItem, QTextEdit, QGraphicsView, QGraphicsTextItem
from src.doc_landscape import VisGraphicsView

class WordCloudWindow(QWidget):
    def __init__(self):
        super().__init__()

        #Set it as window
        self.setWindowTitle("Wordcloud Window")

        self.setFixedSize(900, 700)

        # set widget
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(QRectF(0, 0, 800, 600))  # Set the desired width and height
        self.view = QGraphicsView()
        self.view.setGeometry(0, 0, 800, 600)
        self.view.setScene(self.scene)
        #self.scene.selectionChanged.connect(self.generateTable)  # connect selection change to table update
        self.brush = [QBrush(Qt.yellow), QBrush(Qt.green), QBrush(Qt.blue), QBrush(Qt.red), QBrush(Qt.cyan),
                      QBrush(Qt.magenta), QBrush(Qt.gray), QBrush(Qt.darkYellow), QBrush(Qt.darkGreen),
                      QBrush(Qt.darkBlue), QBrush(Qt.darkRed), QBrush(Qt.darkCyan)]

        format = QSurfaceFormat()
        format.setSamples(4)

        self.view.setBackgroundBrush(QBrush(Qt.white))


        self.layout = QVBoxLayout()

        self.layout.addWidget(self.view)


        # set the layout to the widget
        self.setLayout(self.layout)

        #self.layout.addWidget(QPushButton("Close", clicked=self.close))
        # Create a QLabel widget
        label1 = QLabel('Worlcloud generated from selected documents!', self)

        # Set the position and size of the label
        label1.setGeometry(50, 50, 200, 50)
        self.layout.addWidget(label1)

        word = QGraphicsTextItem()
        word.setPlainText("Gate")
        word.setDefaultTextColor(Qt.magenta)
        word.setPos(0,0)
        self.scene.addItem(word)







