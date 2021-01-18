""" inspecteur.py - Définit l'affichage de l'inspecteur contenant les infomations des robots"""

from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from tab_robot import TabRobot


class Inspecteur(QTabWidget):
    """ Définit l'objet inspecteur (QTabWidget) qui comport les onglets robots (QGroupBox)
    et qui les relie à backend avec des signaux """

    def __init__(self, window):
        super().__init__()
        self.window = window

        # Connexion du signal du clique droit sur robot avec la sélection de l'onglet robot
        self.window.map_view.selected_robot_signal.connect(lambda rid: self.setCurrentWidget(self.window.current_robots_dic[rid]))

        self.ui_setup_tab()

    def update_selected_robot(self, rid):
        self.window.map_view.selected_robot = rid

    def ui_setup_tab(self):
        """ Configure l'inspecteur"""
        self.setMaximumSize(440, 16777215)
        self.setMovable(True)

    @pyqtSlot()
    def update_robots(self, new_robots):
        """ Met à jour la liste des robots présents et initialise la mise à jour de toutes les boites robots """

        # Ajoute les nouveaux robots
        for rid in set(new_robots) - set(self.window.current_robots_list):
            self.add_robot(rid)

        # Met à jour la liste des robots présents
        self.window.current_robots_list = new_robots

        # Initialise la mise à jours des robots
        for tab in self.window.current_robots_dic.values():
            tab.update_tab_robot()

        # Emission du signal de l'onglet sélectionné
        if self.window.current_robots_dic:
            self.window.map_view.selected_robot_signal.emit(self.currentWidget().rid)

    def add_robot(self, rid):
        """ Ajoute le robot dont le nom est placé en paramètre sous forme d'une boite robot dans la zone inspecteur """

        # Création d'un onglet robot
        self.tab_robot = TabRobot(rid, self.window)
        self.window.current_robots_dic[rid] = self.tab_robot

        # Ajout de l'onglet à l'inspecteur
        self.addTab(self.tab_robot, rid)

    @pyqtSlot()
    def remove_robot(self, rid):
        """ Supprime de l'inspecteur la boite robot associée au robot dont le nom est placé en paramètre """

        # Retire l'onglet actuellement sélectionnée
        self.removeTab(self.currentIndex())
        # Cache l'affichage de l'onglet du robot
        self.window.current_robots_dic.pop(rid).hide()
        # Envoie l'information que le robot a été supprimé (via le bouton supprimer)
        self.window.backend.stopandforget_robot(rid)
