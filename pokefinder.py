from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from pygame import mixer
import requests
from dataFetcher import *

class PokeFinder(QWidget):
    def __init__(self):
        super().__init__()
        # uninitialized data variables
        self.current_pixmap = None
        self.back_pixmap = None
        self.front_pixmap = None
        self.is_shiny = None
        self.back_sprite_url = None
        self.front_sprite_url = None
        self.pokemon_data = None
        # visual elements
        self.pokeName = QLabel("Pokémon Name", self)
        self.lineEdit = QLineEdit(self)
        self.sendButton = QPushButton("search", self)
        self.playButton = QPushButton("play", self)
        self.spriteLabel = QLabel(self)
        self.logoImage = QLabel(self)
        self.infoLayout = QGridLayout()
        self.statsLayout = QGridLayout()
        self.infoContainer = QFrame()
        self.statsContainer = QFrame()
        # layout definition
        self.infoContainer.setLayout(self.infoLayout)
        self.statsContainer.setLayout(self.statsLayout)
        # custom name labels for specific objects (for styling)
        self.infoContainer.setObjectName("infoFrame")
        self.spriteLabel.setObjectName("spriteLabel")
        self.statsContainer.setObjectName("statsFrame")

        self.initUI()
        self.play_background_music()

    def initUI(self):
        self.setFixedSize(800, 700)
        self.logoImage.setFixedHeight(200)

        self.lineEdit.setPlaceholderText("Input the name (or # of entry) of the pokemon")
        self.lineEdit.setFixedHeight(45)

        self.pokeName.setFixedHeight(50)

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.lineEdit)
        hbox.addWidget(self.sendButton)

        pixmap = QPixmap("assets/logo.png")
        if not pixmap.isNull():
            scaled = pixmap.scaled(300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
        sprite_info_box.addWidget(self.statsContainer)

        vbox.addLayout(sprite_info_box)
        vbox.addWidget(self.playButton)

        self.setLayout(vbox)
        self.playButton.clicked.connect(self.play_sound)
        self.sendButton.clicked.connect(self.find_pokemon)

        self.spriteLabel.setAlignment(Qt.AlignCenter)

        self.lineEdit.returnPressed.connect(self.find_pokemon)

        for btn in self.findChildren(QPushButton):
            btn.setCursor(Qt.PointingHandCursor)

        self.setStyleSheet("""
            QWidget {
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

            #infoFrame, #spriteLabel, #statsFrame {
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

    def find_pokemon(self):
        name = self.lineEdit.text().strip().lower()
        if not name:
            self.pokeName.setText("Please enter a Pokémon name.")
            self.pokemon_data = None  # clear data
            self.spriteLabel.clear()
            self.update_info_panel()  # 🔁 Clear previous info/stats
            return

        self.pokemon_data = get_pokemon_info(name)

        if not self.pokemon_data:
            self.pokeName.setText("Pokémon not found.")
            self.spriteLabel.clear()
            self.update_info_panel()  # 🔁 Clear previous info/stats
            return

        self.pokeName.setText(
            f"{self.pokemon_data['name'].capitalize()} #{self.pokemon_data['id']:03}"
        )

        sprite_data = get_sprite_url(self.pokemon_data)
        if sprite_data:
            front_sprite_url, is_shiny, back_sprite_url, _ = sprite_data

            # Store both sprites and flag
            self.front_sprite_url = front_sprite_url
            self.back_sprite_url = back_sprite_url
            self.is_shiny = is_shiny

            # Initially display front sprite
            self.display_sprite(self.front_sprite_url)

            # Connect the sprite label click to toggle sprites
            self.spriteLabel.mousePressEvent = self.toggle_sprite
            self.play_sound(self.is_shiny)
        else:
            self.spriteLabel.clear()
        self.update_info_panel()

    def toggle_sprite(self, event):
        # Toggle sprite: If currently showing front, show back and vice versa
        if not hasattr(self, 'current_pixmap') or self.current_pixmap.isNull():
            return  # Do nothing if there's no sprite loaded.

        # Toggle between front and back sprite URLs
        current_sprite_url = self.front_sprite_url if self.current_pixmap == self.front_pixmap else self.back_sprite_url
        new_sprite_url = self.back_sprite_url if current_sprite_url == self.front_sprite_url else self.front_sprite_url

        self.display_sprite(new_sprite_url)

    def display_sprite(self, sprite_url):
        try:
            response = requests.get(sprite_url)
            response.raise_for_status()

            # Load the image into a QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)

            # Store the current pixmap
            if sprite_url == self.front_sprite_url:
                self.front_pixmap = pixmap
            else:
                self.back_pixmap = pixmap

            self.current_pixmap = pixmap  # Store the current pixmap (front or back)

            # Display the pixmap
            self.spriteLabel.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
            # set the cursor to be a pointer
            self.spriteLabel.setCursor(Qt.PointingHandCursor)
        except Exception as e:
            print(f"Failed to load sprite: {e}")
            self.spriteLabel.clear()

    def play_sound(self, is_shiny):
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

            if is_shiny == 0:
                shiny_sound = mixer.Sound("assets/shiny.mp3")
                shiny_sound.set_volume(1)

                # Play shiny sound after the cry ends (non-blocking)
                cry_duration_ms = int(cry_sound.get_length() * 1000)
                QTimer.singleShot(cry_duration_ms, lambda: mixer.Channel(1).play(shiny_sound))

        except Exception as e:
            print(f"❌ Failed to play cry: {e}")

    @staticmethod
    def play_background_music():
        mixer.init()
        mixer.music.load("assets/background.mp3")
        mixer.music.set_volume(0.1)
        mixer.music.play(-1)

    def update_info_panel(self):
        # Clear previous info widgets
        for layout in [self.infoLayout, self.statsLayout]:
            for i in reversed(range(layout.count())):
                widget = layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

        # If no Pokémon data, exit early
        if not self.pokemon_data:
            return

        data = self.pokemon_data
        types = ", ".join(t["type"]["name"].capitalize() for t in data["types"])
        abilities = "\n".join(a["ability"]["name"].replace("-", " ").capitalize() for a in data["abilities"])
        stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}
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

        aliases = {
            "hp": "HP", "attack": "ATK", "defense": "DEF",
            "special-attack": "SPA", "special-defense": "SPD", "speed": "SPE"
        }

        for i, (stat_name, value) in enumerate(stats.items()):
            short_name = aliases.get(stat_name, stat_name.upper())
            label = QLabel(f"{short_name}: {value}")
            label.setProperty("statBox", True)
            self.statsLayout.addWidget(label, i, 1)
