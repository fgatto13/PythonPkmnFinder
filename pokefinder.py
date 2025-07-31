from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QHBoxLayout
from pygame import mixer

from dataFetcher import *


class PokeFinder(QWidget):
    def __init__(self):
        super().__init__()
        self.pokeName = QLabel("Pokémon Name", self)
        self.lineEdit = QLineEdit(self)
        self.sendButton = QPushButton("search", self)
        self.playButton = QPushButton("play", self)
        self.spriteLabel = QLabel(self)  # this displays the QPixmap
        self.logoImage = QLabel(self)

        self.initUI()
        self.play_background_music()

    def initUI(self):
        self.lineEdit.setPlaceholderText("Input the name of the pokemon")

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.lineEdit)
        hbox.addWidget(self.sendButton)

        # Load and scale the logo
        pixmap = QPixmap("assets/logo.png")
        if not pixmap.isNull():
            scaled = pixmap.scaled(500, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logoImage.setPixmap(scaled)
            self.logoImage.setAlignment(Qt.AlignCenter)
        else:
            self.logoImage.setText("⚠️ Logo not found")

        # Add to layout
        vbox.addWidget(self.logoImage)
        vbox.addLayout(hbox)
        vbox.addWidget(self.pokeName)
        vbox.addWidget(self.spriteLabel)
        vbox.addWidget(self.playButton)

        self.setLayout(vbox)

        self.playButton.clicked.connect(self.play_sound)
        self.sendButton.clicked.connect(self.find_pokemon)

        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignCenter)

        hbox = QHBoxLayout()
        hbox.setAlignment(Qt.AlignCenter)

        vbox.setSpacing(20)
        vbox.setContentsMargins(30, 30, 30, 30)

        self.spriteLabel.setFixedHeight(200)
        self.spriteLabel.setAlignment(Qt.AlignCenter)

        # now for some styling
        self.setStyleSheet("""
            QWidget {
                background-color: #9bbc0f;
                font-family: Courier New;
                font-weight: bold;
                color: #0f380f;
            }

            QLabel {
                font-size: 20px;
                border: 2px solid #0f380f;
                padding: 10px;
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
        """)

    def find_pokemon(self):
        name = self.lineEdit.text().strip().lower()
        if not name:
            self.pokeName.setText("Please enter a Pokémon name.")
            return

        data = get_pokemon_info(name)

        if not data:
            self.pokeName.setText("Pokémon not found.")
            self.spriteLabel.clear()
            return

        # Set the name
        self.pokeName.setText(data["name"].capitalize())

        # Get and display the sprite
        sprite_url = get_sprite_url(data)
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

    def play_sound(self):
        try:
            tmp_path = download_cry(self.lineEdit.text())

            if not mixer.get_init():
                mixer.init()

            cry_sound = mixer.Sound(tmp_path)
            cry_sound.set_volume(0.8)  # Set cry volume before playing

            # Use a separate channel so it plays *on top of* the background music
            cry_channel = mixer.Channel(1)
            cry_channel.play(cry_sound)

        except Exception as e:
            print(f"❌ Failed to play cry: {e}")

    def play_background_music(self):
        mixer.init()
        mixer.music.load("assets/background.mp3")  # your background music file
        mixer.music.set_volume(0.1)  # optional: reduce volume
        mixer.music.play(-1)  # -1 = infinite loop