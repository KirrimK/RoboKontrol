"""Module ui_window.py - Crée la fenêtre comportant l'inspecteur, la carte et la zone de menu"""

from PyQt5 import QtCore, QtWidgets
import inspecteur

QPUSHBUTTON = "background-color: grey; border 2px solid rgb(113, 113, 113);border-width: 2px; " \
              "border-radius: 10px;  color: rgb(0,0,0) "


class Window(object):
    """ Définit la fenêtre principale dans laquelle est affiché toute les informations de l'appliaction"""

    def __init__(self, backend):
        """ Création de la fenêtre principale"""
        self.main_window = QtWidgets.QWidget()
        self.main_window.setObjectName("main_window")
        self.main_window.resize(1091, 782)
        self.main_window.setWindowTitle("Form")
        # Récupération de l'objet backend
        self.backend = backend
        # Création du layout de la fenêtre
        self.layout_window = QtWidgets.QVBoxLayout(self.main_window)


        self.create_menu_area()

        # Création de la zone map-inspecteur
        self.layout_map_inspector = QtWidgets.QHBoxLayout()
        self.layout_window.addLayout(self.layout_map_inspector)

        self.map_view = QtWidgets.QGraphicsView(self.main_window)  # todo:
        self.map_view.setMinimumSize(QtCore.QSize(0, 250))

        self.layout_map_inspector.addWidget(self.map_view)
        self.create_inspecteur_scrollbar(self.main_window)
        self.inspecteur = inspecteur.Inspecteur(self.inspector_scroll_area, self.layout_inspector, self.main_window,
                                                self.backend)

        self.inspector_scroll_area.setWidget(self.scrollArea)
        self.layout_map_inspector.addWidget(self.inspector_scroll_area)

        # QtCore.QMetaObject.connectSlotsByName(self.main_window)

        self.button_help.clicked.connect(lambda: show_help(self.main_window))

        self.main_window.show()

    def create_inspecteur_scrollbar(self, main_window):
        """Crée  la QScrollBar qui contient un bouton'Ajouter' (QPushButton) et les boites robots de la classe
        BoiteRobot de boite_robot """

        self.inspector_scroll_area = QtWidgets.QScrollArea(main_window)
        self.inspector_scroll_area.setMinimumSize(QtCore.QSize(350, 0))
        self.inspector_scroll_area.setMaximumSize(QtCore.QSize(350, 16777215))
        self.inspector_scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.inspector_scroll_area.setWidgetResizable(True)
        # noinspection PyArgumentList
        self.scrollArea = QtWidgets.QWidget(self.inspector_scroll_area)
        self.scrollArea.setGeometry(QtCore.QRect(0, 0, 350, 16777215))
        self.layout_inspector = QtWidgets.QVBoxLayout(self.scrollArea)

        #"""Crée le QPushButton et l'ajoute à la QScrollBar"""
        #self.button_add_robot = QtWidgets.QPushButton(self.scrollArea)
        #self.button_add_robot.setMinimumSize(0, 30)
        #self.button_add_robot.setText("Ajouter un robot")
        #self.button_add_robot.setStyleSheet(QPUSHBUTTON)
        #self.button_add_robot.clicked.connect(lambda: self.add_robot())
        #self.layout_inspector.addWidget(self.button_add_robot)

    def create_menu_area(self):
        """ Création de la zone menu"""
        self.menu_area = QtWidgets.QGroupBox(self.main_window)
        self.layout_menu = QtWidgets.QHBoxLayout(self.menu_area)
        self.layout_window.addWidget(self.menu_area)

        # Création du bouton record
        self.button_record = QtWidgets.QPushButton(self.menu_area)
        self.button_record.setMaximumSize(200, 16777215)
        self.button_record.setText("Record")
        self.button_record.setCheckable(True)
        self.layout_menu.addWidget(self.button_record)
        self.button_record.clicked.connect(lambda: color_record())


        def color_record():
            """ Change la couleur du bouton record suivant qu'il est activé ou non """
            if self.button_record.isChecked():
                self.button_record.setStyleSheet("background-color: grey")
            else:
                self.button_record.setStyleSheet("background-color: red")

        # Création du bouton play
        self.button_play = QtWidgets.QPushButton(self.menu_area)
        self.button_play.setMaximumSize(200, 16777215)
        self.button_play.setText("|>")
        self.layout_menu.addWidget(self.button_play)

        # Création du bouton pause
        self.button_pause = QtWidgets.QPushButton(self.menu_area)
        self.button_pause.setMaximumSize(200, 16777215)
        self.button_pause.setText("||")
        self.layout_menu.addWidget(self.button_pause)

        # Création du bouton arrêt
        self.button_stop = QtWidgets.QPushButton(self.menu_area)
        self.button_stop.setMaximumSize(200, 16777215)
        self.button_stop.setText("Stop")
        self.layout_menu.addWidget(self.button_stop)

        # Création du bouton sauvegarder
        self.button_save = QtWidgets.QPushButton(self.menu_area)
        self.button_save.setMaximumSize(200, 16777215)
        self.button_save.setText("Save")
        self.layout_menu.addWidget(self.button_save)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layout_menu.addItem(spacerItem)

        # Création du bouton configuration
        self.button_settings = QtWidgets.QPushButton(self.menu_area)
        self.button_settings.setText("Configuration")
        self.layout_menu.addWidget(self.button_settings)
        self.button_settings.clicked.connect(lambda: show_settings(self.main_window))

        # Création du bouton aide
        self.button_help = QtWidgets.QPushButton(self.menu_area)
        self.button_help.setText("Aide")
        self.layout_menu.addWidget(self.button_help)

def show_settings(main_window):
    """ Ouvre un popup (QDialog) Configuration permettant la modification des réglages d'enregistrement"""
    setting = QtWidgets.QDialog(main_window)
    setting.setWindowTitle("Configuration")
    setting.setMinimumSize(500,750)
    setting.exec_()

def show_help(main_window):
    """Ouvre une pop_up (QMessageBox) Aide avec la contenu du fichier aide.txt"""
    aide = QtWidgets.QMessageBox(main_window)
    aide.setWindowTitle("Aide")
    list_aide = []
    with open("aide.txt", encoding='utf-8') as f:
        for line in f:
            list_aide.append(line)
    aide.setText("".join(list_aide))
    aide.exec_()


def main(backend):
    """ Création la fenêtre principale """
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Window(backend)
    sys.exit(app.exec_())
