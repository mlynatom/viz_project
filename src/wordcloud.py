import random

import numpy as np
from PySide6.QtCore import QRectF
from PySide6.QtGui import Qt, QBrush, QSurfaceFormat, QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsScene, \
    QGraphicsView, QGraphicsTextItem

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

        # Set it as window
        self.document_data = document_data
        self.setWindowTitle("Wordcloud Window")

        self.setFixedSize(900, 700)

        # set widget
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(QRectF(0, 0, 800, 600))  # Set the desired width and height
        self.view = QGraphicsView()
        self.view.setGeometry(0, 0, 800, 600)
        self.view.setScene(self.scene)
        # self.scene.selectionChanged.connect(self.generateTable)  # connect selection change to table update

        format = QSurfaceFormat()
        format.setSamples(4)

        self.view.setBackgroundBrush(QBrush(Qt.white))

        self.layout = QVBoxLayout()

        self.layout.addWidget(self.view)

        # set the layout to the widget
        self.setLayout(self.layout)

        # self.layout.addWidget(QPushButton("Close", clicked=self.close))
        # Create a QLabel widget
        label1 = QLabel('Worlcloud generated from selected documents!', self)

        # Set the position and size of the label
        label1.setGeometry(50, 50, 200, 50)
        self.layout.addWidget(label1)

        self._generate_words_from_g2()

        # print(document_data.selected_documents)
        # print()
        # print(document_data.compute_g2())

    def _generate_words_from_g2(self):
        g2 = self.document_data.compute_g2()
        g2 = normalise(g2)
        sorted_words = np.flip(np.argsort(g2))
        max_width = self.scene.width()
        max_height = self.scene.height()
        x = 0
        y = 0
        row_height = None
        for idx in sorted_words:
            size = g2[idx] * 100
            if size < 5:
                break
            item = self._get_text_item(idx, size)
            #print(x, y, item.boundingRect().width(), item.boundingRect().height(), item.toPlainText())
            if item.boundingRect().width() + x <= max_width:
                if row_height:  # to have it aligned from the bottom
                    item.setPos(x, y + (row_height - item.boundingRect().height()))
                else:
                    row_height = item.boundingRect().height()
                    item.setPos(x, y)
                x += item.boundingRect().width()
            elif item.boundingRect().height() + row_height + y <= max_height:
                y += row_height
                row_height = item.boundingRect().height()
                item.setPos(0, y)
                x = item.boundingRect().width()
            else:
                break
            self.scene.addItem(item)

    def _get_text_item(self, idx, font_size):
        text = self.document_data.vocabulary[idx]
        color = random.choice(COLORS)
        # Create a QGraphicsTextItem
        text_item = QGraphicsTextItem(text + " ")
        # Set the font size and type
        font = QFont("Arial", font_size)  # You can choose a different font type
        text_item.setFont(font)

        # Set the color
        text_item.setDefaultTextColor(color)

        return text_item
