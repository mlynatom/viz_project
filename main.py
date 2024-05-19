import sys
from typing import Literal, Union

from PySide6.QtCore import Qt, QObject, QEvent
from PySide6.QtGui import (QAction, QBrush, QColor, QKeySequence, QSurfaceFormat, QKeyEvent)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QHeaderView, QLabel,
                               QMainWindow, QSizePolicy, QSpinBox,
                               QWidget, QTableWidget, QTableWidgetItem)

from src.data_utils import DocumentData
from src.doc_landscape import VisGraphicsScene, VisGraphicsView
from src.doc_table import TableView


class GlobalEventFilter(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ctrl_pressed = False

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress or event.type() == QEvent.Type.KeyRelease:
            if isinstance(event, QKeyEvent):
                if event.key() == Qt.Key.Key_Control:
                    if event.type() == QEvent.Type.KeyPress:
                        self.ctrl_pressed = True
                    elif event.type() == QEvent.Type.KeyRelease:
                        self.ctrl_pressed = False
        return super().eventFilter(obj, event)




class CentralWidget(QWidget):
    """
    Class for holding the central widget of our application.
    """

    def __init__(self, global_event_filter) -> None:
        QWidget.__init__(self)
        # init subwidget - scene
        self.scene = VisGraphicsScene(global_event_filter)
        self.scene.selectionChanged.connect(self.generateTable)  # connect selection change to table update

        self.brush = [QBrush(Qt.darkMagenta), QBrush(Qt.green), QBrush(Qt.blue), QBrush(Qt.red), QBrush(Qt.cyan),
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

        # init subwidget - table
        self.table_view = TableView()
        self.table = self.table_view.table
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.itemClicked.connect(self.on_table_item_clicked)

        # set layout for table right and visualization left
        self.main_layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        # left layout
        size.setHorizontalStretch(4)
        self.view.setGeometry(0, 0, 800, 600)
        self.view.setSizePolicy(size)
        self.main_layout.addWidget(self.view)

        # right layout
        size.setHorizontalStretch(1)
        self.table.setSizePolicy(size)
        self.main_layout.addWidget(self.table_view)

        # set the layout to the widget
        self.setLayout(self.main_layout)

    def reload_data(self, name: str = "kos",
                    dimred_solver: Union[Literal["pca"], Literal["umap"], Literal["tsne"]] = "tsne",
                    topic_solver: Union[Literal["nmf"], Literal["lda"]] = "nmf", n_components: int = 10,
                    num_topic_words: int = 5):
        # load all data
        self.document = DocumentData(data_path="data/bag+of+words", name=name)
        self.document.brush = self.brush
        self.table_view.document_data = self.document
        self.document_coords = self.document.fit_transform(dimred_solver)
        self.doc_topic, self.topics_all = self.document.fit_topics(solver=topic_solver, n_components=n_components)
        # self.topics = self.document.get_topics_words(self.topics_all)
        # self.document.topic_words = self.topics
        self.document.doc_topic = self.doc_topic
        self.document.topics_all = self.topics_all
        # add data
        self.reload_scene()

    def reload_topics(self, topic_solver: Union[Literal["nmf"], Literal["lda"]] = 'nmf', n_components: int = 10,
                         num_topic_words: int = 5):
        self.doc_topic, self.topics_all = self.document.fit_topics(topic_solver, n_components=n_components)
        # self.topics = self.document.get_topics_words(self.topics_all)
        # self.document.topic_words = self.topics
        self.document.doc_topic = self.doc_topic
        self.document.topics_all = self.topics_all
        self.reload_scene()

    def reload_scene(self):
        self.scene.clear()
        self.scene.wasDragg = False
        self.scene.generateAndMapData(self.document_coords, self.doc_topic, self.brush)

    def reload_num_topic_words(self, num_topic_words: int = 5):
        pass
        # self.topics = self.document.get_topics_words(self.topics_all, n=num_topic_words)
        # self.document.topic_words = self.topics

    def generateTable(self):
        self.table.clear()
        self.table.setRowCount(self.doc_topic.shape[0])
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Doc ID", "Topic ID", "Topic Colour"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)

        # obtain selected documents from the scene + sort them
        selected_docs = sorted(self.scene.selected_docs, reverse=True)
        self.document.selected_documents = selected_docs

        # global idx
        idx = 0
        # first add the selected documents
        for doc_id in selected_docs:
            # self.table.insertRow(0) #insert at the beginning
            item_id = QTableWidgetItem(str(doc_id))
            item_topic_id = QTableWidgetItem(str(self.doc_topic[doc_id]))
            item_topic_colour = QTableWidgetItem()
            item_topic_colour.setBackground(self.brush[self.doc_topic[doc_id]])
            self.table.setItem(idx, 0, item_id)
            self.table.setItem(idx, 1, item_topic_id)
            self.table.setItem(idx, 2, item_topic_colour)
            # TODO link cell double_clicked to the wordclouds
            idx += 1

        # then add the rest of the documents
        for i, topic in enumerate(self.doc_topic):
            if i in selected_docs:
                continue
            item_id = QTableWidgetItem(str(i))
            item_topic_id = QTableWidgetItem(str(topic))
            item_topic_colour = QTableWidgetItem()
            item_topic_colour.setBackground(self.brush[topic])
            self.table.setItem(idx, 0, item_id)
            self.table.setItem(idx, 1, item_topic_id)
            self.table.setItem(idx, 2, item_topic_colour)
            # TODO link cell double_clicked to the wordclouds
            idx += 1

        # highlight the selected rows
        for col in range(0, 2):
            for row in range(len(selected_docs)):
                self.table.item(row, col).setSelected(True)

        # TODO sorting by compass
        # self.table.sortByColumn(1, Qt.SortOrder.AscendingOrder)

        self.table.resizeColumnsToContents()

    def on_table_item_clicked(self, item):
        # Get the row and column of the clicked item
        row = item.row()
        first_column_item = self.table.item(row, 0)
        doc_idx = int(first_column_item.text())
        self.scene.handle_item_click(self.scene.doc_elipses[doc_idx])


class LabeledWidget(QWidget):
    def __init__(self, label_text, widget):
        super().__init__()
        layout = QHBoxLayout()
        self.label = QLabel(label_text)
        self.widget = widget
        layout.addWidget(self.label)
        layout.addWidget(self.widget)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    """
    The main window of the application.
    """

    def __init__(self, central_widget: CentralWidget):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Document Corpus Visualization')

        # window dimensions
        geometry = self.screen().availableGeometry()
        # self.setFixedSize(geometry.width() * 0.8, geometry.height() * 0.7)
        self.setMinimumSize(geometry.width() * 0.5, geometry.height() * 0.4)

        # set central widget
        self.central_widget = central_widget
        self.setCentralWidget(self.central_widget)

        # status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready, to load a file go to File -> Open -> Kos/Nips/Enron/Nytimes/Pubmed",
                                    timeout=500000)

        # menu
        self.init_menu()

        # toolbar
        self.init_toolbar()

        # load default file
        self.loaded_file = None  # to remember which file was las loaded
        self.open_file_action("kos")

        self.show()

    def open_file_action(self, name: str):
        self.loaded_file = name
        self.status_bar.showMessage(f"Loading data {name}")
        # self.central_widget.reload_data(name, dimred_solver=self.dimred_literals[self.dimred_combo.currentIndex()],
        #                                 topic_solver=self.topic_literals[self.topic_combo.currentIndex()],
        #                                 n_components=self.num_topics_spinbox.value(), num_topic_words=self.num_topic_words_spinbox.value())
        self.central_widget.reload_data(name, dimred_solver=self.dimred_literals[self.dimred_combo.currentIndex()],
                                        topic_solver=self.topic_literals[self.topic_combo.currentIndex()],
                                        n_components=self.num_topics_spinbox.value(), num_topic_words=0)
        self.central_widget.generateTable()
        self.status_bar.showMessage(f"Data {name} loaded and plotted")
        self.setWindowTitle(f'Document Corpus Visualization - dataset: {name}')

    def dimred_combo_action(self, index: int):
        dimred = self.dimred_literals[index]
        self.central_widget.reload_data(self.loaded_file, dimred,
                                        topic_solver=self.topic_literals[self.topic_combo.currentIndex()],
                                        n_components=self.num_topics_spinbox.value())
        self.status_bar.showMessage(f"Data {self.loaded_file} loaded and plotted with {dimred}")

    def topic_combo_action(self, index: int):
        topic_solver = self.topic_literals[index]
        self.central_widget.reload_topics(topic_solver=topic_solver, n_components=self.num_topics_spinbox.value())
                                          #num_topic_words=self.num_topic_words_spinbox.value())
        self.central_widget.generateTable()
        self.status_bar.showMessage(f"Topics computed with {topic_solver}")

    def topic_num_topics_action(self, value: int):
        # self.central_widget.reload_topics(topic_solver=self.topic_literals[self.topic_combo.currentIndex()],
        #                                   n_components=value, num_topic_words=self.num_topic_words_spinbox.value())
        self.central_widget.reload_topics(topic_solver=self.topic_literals[self.topic_combo.currentIndex()],
                                          n_components=value)
        self.central_widget.generateTable()
        self.status_bar.showMessage(f"Topics computed for {value} topics")

    # def topic_num_topic_words_action(self, value:int):
    #     self.central_widget.reload_num_topic_words(num_topic_words=value)
    #     self.status_bar.showMessage(f"Topic words recomputed for {value} topic words")

    def init_menu(self):
        # menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        # open menu
        self.file_menu_open = self.file_menu.addMenu("Load Dataset")
        # add alternatives to the menu to let user choose one from kos, nips, enron
        self.file_menu_open_kos = self.file_menu_open.addAction("KOS")
        self.file_menu_open_nips = self.file_menu_open.addAction("NIPS")
        # self.file_menu_open_enron = self.file_menu_open.addAction("Enron")
        # self.file_menu_open_nytimes = self.file_menu_open.addAction("NYTimes")
        # self.file_menu_open_pubmed = self.file_menu_open.addAction("PubMed")
        # connect the actions for kos and nips
        self.file_menu_open_kos.triggered.connect(lambda: self.open_file_action("kos"))
        self.file_menu_open_nips.triggered.connect(lambda: self.open_file_action("nips"))
        # self.file_menu_open_enron.triggered.connect(lambda: self.open_file_action("enron"))
        # self.file_menu_open_nytimes.triggered.connect(lambda: self.open_file_action("nytimes"))
        # self.file_menu_open_pubmed.triggered.connect(lambda: self.open_file_action("pubmed"))

        # exit action
        self.file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)

    def init_toolbar(self):
        self.toolbar = self.addToolBar("Toolbar")
        # self.toolbar.setMovable(False)
        # self.toolbar.setAllowedAreas(Qt.ToolBarArea.TopToolBarArea)

        # dimred combobox
        self.dimred_combo_label_widget = LabeledWidget("Dimensionality Reduction", QComboBox())
        self.dimred_combo = self.dimred_combo_label_widget.widget
        self.dimred_combo.addItems(["t-SNE", "UMAP", "PCA"])
        self.dimred_combo.setAccessibleName("Dimensionality Reduction")
        self.dimred_literals = ["tsne", "umap", "pca"]
        self.dimred_combo.currentIndexChanged.connect(self.dimred_combo_action)
        self.toolbar.addWidget(self.dimred_combo_label_widget)

        # topic solver combobox
        self.topic_combo_label_widget = LabeledWidget("Topic Solver", QComboBox())
        self.topic_combo = self.topic_combo_label_widget.widget
        self.topic_combo.addItems(["LDA", "NMF"])
        self.topic_combo.setAccessibleName("Topic Solver")
        self.topic_literals = ["lda", "nmf"]
        self.topic_combo.currentIndexChanged.connect(self.topic_combo_action)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.topic_combo_label_widget)

        # spinbox for number of topics
        self.num_topics_spinbox_label = LabeledWidget("Number of Topics", QSpinBox())
        self.num_topics_spinbox = self.num_topics_spinbox_label.widget
        self.num_topics_spinbox.setAccessibleName("Number of Topics")
        self.num_topics_spinbox.setMinimum(1)
        self.num_topics_spinbox.setMaximum(12)
        self.num_topics_spinbox.setValue(8)
        self.num_topics_spinbox.valueChanged.connect(self.topic_num_topics_action)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.num_topics_spinbox_label)

        # #spinbox for number of topic words
        # self.num_topic_words_spinbox_label = LabeledWidget("Number of Topic Words", QSpinBox())
        # self.num_topic_words_spinbox = self.num_topic_words_spinbox_label.widget
        # self.num_topic_words_spinbox.setAccessibleName("Number of Topic Words")
        # self.num_topic_words_spinbox.setMinimum(1)
        # self.num_topic_words_spinbox.setMaximum(10)
        # self.num_topic_words_spinbox.setValue(5)
        # self.num_topic_words_spinbox.valueChanged.connect(self.topic_num_topic_words_action)
        # self.toolbar.addSeparator()
        # self.toolbar.addWidget(self.num_topic_words_spinbox_label)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    global_event_filter = GlobalEventFilter()
    app.installEventFilter(global_event_filter)

    central_widget = CentralWidget(global_event_filter)
    ex = MainWindow(central_widget=central_widget)
    sys.exit(app.exec())
