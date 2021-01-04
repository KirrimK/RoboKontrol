"""Module ui_window.py - Crée la fenêtre comportant l'inspecteur, la carte et d'autres fonctionnalités"""

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import inspecteur

QPUSHBUTTON = "background-color: grey; border 2px solid rgb(113, 113, 113);border-width: 2px; " \
              "border-radius: 10px;  color: rgb(0,0,0) "


class Window(object):
    """ Définit la fenêtre dans laquelle est affiché toute les informations de l'appliaction"""

    def __init__(self, backend):
        """ Création de la fenêtre"""
        self.main_window = QtWidgets.QWidget()
        self.main_window.setObjectName("main_window")
        self.main_window.resize(1091, 782)
        self.main_window.setWindowTitle("Form")
        # Récupération de l'objet backend
        self.backend = backend
        # Création du layout de la fenêtre
        self.layout_window = QtWidgets.QVBoxLayout(self.main_window)
        # Création de la zone menu
        self.menu_area = QtWidgets.QGroupBox(self.main_window)
        self.layout_menu = QtWidgets.QHBoxLayout(self.menu_area)
        self.layout_window.addWidget(self.menu_area)
        # Création du bouton "Configurer la map"
        self.button_map = QtWidgets.QPushButton(self.menu_area)
        self.button_map.setMaximumSize(200, 16777215)
        self.button_map.setText("Configurer la carte")
        self.layout_menu.addWidget(self.button_map)
        # Création du bouton "Connecter un robot"
        self.button_connect_robot = QtWidgets.QPushButton(self.menu_area)
        self.button_connect_robot.setText("Connecter un robot")
        self.layout_menu.addWidget(self.button_connect_robot)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layout_menu.addItem(spacerItem)
        # Création du bouton aide
        self.button_help = QtWidgets.QPushButton(self.menu_area)
        self.button_help.setText("Aide")
        self.layout_menu.addWidget(self.button_help)

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

        """Crée le QPushButton et l'ajoute à la QScrollBar"""
        self.button_add_robot = QtWidgets.QPushButton(self.scrollArea)
        self.button_add_robot.setMinimumSize(0, 30)
        self.button_add_robot.setText("Ajouter un robot")
        self.button_add_robot.setStyleSheet(QPUSHBUTTON)
        self.button_add_robot.clicked.connect(lambda: self.add_robot())
        self.layout_inspector.addWidget(self.button_add_robot)


def show_help(main_window):
    """Ouvre une pop_up Aide avec la contenu du fichier aide.txt"""
    aide = QMessageBox(main_window)
    aide.setWindowTitle("Aide")
    list_aide = []
    with open("aide.txt", encoding='utf-8') as f:
        for line in f:
            list_aide.append(line)
    aide.setText("".join(list_aide))
    aide.exec_()


def main(backend):
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Window(backend)
    sys.exit(app.exec_())
