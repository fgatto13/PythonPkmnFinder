from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from pygame import mixer
import requests
from dataFetcher import *

class PokeFinder(QWidget):
    def __init__(self):
        super().__init__()
        self.pokemon_data = None
        self.pokeName = QLabel("Pokémon Name", self)
        self.lineEdit = QLineEdit(self)
        self.sendButton = QPushButton("search", self)
        self.playButton = QPushButton("play", self)
        self.spriteLabel = QLabel(self)
        self.logoImage = QLabel(self)
        self.infoLayout = QGridLayout()
        self.infoContainer = QFrame()

        self.infoContainer.setLayout(self.infoLayout)

        self.infoContainer.setObjectName("infoFrame")
        self.spriteLabel.setObjectName("spriteLabel")

        self.initUI()
        self.play_background_music()

    def initUI(self):
        self.setFixedSize(600, 800)
        self.lineEdit.setPlaceholderText("Input the name of the pokemon")
        self.lineEdit.setFixedHeight(45)
        self.pokeName.setFixedHeight(50)
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.lineEdit)
        hbox.addWidget(self.sendButton)

        pixmap = QPixmap("assets/logo.png")
        if not pixmap.isNull():
            scaled = pixmap.scaled(500, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logoImage.setPixmap(scaled)
            self.logoImage.setAlignment(Qt.AlignCenter)
        else:
            self.logoImage.setText("⚠️ Logo not found")

        vbox.addWidget(self.logoImage)
        vbox.addLayout(hbox)
        vbox.addWidget(self.pokeName)

        sprite_info_box = QHBoxLayout()
        sprite_info_box.addWidget(self.spriteLabel)
        sprite_info_box.addWidget(self.infoContainer)

        vbox.addLayout(sprite_info_box)
        vbox.addWidget(self.playButton)

        self.setLayout(vbox)
        self.playButton.clicked.connect(self.play_sound)
        self.sendButton.clicked.connect(self.find_pokemon)

        self.spriteLabel.setAlignment(Qt.AlignCenter)

        self.setStyleSheet("""
            QWidget {
                background-color: #9bbc0f;
                font-family: Courier New;
                font-weight: bold;
                color: #0f380f;
            }

            QLabel {
                font-size: 18px;
                border: 2px solid #0f380f;
                padding: 6px;
                border-radius: 8px;
                background-color: #e0f8d0;
            }

            QLineEdit {
                background-color: #e0f8d0;
                border: 2px solid #0f380f;
                border-radius: 5px;
                padding: 5px;
            }

            QPushButton {
                background-color: #8bac0f;
                border: 2px solid #0f380f;
                border-radius: 6px;
                padding: 10px;
                font-size: 18px;
            }

            QPushButton:hover {
                background-color: #0f380f;
                color: #e0f8d0;
            }

            #infoFrame, #spriteLabel {
                border: 5px double #0f380f;
                padding: 10px;
                background-color: #c4e66d;
                border-radius: 8px;
            }

            QLabel[statBox="true"] {
                font-size: 12px;
                min-width: 120px;
                qproperty-alignment: AlignCenter;
            }
        """)
        for btn in self.findChildren(QPushButton):
            btn.setCursor(Qt.PointingHandCursor)

    def find_pokemon(self):
        name = self.lineEdit.text().strip().lower()
        if not name:
            self.pokeName.setText("Please enter a Pokémon name.")
            return

        self.pokemon_data = get_pokemon_info(name)

        if not self.pokemon_data:
            self.pokeName.setText("Pokémon not found.")
            self.spriteLabel.clear()
            return

        self.pokeName.setText(
            f"{self.pokemon_data['name'].capitalize()} #{self.pokemon_data['id']:03}"
        )

        sprite_url = get_sprite_url(self.pokemon_data)
        if sprite_url:
            try:
                response = requests.get(sprite_url)
                response.raise_for_status()
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                self.spriteLabel.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
            except Exception as e:
                print(f"Failed to load sprite: {e}")
                self.spriteLabel.clear()
        else:
            self.spriteLabel.clear()

        self.update_info_panel()

    def play_sound(self):
        try:
            if not self.pokemon_data:
                print("❌ No Pokémon selected.")
                return

            tmp_path = download_cry(self.pokemon_data)
            if not tmp_path:
                print("❌ No cry found.")
                return

            if not mixer.get_init():
                mixer.init()

            cry_sound = mixer.Sound(tmp_path)
            cry_sound.set_volume(0.8)
            mixer.Channel(1).play(cry_sound)

        except Exception as e:
            print(f"❌ Failed to play cry: {e}")

    def play_background_music(self):
        mixer.init()
        mixer.music.load("assets/background.mp3")
        mixer.music.set_volume(0.1)
        mixer.music.play(-1)

    def update_info_panel(self):
        for i in reversed(range(self.infoLayout.count())):
            widget = self.infoLayout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        data = self.pokemon_data
        types = ", ".join(t["type"]["name"].capitalize() for t in data["types"])
        abilities = ", ".join(a["ability"]["name"].replace("-", " ").capitalize() for a in data["abilities"])
        weight = data["weight"] / 10
        exp = data["base_experience"]

        lines = [
            f"Type: {types}",
            f"Abilities: {abilities}",
            f"Weight: {weight:.1f} kg",
            f"Base EXP: {exp}"
        ]

        for i, text in enumerate(lines):
            label = QLabel(text)
            label.setProperty("statBox", True)
            self.infoLayout.addWidget(label, i, 0)