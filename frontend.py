import sys, random, math
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QSizePolicy, QMenuBar, QWidget, QHBoxLayout, QHeaderView
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QBrush, QPen, QTransform, QPainter, QSurfaceFormat, QColor, QKeySequence, QAction

class VisGraphicsScene(QGraphicsScene):
    def __init__(self):
        super(VisGraphicsScene, self).__init__()
        self.selection = None
        self.wasDragg = False
        self.pen = QPen(Qt.black)
        self.selected = QPen(Qt.red)

    def mouseReleaseEvent(self, event): 
        if(self.wasDragg):
            return
        if(self.selection):
            self.selection.setPen(self.pen)
        item = self.itemAt(event.scenePos(), QTransform())
        if(item):
            item.setPen(self.selected)
            self.selection = item


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

class MainWindow(QMainWindow):
    def __init__(self, central_widget: QWidget):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Document Corpus Visualization')
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

        #window dimensions
        geometry = self.screen().availableGeometry()
        #self.setFixedSize(geometry.width() *0.8, geometry.height() * 0.7)
        self.setMinimumSize(geometry.width() *0.5, geometry.height() * 0.4)
      
        self.show()

class CentralWidget(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)

        #init subwidget
        self.scene = VisGraphicsScene()
        self.brush = [QBrush(Qt.yellow), QBrush(Qt.green), QBrush(Qt.blue)]
        
        format = QSurfaceFormat()
        format.setSamples(4)
        
        gl = QOpenGLWidget()
        gl.setFormat(format)
        gl.setAutoFillBackground(True)
        
        self.view = VisGraphicsView(self.scene, self)
        self.view.setViewport(gl)
        self.view.setBackgroundBrush(QColor(255, 255, 255))

        #add data
        self.generateAndMapData()

        #init subwidget
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
        self.generateAndMapData()
        

        
        #set layout for table right and visualization left
        self.main_layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)


        #left layout
        size.setHorizontalStretch(4)
        #self.view.setGeometry(0, 0, 800, 600)
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
        count = 100
        x = []
        y = []
        r = []
        c = []
        for i in range(0, count):
            x.append(random.random()*600)
            y.append(random.random()*400)
            r.append(random.random()*50)
            c.append(random.randint(0, 2))

        #Map data to graphical elements
        for i in range(0, count):
            d = 2*r[i]
            ellipse = self.scene.addEllipse(x[i], y[i], d, d, self.scene.pen, self.brush[c[i]])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    central_widget = CentralWidget()
    ex = MainWindow(central_widget=central_widget)
    sys.exit(app.exec())
