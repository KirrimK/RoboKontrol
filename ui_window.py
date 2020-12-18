"""Module ui_window.py - Crée la fenêtre comportant l'inspecteur, la carte et d'autres fonctionnalités"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

import inspecteur


class Ui_window(object):
    def __init__(self, main_window, number_robots=0):
        main_window.setObjectName("main_window")
        main_window.resize(1091, 782)
        main_window.setWindowTitle("Form")
        self.number_robots = number_robots

        self.layout_window = QtWidgets.QVBoxLayout(main_window)

        self.menu_area = QtWidgets.QGroupBox(main_window)

        self.layout_menu = QtWidgets.QHBoxLayout(self.menu_area)

        self.button_map = QtWidgets.QPushButton(self.menu_area)
        self.button_map.setMaximumSize(QtCore.QSize(200, 16777215))
        self.button_map.setText("Configurer la carte")
        self.layout_menu.addWidget(self.button_map)

        self.button_connect_robot = QtWidgets.QPushButton(self.menu_area)
        self.button_connect_robot.setText("Connecter un robot")
        self.layout_menu.addWidget(self.button_connect_robot)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layout_menu.addItem(spacerItem)

        self.button_help = QtWidgets.QPushButton(self.menu_area)
        self.button_help.setText("Aide")
        self.layout_menu.addWidget(self.button_help)

        self.layout_window.addWidget(self.menu_area)

        self.layout_map_inspector = QtWidgets.QHBoxLayout()
        self.map_view = QtWidgets.QGraphicsView(main_window)     #TODO: intégrer la map de Jacques
        self.map_view.setMinimumSize(QtCore.QSize(0, 250))
        self.layout_map_inspector.addWidget(self.map_view)

        self.create_inspecteur_scrollbar(main_window)

        self.add_robot()

        self.inspector_scroll_area.setWidget(self.scrollArea)
        self.layout_map_inspector.addWidget(self.inspector_scroll_area)
        self.layout_window.addLayout(self.layout_map_inspector)

        QtCore.QMetaObject.connectSlotsByName(main_window)

        self.button_help.clicked.connect(lambda: show_help(main_window))

    def add_robot(self):
        self.boite_robot = inspecteur.BoiteRobot(self.scrollArea, self.layout_inspector, self.number_robots)
        self.boite_robot.add_box_robot()
        self.number_robots += 1

    def create_inspecteur_scrollbar(self, main_window):
        """Crée  la QScrollBar qui contient un QPushButton 'Ajouter' et auquel on ajoutera les boites (QGroupBox) robots """
        self.inspector_scroll_area = QtWidgets.QScrollArea(main_window)
        # self.inspector_scroll_area.setStyleSheet("background-color: deepskyblue")  #customisation de la boite robot(couleur fond)
        self.inspector_scroll_area.setMinimumSize(QtCore.QSize(350, 0))
        self.inspector_scroll_area.setMaximumSize(QtCore.QSize(350, 16777215))
        self.inspector_scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.inspector_scroll_area.setWidgetResizable(True)
        self.scrollArea = QtWidgets.QWidget()
        self.scrollArea.setGeometry(QtCore.QRect(0, 0, 333, 882))
        self.layout_inspector = QtWidgets.QVBoxLayout(self.scrollArea)

        """Crée le QPushButton et l'ajoute à la QScrollBar"""
        self.button_add_robot = QtWidgets.QPushButton(self.scrollArea)
        self.button_add_robot.setMinimumSize(QtCore.QSize(0, 30))
        self.button_add_robot.setText("Ajouter un robot")
        self.button_add_robot.clicked.connect(lambda: self.add_robot())
        self.layout_inspector.addWidget(self.button_add_robot)


def show_help(main_window):
    """Ouvre une pop_up Aide avec la contenu du fichier aide.txt"""
    aide = QMessageBox(main_window)
    aide.setWindowTitle("Aide")
    l = []
    with open("aide.txt", encoding='utf-8') as f:
        for line in f:
            l.append(line)
    aide.setText("".join(l))
    aide.exec_()


def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QWidget()
    Ui_window(main_window)
    main_window.show()
    sys.exit(app.exec_())


