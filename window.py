"""Module ui_window.py - Crée la fenêtre comportant l'inspecteur, la carte et la zone de menu"""

import os, sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QGroupBox, QPushButton, QSpacerItem, QStatusBar
from PyQt5.QtWidgets import QDialog, QSizePolicy, QMessageBox, QFileDialog
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QCheckBox
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QSize
from carte import MapView
import display as dsp
import externals
import lecture_fichiers_enregistres as lect

WINDOW_STYLE = "QLCDNumber{background-color: grey;border: 1px solid dimgray;color: white;border-radius: 2px} "\
               "QProgressBar{background-color : grey;border: 1px solid dimgray;border-radius: 2px}" \
               "QPushButton{border: 1px solid rgb(150,150,150);border-radius: 2px}" \
               "QPushButton:hover{background-color: rgb(180,180,180); border: 1px solid rgb(130,130,130)}"\
               "QPushButton:pressed{background-color: rgb(150,150,150); border: 1px solid rgb(130,130,130)}" \
               
BUTTON_ON = "QPushButton{background-color: rgb(180,0,0); border: 1px solid rgb(100,0,0)}"
BUTTON_OFF = ""

QSIZE = QSize(100, 30)
QSIZE_BIG = QSize(160, 30)


class Window(QMainWindow):
    """ Définit la fenêtre principale """

    # Création du signal de mise à jour de la liste des robots présents
    list_robot_changed_signal = pyqtSignal(list)

    playback_sgnl = pyqtSignal(list)

    def __init__(self, backend):

        super().__init__()
        self.resize(1200, 600)
        self.setWindowTitle("Form")
        self.setStyleSheet(WINDOW_STYLE)

        # Récupération de l'objet backend
        self.backend = backend
        self.backend.launch_qt()

        self.record_status = -1

        #Création du lecteur de fichiers
        self.lecteur = lect.Lecteur (self)

        # Création des widgets de la fenêtre
        self.window = QWidget()
        self.layout_window = QHBoxLayout(self.window)
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
        self.statuslabel = QLabel()

        # Création de la liste des noms des robots présents
        self.current_robots_list = []
        self.current_robots_dic = {}

        # Configuration des widgets de la fenêtre
        self.ui_setup_menu_area()
        self.ui_setup_map()
        self.ui_setup_inspector()
        self.ui_setup_statusbar()

        self.ui_setup_window()

        self.settings_dict = externals.get_settings()
        self.act_settings()

    def ui_setup_window(self):
        """Mise en place de la fenêtre principale"""
        self.setCentralWidget(self.window)
        self.setMenuWidget(self.menu_area)
        self.setStatusBar(self.statusbar)

    def ui_setup_map(self):
        """Crée la carte et l'affiche dans la fenêtre"""
        self.map_view = MapView(self)
        self.map_view.setMinimumSize(QSize(0, 250))
        self.layout_window.addWidget(self.map_view)

    def ui_setup_inspector(self):
        """ Crée l'inspecteur (QTabWidget) et l'affiche dans la fenêtre"""
        self.inspecteur = dsp.DisplayAnnuaire(self)
        self.layout_window.addWidget(self.inspecteur)

    def ui_setup_menu_area(self):
        """ Création de la zone menu"""
        self.menu_area.setStyleSheet("QGroupBox{border: 0px;}")

        # Création du bouton record
        self.button_record.setFixedSize(QSIZE)
        self.button_record.setText("Record")
        self.button_record.setCheckable(True)
        self.layout_menu.addWidget(self.button_record)
        self.button_record.clicked.connect(self.record)

        # Création du bouton play
        self.button_play.setFixedSize(QSIZE)
        self.button_play.setText("|>")
        self.button_play.setCheckable (True)
        self.button_play.clicked.connect(self.show_play_dialog)
        self.layout_menu.addWidget(self.button_play)

        # Création du bouton pause
        self.button_pause.setFixedSize(QSIZE)
        self.button_pause.setText("||")
        self.button_pause.setCheckable (True)
        self.button_pause.clicked.connect (self.onPauseButton)
        self.layout_menu.addWidget(self.button_pause)

        # Création du bouton arrêt
        self.button_stop.setFixedSize(QSIZE)
        self.button_stop.setText("Stop")
        self.button_stop.clicked.connect(self.on_stoprecord_button)
        self.layout_menu.addWidget(self.button_stop)

        # Création du bouton sauvegarder
        self.button_save.setFixedSize(QSIZE)
        self.button_save.setText("Save")
        self.button_save.clicked.connect(self.on_save_button)
        self.layout_menu.addWidget(self.button_save)

        self.layout_menu.addItem(self.spacer_item)

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

        self.backend.widget.record_signal.connect(self.updt_status_record)
        self.playback_sgnl.connect(self.updt_status_playback)

    def updt_status_record(self, state):
        """Met à jour la barre de status quand enregistrement en cours"""
        if state == -1:
            self.statusbar.showMessage("Enregistrement arrêté et sauvegardé sur disque.")
            self.record_status = -1
        elif state == -2:
            self.statusbar.showMessage("Enregistrement arrêté et tampon supprimé.")
            self.record_status = -1
        elif state == 0:
            self.statusbar.showMessage("Enregistrement démarré.")
            self.record_status = 0
        elif state == 1:
            self.record_status += 1
            self.statusbar.showMessage("Enregistrement: {} reçus.".format(self.record_status))

    def updt_status_playback(self, args):
        """Met à jour la barre de status quand lecture en cours"""
        if args[0] == -1:
            self.statusbar.showMessage("Lecture arrêtée")
        elif args[0] == -2:
            self.statusbar.showMessage("Lecture en pause")
        elif args[0] == 0:
            if args[2] == 1:
                self.statusbar.showMessage("Lecture de messages démarrée.")
            else:
                self.statusbar.showMessage("Lecture de commandes démarrée.")
        else:
            msg_mot = "messages restants" if args[2] == 1 else "commandes restantes"
            self.statusbar.showMessage("Lecture: {} {}".format(args[1], msg_mot))

    def ui_setup_statusbar(self):
        """ Configure la bar d'état """
        # self.layout_window.addWidget(self.statusbar)
        self.statusbar.addPermanentWidget(self.statuslabel)

    def show_play_dialog(self):
        """Ouvre un petit popup demandant de choisir un fichier à lire"""
        if not self.button_pause.isChecked ():
            file_name = self.get_filename()
            self.settings_dict["Enregistrement/Playback (Dernière Lecture)"] = file_name
        self.onPlayButton ()

    def get_filename(self):
        """Obtenir un nom de fichier à partir d'un QFileDialog"""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Choisir un fichier à lire",
                                                "", "All Files (*)", options=options)
        return file_name

    def act_settings(self):
        """Effectuer les actions liées aux paramètres"""
        record_path = self.settings_dict["Enregistrement/Playback (Chemin Sauvegarde)"]
        dim_crte = self.settings_dict["Carte (Dimensions)"].split("x")
        self.map_view.updt_map_data(self.settings_dict["Carte (Fichier)"],
                                    int(dim_crte[0]), int(dim_crte[1]))
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
        if not os.path.exists(record_path) and record_path != "":
            os.mkdir(self.settings_dict["Enregistrement/Playback (Chemin Sauvegarde)"])

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
        update_btn.setMinimumSize(16777215, 25)
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
            self.button_record.setStyleSheet(BUTTON_ON)
            self.backend.record("BMC")

    @pyqtSlot()
    def on_stoprecord_button(self):
        """Bouton stop cliqué"""
        if self.button_record.isChecked():
            self.button_record.setStyleSheet(BUTTON_OFF)
            self.backend.record("EMCD")
            self.button_record.setChecked(False)
        elif self.button_play.isChecked () or self.button_pause.isChecked():
            self.button_pause.setChecked (False)
            self.button_play.setChecked (False)
            self.button_play.setStyleSheet (BUTTON_OFF)
            self.button_pause.setStyleSheet (BUTTON_OFF)
            self.lecteur.onStopButton ()

    @pyqtSlot()
    def on_save_button(self):
        """Bouton sauvegarde cliqué"""
        path = self.settings_dict["Enregistrement/Playback (Chemin Sauvegarde)"]
        if self.button_record.isChecked():
            self.button_record.setStyleSheet(BUTTON_OFF)
            self.backend.record("EMCSD", path)
            self.button_record.setChecked(False)

    @pyqtSlot()
    def onPlayButton (self):
        """Bouton play cliqué"""
        if self.button_pause.isChecked ():
            self.button_pause.setChecked (False)
            self.button_pause.setStyleSheet (BUTTON_OFF)
        self.lecteur.onPlayButton ()

    @pyqtSlot ()
    def onPauseButton (self):
        """Bouton pause cliqué"""
        if self.button_play.isChecked ():
            self.button_play.setChecked (False)
            self.button_play.setStyleSheet (BUTTON_OFF)
            self.button_pause.setChecked (True)
            self.button_pause.setStyleSheet (BUTTON_ON)
            self.lecteur.onPauseButton ()

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
    window = Window(backend)
    window.backend.annu = window.inspecteur
    window.show()
    sys.exit(app.exec_())
