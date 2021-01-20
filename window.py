"""Module ui_window.py - Crée la fenêtre comportant l'inspecteur, la carte et la zone de menu"""

import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QGroupBox, QPushButton, QSpacerItem, QStatusBar
from PyQt5.QtWidgets import QDialog, QSizePolicy, QMessageBox, QFileDialog
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QCheckBox
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QTimer, QSize
from carte import MapView
from inspecteur import Inspecteur
import externals

WINDOW_STYLE = "QLCDNumber{background-color: grey;border: 2px solid rgb(113, 113, 113);border-width: 2px; " \
                "border-radius: 5px;  color: rgb(255, 255, 255)} " \

QSIZE = QSize(100, 30)
QSIZE_BIG = QSize(160, 30)


class Window(QMainWindow):
    """ Définit la fenêtre principale """

    # Création du signal de mise à jour de la liste des robots présents
    list_robot_changed_signal = pyqtSignal(list)

    def __init__(self, backend):

        super().__init__()
        self.window = QWidget()
        self.window.setObjectName("main_window")
        self.window.resize(1091, 782)
        self.window.setWindowTitle("Form")

        self.window.setStyleSheet(WINDOW_STYLE)

        # Récupération de l'objet backend
        self.backend = backend

        # Création des widgets de la fenêtre
        self.layout_window = QVBoxLayout(self.window)
        self.layout_map_inspector = QHBoxLayout()
        self.menu_area = QGroupBox()
        self.layout_menu = QHBoxLayout(self.menu_area)
        self.button_record = QPushButton()
        self.button_play = QPushButton()
        self.button_pause = QPushButton()
        self.button_stop = QPushButton()
        self.button_save = QPushButton()
        self.spacer_item = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.button_simu = QPushButton()
        self.button_settings = QPushButton()
        self.button_help = QPushButton()
        self.statusbar = QStatusBar()

        # Création de la liste des noms des robots présents
        self.current_robots_list = []
        self.current_robots_dic = {}

        # Configuration des widgets de la fenêtre
        self.ui_setup_menu_area()
        self.ui_setup_map()
        self.ui_setup_inspector()
        self.layout_window.addLayout(self.layout_map_inspector)
        self.ui_setup_statusbar()

        # Création du dictionnaire des robots présents (k=nom, v=boite robot)

        # Connexion du signal de UpdateTrigger avec le slot de mise à jour de la fenêtre
        self.backend.widget.UpdateTrigger.connect(self.update_window)

        # Connexion du signal de mise à jour de la liste des robots présents
        # avec le slot de maj des robots affichés
        self.list_robot_changed_signal.connect(lambda l: self.inspecteur.update_robots(l))

        self.settings_dict = externals.get_settings()
        self.act_settings()

    def ui_setup_map(self):
        """Crée la carte et l'affiche dans la fenêtre"""
        self.map_view = MapView(self)
        self.map_view.setMinimumSize(QSize(0, 250))
        self.layout_map_inspector.addWidget(self.map_view)

    def ui_setup_inspector(self):
        """ Crée l'inspecteur (QTabWidget) et l'affiche dans la fenêtre"""
        self.inspecteur = Inspecteur(self)
        self.layout_map_inspector.addWidget(self.inspecteur)

    def ui_setup_menu_area(self):
        """ Création de la zone menu"""
        self.menu_area.setStyleSheet("QGroupBox  {border: 0px;}")

        # Création du bouton record
        self.button_record.setFixedSize(QSIZE)
        self.button_record.setText("Record")
        self.button_record.setCheckable(True)
        self.layout_menu.addWidget(self.button_record)
        self.button_record.clicked.connect(self.record)

        # Création du bouton play
        self.button_play.setFixedSize(QSIZE)
        self.button_play.setText("|>")
        self.button_play.clicked.connect(self.show_play_dialog)
        self.layout_menu.addWidget(self.button_play)

        # Création du bouton pause
        self.button_pause.setFixedSize(QSIZE)
        self.button_pause.setText("||")
        self.layout_menu.addWidget(self.button_pause)

        # Création du bouton arrêt
        self.button_stop.setFixedSize(QSIZE)
        self.button_stop.setText("Stop")
        self.button_stop.clicked.connect(lambda: self.onStopRecordButton())
        self.layout_menu.addWidget(self.button_stop)

        # Création du bouton sauvegarder
        self.button_save.setFixedSize(QSIZE)
        self.button_save.setText("Save")
        self.button_save.clicked.connect(lambda: self.onSaveButton())
        self.layout_menu.addWidget(self.button_save)

        self.layout_menu.addItem(self.spacer_item)

        # Création du bouton Simulateur
        self.layout_menu.addWidget(self.button_simu)
        self.button_simu.setFixedSize(QSIZE)
        self.button_simu.setText("Nv. Simu.")
        self.button_simu.clicked.connect(lambda: externals.exec_simu(self.settings_dict))

        # Création du bouton configuration
        self.button_settings.setText("Configuration")
        self.button_settings.setFixedSize(QSIZE_BIG)
        self.layout_menu.addWidget(self.button_settings)
        self.button_settings.clicked.connect(self.show_settings)

        # Création du bouton aide
        self.button_help.setText("Aide")
        self.button_help.setFixedSize(QSIZE)
        self.button_help.clicked.connect(show_help)
        self.layout_menu.addWidget(self.button_help)

        self.layout_window.addWidget(self.menu_area)

    def ui_setup_statusbar(self):
        """ Configure la bar d'état """
        self.layout_window.addWidget(self.statusbar)

    def show_play_dialog(self):
        """Ouvre un petit popup demandant de choisir un fichier à lire"""
        file_name = self.get_filename()
        self.settings_dict["Enregistrement/Playback (Dernière Lecture)"] = file_name

    def get_filename(self):
        """Obtenir un nom de fichier à partir d'un QFileDialog"""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Choisir un fichier à lire", "", "All Files (*)", options=options)
        return file_name

    def act_settings(self):
        """Effectuer les actions liées aux paramètres"""
        dim_crte = self.settings_dict["Carte (Dimensions)"].split("x")
        self.map_view.updt_map_data(self.settings_dict["Carte (Fichier)"], int(dim_crte[0]), int(dim_crte[1]))
        if self.settings_dict["Simulateur (Activer Bouton)"]:
            self.button_simu.show()
        else:
            self.button_simu.hide()
        if self.settings_dict["Enregistrement/Playback (Activer Bouton)"]:
            self.button_record.show()
            self.button_play.show()
            self.button_pause.show()
            self.button_stop.show()
            self.button_save.show()
        else:
            self.button_record.hide()
            self.button_play.hide()
            self.button_pause.hide()
            self.button_stop.hide()
            self.button_save.hide()

    def show_settings(self):
        """ Ouvre un popup (QDialog) Configuration
        permettant la modification des réglages d'enregistrement"""
        setting = QDialog(self.window)
        setting.setWindowTitle("Configuration")
        setting.setMinimumSize(550, 400)
        setting.layout = QVBoxLayout(setting)

        #paramètres d'un setting
        field_dict = {}

        def updt_settings():
            """Mise à jour des paramètres"""
            for setting_nm in self.settings_dict:
                if isinstance(field_dict[setting_nm], QCheckBox):
                    self.settings_dict[setting_nm] = field_dict[setting_nm].isChecked()
                else:
                    self.settings_dict[setting_nm] = field_dict[setting_nm].text()
            externals.set_settings(self.settings_dict)

        update_btn = QPushButton("Sauvegarder")
        setting.layout.addWidget(update_btn)
        update_btn.clicked.connect(updt_settings)
        update_btn.clicked.connect(self.act_settings)

        for setting_nm in self.settings_dict:
            box_layout = QHBoxLayout()
            setting.layout.addLayout(box_layout)

            label = QLabel(setting_nm)
            box_layout.addWidget(label)

            if isinstance(self.settings_dict[setting_nm], bool):
                field_dict[setting_nm] = QCheckBox(setting)
                field_dict[setting_nm].setChecked(self.settings_dict[setting_nm])
            else:
                field_dict[setting_nm] = QLineEdit(setting)
                field_dict[setting_nm].setText(self.settings_dict[setting_nm])
            box_layout.addWidget(field_dict[setting_nm])

        setting.exec_()

    @pyqtSlot()
    def record(self):
        """ Enregistre des messages et commandes
        et arrête l'enregistrement lorsque cliquer une seconde fois """
        if self.button_record.isChecked():
            self.button_record.setStyleSheet("background-color: red")
            self.backend.record("BMC")

    @pyqtSlot()
    def onStopRecordButton(self):
        if self.button_record.isChecked():
            self.button_record.setStyleSheet("background-color: lightgrey")
            self.backend.record("EMCD")
            self.button_record.setChecked(False)

    @pyqtSlot()
    def onSaveButton(self):
        path = self.settings_dict["Enregistrement/Playback (Chemin Sauvegarde)"]
        if self.button_record.isChecked():
            self.button_record.setStyleSheet("background-color: lightgrey")
            self.backend.record("EMCSD", path)
            self.button_record.setChecked(False)

    @pyqtSlot()
    def update_window(self):
        """ Initialise la mise à jour de la fenêtre"""
        new_robots = self.backend.get_all_robots()

        self.inspecteur.update_robots(new_robots)
        self.list_robot_changed_signal.emit(self.current_robots_list)


@pyqtSlot()
def show_help():
    """Ouvre une pop_up (QMessageBox) Aide avec la contenu du fichier aide.txt"""
    aide = QMessageBox()
    aide.setWindowTitle("Aide")
    with open("aide.txt", encoding='utf-8') as file:
        list_aide = file.readlines()
    aide.setText("".join(list_aide))
    aide.exec_()


def main(backend):
    """ Création la fenêtre principale """
    app = QApplication(sys.argv)
    backend.launchQt()
    window = Window(backend)
    window.window.show()
    sys.exit(app.exec_())
