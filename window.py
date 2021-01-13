"""Module ui_window.py - Crée la fenêtre comportant l'inspecteur, la carte et la zone de menu"""

import os, sys, subprocess, time, shutil
from carte import MapView
import file_io
import boite_robot
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QGroupBox, QPushButton, QSpacerItem
from PyQt5.QtWidgets import QDialog, QGraphicsView, QSizePolicy, QMessageBox, QApplication, QMainWindow, QFrame, QLabel, QLineEdit

from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QTimer, QSize, QRect

QPUSHBUTTON = "background-color: grey; border 2px solid rgb(113, 113, 113);border-width: 2px; " \
              "border-radius: 10px;  color: rgb(0,0,0) "


class Window(QMainWindow):
    """ Définit la fenêtre principale """

    # Création du signal de mise à jour de la liste des robots présents
    list_robot_changed_signal = pyqtSignal(list)

    def __init__(self, backend):

        super().__init__()
        self.main_window = QWidget()
        self.main_window.setObjectName("main_window")
        self.main_window.resize(1091, 782)
        self.main_window.setWindowTitle("Form")

        # Récupération de l'objet backend
        self.backend = backend

        self.boite_robot = boite_robot.BoiteRobot

        # Création des widgets de la fenêtre
        self.layout_window = QVBoxLayout(self.main_window)
        self.layout_map_inspector = QHBoxLayout()
        self.inspector_scroll_area = QScrollArea()
        self.scrollArea = QWidget(self.inspector_scroll_area)
        self.inspector_scroll_area.setWidget(self.scrollArea)
        self.layout_inspector = QVBoxLayout(self.scrollArea)
        self.menu_area = QGroupBox()
        self.layout_menu = QHBoxLayout(self.menu_area)
        self.button_record = QPushButton()
        self.button_play = QPushButton()
        self.button_pause = QPushButton()
        self.button_stop = QPushButton()
        self.button_save = QPushButton()
        self.spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.button_simu = QPushButton()
        self.button_settings = QPushButton()
        self.button_help = QPushButton()
        self.map_view = QGraphicsView()

        # Configuration des widgets de la fenêtre
        self.ui_setup_menu_area()
        self.ui_setup_map()
        self.ui_setup_inspecteur()

        # Création de la liste des noms des robots présents
        self.current_robots_list = []
        # Création du dictionnaire des robots présents (k=nom, v=boite robot)
        self.current_robots_dic = {}

        # Création de timer
        self.timer = QTimer(self)
        self.timer.start(100)
        # Connexion du signal timer avec le slot de mise à jour de la fenêtre
        self.timer.timeout.connect(lambda: self.update_window())

        # Connexion du signal de mise à jour de la liste des robots présents avec le slot de maj des robots affichés
        self.list_robot_changed_signal.connect(lambda l: self.update_robots(l))

        self.settings_dict = file_io.get_settings()
        self.act_settings()

    def ui_setup_map(self):
        self.map_view = MapView(self)
        self.map_view.setMinimumSize(QSize(0, 250))
        self.layout_map_inspector.addWidget(self.map_view)

    def ui_setup_inspecteur(self):
        """Crée  la QScrollBar qui contient un bouton 'Ajouter' (QPushButton) et les boites robots de la classe
        BoiteRobot de boite_robot """

        self.inspector_scroll_area.setWidgetResizable(True)
        self.inspector_scroll_area.setMinimumSize(QSize(410, 0))
        self.inspector_scroll_area.setMaximumSize(QSize(410, 16777215))
        self.inspector_scroll_area.setFrameShape(QFrame.NoFrame)
        self.inspector_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea = QWidget()
        self.scrollArea.setGeometry(QRect(0, 0, 410, 16777215))
        self.layout_map_inspector.addWidget(self.inspector_scroll_area)
        self.layout_window.addLayout(self.layout_map_inspector)

    def ui_setup_menu_area(self):
        """ Création de la zone menu"""
        # Création du bouton record
        self.button_record.setMaximumSize(200, 16777215)
        self.button_record.setText("Record")
        self.button_record.setCheckable(True)
        self.layout_menu.addWidget(self.button_record)
        self.button_record.clicked.connect(lambda: self.record())

        # Création du bouton play
        self.button_play.setMaximumSize(200, 16777215)
        self.button_play.setText("|>")
        self.layout_menu.addWidget(self.button_play)

        # Création du bouton pause
        self.button_pause.setMaximumSize(200, 16777215)
        self.button_pause.setText("||")
        self.layout_menu.addWidget(self.button_pause)

        # Création du bouton arrêt
        self.button_stop.setMaximumSize(200, 16777215)
        self.button_stop.setText("Stop")
        self.layout_menu.addWidget(self.button_stop)

        # Création du bouton sauvegarder
        self.button_save.setMaximumSize(200, 16777215)
        self.button_save.setText("Save")
        self.layout_menu.addWidget(self.button_save)

        self.layout_menu.addItem(self.spacerItem)

        # Création du bouton Simulateur

        self.layout_menu.addWidget(self.button_simu)
        self.button_simu.setText("Créer Simu")
        self.button_simu.clicked.connect(self.exec_simu)

        # Création du bouton configuration
        self.button_settings.setText("Configuration")
        self.layout_menu.addWidget(self.button_settings)
        self.button_settings.clicked.connect(self.show_settings)

        # Création du bouton aide
        self.button_help.setText("Aide")
        self.button_help.clicked.connect(lambda: show_help())
        self.layout_menu.addWidget(self.button_help)

        self.layout_window.addWidget(self.menu_area)

    def add_robot(self, nom_robot):
        """ Ajoute le robot dont le nom est placé en paramètre sous forme d'une boite robot dans la zone inspecteur """
        self.boite_robot = boite_robot.BoiteRobot(str(nom_robot), self)
        self.current_robots_dic[self.boite_robot.rid] = self.boite_robot
        self.layout_inspector.addWidget(self.boite_robot.groupBox_robot, 0, Qt.AlignTop)

    def remove_robot(self, nom_robot):
        """ Supprime de l'inspecteur la boite robot associée au robot dont le nom est placé en paramètre """
        deleted_robot = self.current_robots_dic.pop(nom_robot)
        deleted_robot.remove_box_robot()
        # Envoie l'information que le robot a été oublié (via le bouton oublier)
        self.backend.stopandforget_robot(nom_robot)

    def act_settings(self):
        """Effectuer les actions liées aux paramètres"""
        self.map_view.updt_map_data(self.settings_dict["Fichier de Carte"])

    def show_settings(self):
        """ Ouvre un popup (QDialog) Configuration
        permettant la modification des réglages d'enregistrement"""
        setting = QDialog(self.main_window)
        setting.setWindowTitle("Configuration")
        setting.setMinimumSize(500, 400)
        setting.layout = QVBoxLayout(setting)

        #paramètres d'un setting
        field_dict = {}

        def updt_settings():
            """Mise à jour des paramètres"""
            for setting_nm in self.settings_dict:
                self.settings_dict[setting_nm] = field_dict[setting_nm].text()
            file_io.set_settings(self.settings_dict)

        update_btn = QPushButton("Sauvegarder")
        setting.layout.addWidget(update_btn)
        update_btn.clicked.connect(updt_settings)
        update_btn.clicked.connect(self.act_settings)

        for setting_nm in self.settings_dict:
            box_layout = QHBoxLayout()
            setting.layout.addLayout(box_layout)

            label = QLabel(setting_nm)
            box_layout.addWidget(label)

            field_dict[setting_nm] = QLineEdit(setting)
            field_dict[setting_nm].setText(self.settings_dict[setting_nm])
            box_layout.addWidget(field_dict[setting_nm])

        setting.exec_()

    @pyqtSlot()
    def update_robots(self, new_robots):
        """ Met à jour la liste des robots présents et initialise la mise à jour de toutes les boites robots """

        # new_robots = self.backend.get_all_robots()

        # Ajoute les nouveaux robots
        for robot in set(new_robots) - set(self.current_robots_list):
            self.add_robot(robot)

        # Supprime les robots qui ne sont plus présents
        for robot in set(self.current_robots_list) - set(new_robots):
            self.remove_robot(robot)

        for robot in self.current_robots_dic.values():
            robot.update_boite_robot()

        # Met à jour la liste des robots présents
        self.current_robots_list = new_robots

    @pyqtSlot()
    def record(self):
        """ Enregistre des messages et commandes et arrête l'enregistrement lorsque cliquer une seconde fois """
        if self.button_record.isChecked():
            self.button_record.setStyleSheet("background-color: red")
            self.backend.record("BMC")
        else:
            self.button_record.setStyleSheet("background-color: grey")
            self.backend.record("EMC")

    @pyqtSlot()
    def update_window(self):
        """ Initialise la mise à jour de la fenêtre"""
        new_robots = self.backend.get_all_robots()
        self.update_robots(new_robots)
        self.list_robot_changed_signal.emit(self.current_robots_list)
    
    def exec_simu(self):
        """Exécute un simulateur en parallèle"""
        try:
            if os.path.exists(self.settings_dict["Chemin Simulateur"]):
                if shutil.which("python3"):
                    subprocess.Popen(["python3", self.settings_dict["Chemin Simulateur"], str(time.time())])
                else:
                    subprocess.Popen(["python", self.settings_dict["Chemin Simulateur"], str(time.time())])
        except Exception as exc:
            print(exc)

@pyqtSlot()
def show_help():
    """Ouvre une pop_up (QMessageBox) Aide avec la contenu du fichier aide.txt"""
    aide = QMessageBox()
    aide.setWindowTitle("Aide")
    list_aide = []
    with open("aide.txt", encoding='utf-8') as f:
        for line in f:
            list_aide.append(line)
    aide.setText("".join(list_aide))
    aide.exec_()

def main(backend):
    """ Création la fenêtre principale """
    app = QApplication(sys.argv)
    window = Window(backend)
    window.main_window.show()
    sys.exit(app.exec_())
