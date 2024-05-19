import numpy as np
from PySide6.QtCore import QRectF
from PySide6.QtGui import Qt, QBrush, QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsScene, \
    QGraphicsView, QGraphicsTextItem, QHBoxLayout, QPushButton

from src.data_utils import DocumentData

COLORS = [
    Qt.darkYellow, Qt.green, Qt.blue, Qt.red, Qt.cyan, Qt.magenta,
    Qt.gray, Qt.darkYellow, Qt.darkGreen, Qt.darkBlue, Qt.darkRed, Qt.darkCyan
]


def normalise(array):
    return array / np.max(array)


class WordCloudWindow(QWidget):
    def __init__(self, document_data: DocumentData):
        super().__init__()
        self.document_data = document_data
        self.generated_topic_wordcloud = False

        # Set it as window
        self.setWindowTitle("Wordcloud Window")
        self.setFixedSize(1000, 700)

        # set menu with Buttons
        self.menu = QHBoxLayout()
        self.pushed_styledheet = "background-color: gray; border: none; "
        self.selection_wordcloud_button = QPushButton("Generate wordcloud from selected documents")
        self.selection_wordcloud_button.setStyleSheet(self.pushed_styledheet)
        self.selection_wordcloud_button.clicked.connect(self.generate_selection_wordcloud)
        self.topic_wordcloud_button = QPushButton("Generate wordcloud from topic words")
        self.topic_wordcloud_button.clicked.connect(self.generate_topic_wordcloud)
        # separator = QFrame()
        # separator.setFrameShape(QFrame.VLine)
        # separator.setFrameShadow(QFrame.Sunken)
        # separator.setLineWidth(1)
        # separator.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        # self.menu.addWidget(separator)
        self.menu.addWidget(self.selection_wordcloud_button)
        # self.menu.addWidget(separator)
        self.menu.addWidget(self.topic_wordcloud_button)
        # self.menu.addWidget(separator)

        # Set the wordcloud scene
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(QRectF(0, 0, 800, 600))  # Set the desired width and height
        self.view = QGraphicsView()
        self.view.setBackgroundBrush(QBrush(Qt.white))
        self.view.setGeometry(0, 0, 800, 600)
        self.view.setScene(self.scene)
        self._generate_words_from_g2()

        # Set status bar
        self.status_bar = QHBoxLayout()
        self.status_bar_widget = QWidget()
        self.status_bar_widget.setLayout(self.status_bar)
        self.text1 = ("\tThe Wordcloud was generated from the selected document "
                 "using the g2 algorithm. It compares selected and unselected documents.\n\t\t\t\tThe colors of words "
                 "corresponds with the topic it belongs to the most.")
        self.text2 = (f"\tThe Wordcloud was generated from words describing the prevalent topic among selected document "
                 f"(or the whole corpus). \n\t  Topics where determined by selected {self.document_data.topics_method} algorithm."
                 "The words of different color are stronger connected to different topic.")
        self.label1 = QLabel(self.text1)
        # Set the position and size of the label
        self.label1.setGeometry(25, 25, 150, 40)
        font = QFont("Arial", 10)
        self.label1.setFont(font)
        self.status_bar_widget.setStyleSheet("""
                    QWidget {
                        background-color: #606060; /* Light grey background */
                    }
                    QLabel {
                        color: #f0f0f0; /* Dark grey text color */
                    }
                """)

        self.status_bar.addWidget(self.label1)
        self.status_bar.setAlignment(Qt.AlignCenter)

        # set the layout to the widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.status_bar_widget)
        self.layout.addLayout(self.menu)
        self.layout.addWidget(self.view)
        self.setLayout(self.layout)

    def generate_selection_wordcloud(self):
        if self.generated_topic_wordcloud:
            self.generated_topic_wordcloud = False
            self.selection_wordcloud_button.setStyleSheet(self.pushed_styledheet)
            self.topic_wordcloud_button.setStyleSheet("")
            self.label1.setText(self.text1)
            self._generate_words_from_g2()

    def generate_topic_wordcloud(self):
        if not self.generated_topic_wordcloud:
            self.generated_topic_wordcloud = True
            self.topic_wordcloud_button.setStyleSheet(self.pushed_styledheet)
            self.selection_wordcloud_button.setStyleSheet("")
            self.label1.setText(self.text2)
            self._generate_words_from_topic()

    def _get_text_item(self, idx, font_size):
        text = self.document_data.vocabulary[idx]
        best_topic = self.document_data.get_words_best_topic(idx, self.document_data.topics_all)
        color = self.document_data.brush[best_topic].color()
        # Create a QGraphicsTextItem
        text_item = QGraphicsTextItem(text + " ")
        # Set the font size and type
        font = QFont("Arial", font_size)  # You can choose a different font type
        text_item.setFont(font)

        # Set the color
        text_item.setDefaultTextColor(color)

        return text_item

    def _generate_words_from_g2(self):
        g2 = self.document_data.compute_g2()
        g2 = normalise(g2)
        sorted_words = np.flip(np.argsort(g2))
        self._generate_words(sorted_words, g2)

    def _generate_words_from_topic(self):
        topics_of_documents = self.document_data.doc_topics
        topics = self.document_data.topics
        selected_documents = self.document_data.selected_documents
        if not selected_documents:
            selected_documents = np.arange(self.document_data.n_docs, dtype=int)
        counts = np.bincount(topics_of_documents[selected_documents])
        selected_topic = np.argmax(counts)
        sizes = normalise(topics[selected_topic])
        sorted_words = np.flip(np.argsort(sizes))
        self._generate_words(sorted_words, sizes)

    def _generate_words(self, sorted_words, sizes):
        self.scene.clear()
        max_width = self.scene.width()
        max_height = self.scene.height()
        x = 0
        y = 0
        row_height = None
        for idx in sorted_words:
            # Make it a bit nonlinear, so the small words are still readable
            # There is a lot of cases, where one word outscale the rest
            size = sizes[idx] ** 0.9 * 100
            if size < 10:
                break
            item = self._get_text_item(idx, size)
            # print(x, y, item.boundingRect().width(), item.boundingRect().height(), item.toPlainText())
            if item.boundingRect().width() + x <= max_width:
                if not row_height:  # to have it aligned from the bottom
                    row_height = item.boundingRect().height()
                item.setPos(x, y + (row_height - item.boundingRect().height()) * 0.9)
                x += item.boundingRect().width()
            elif item.boundingRect().height() + row_height + y <= max_height:
                if not row_height:
                    row_height = item.boundingRect().height()
                y += row_height
                row_height = item.boundingRect().height()
                item.setPos(0, y)
                x = item.boundingRect().width()
            else:
                break
            self.scene.addItem(item)
