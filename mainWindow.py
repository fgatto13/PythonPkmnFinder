# pokefinder_main.py
from PyQt5.QtWidgets import QMainWindow
from pokefinder import PokeFinder

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pokefinder")
        self.setGeometry(300, 300, 600, 400)
        self.setStyleSheet("background-color: #a9a9a9; border: 3px solid black; border-radius: 10px;")

        self.finder = PokeFinder()
        self.setCentralWidget(self.finder)
