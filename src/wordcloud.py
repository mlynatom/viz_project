import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout

class WordCloudWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wordcloud Window")
        layout = QVBoxLayout()
        layout.addWidget(QPushButton("Close", clicked=self.close))
        self.setLayout(layout)