from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QPushButton, QSizePolicy, QTableWidget,
                               QVBoxLayout, QWidget)

from src.wordcloud import WordCloudWindow


class TableView(QWidget):
    def __init__(self):
        super(TableView, self).__init__()

        #table init
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        #button init
        self.button1 = QPushButton("Generate Wordcloud")
        self.button1.clicked.connect(self.open_selection_wordcloud) #on init open window

        # self.button2 = QPushButton("Prevailing topic wordcloud")
        # self.button2.clicked.connect(self.open_topic_wordcloud)  # on init open window

        self.main_layout = QVBoxLayout()
        size = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        #upper part
        self.main_layout.addWidget(self.button1, alignment=Qt.AlignmentFlag.AlignTop)
        self.main_layout.setStretchFactor(self.button1, 0)
        # self.main_layout.addWidget(self.button2, alignment=Qt.AlignmentFlag.AlignTop)
        # self.main_layout.setStretchFactor(self.button2, 0)
        
        #lower part
        # size.setVerticalStretch(100)
        # self.table.setSizePolicy(size)
        self.main_layout.addWidget(self.table)
        self.main_layout.setStretchFactor(self.table, 100)

        self.setLayout(self.main_layout)

        self.document_data = None


    def open_selection_wordcloud(self):
        self.new_window = WordCloudWindow(self.document_data)
        self.new_window.show()

    # def open_topic_wordcloud(self):
    #     self.new_window = WordCloudWindow(self.document_data, use_topic=True)
    #     self.new_window.show()
