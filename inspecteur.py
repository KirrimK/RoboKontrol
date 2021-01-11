""" Module inspecteur.py - Récupère les données sur les robots et effectue les mise à jour """

import boite_robot
from PyQt5 import QtWidgets, QtCore


class Inspecteur(QtWidgets.QWidget):
    """ Définit l'objet inspecteur qui comport les boites robots et qui les relie à backend avec des signaux """

    def __init__(self, parent_widget, parent_layout, main_window, backend):
        super(Inspecteur, self).__init__()
        self.backend = backend
        self.main_window = main_window
        self.widget_parent = parent_widget
        self.layout_parent = parent_layout

        # Création de la liste des noms des robots présents
        self.current_robots_list = []
        # Création du dictionnaire des robots présents (k=nom, v=boite robot)
        self.current_robots_dic = {}

        # Création d'un timer
        self.timer = QtCore.QTimer(self.main_window)
        # Connexion de ce timer au slot de mise à jour des robots
        self.timer.timeout.connect(self.update_robot)
        # Définit la période temporelle (en ms) associée a la fréquence de mise à jour du timer
        self.timer.start(400)

    @QtCore.pyqtSlot()
    def update_robot(self):
        """ Met à jour la liste des robots présents et initialise la mise à jour de toutes les boites robots """

        new_robots = self.backend.get_all_robots()

        # Ajoute les nouveaux robots
        for robot in set(new_robots) - set(self.current_robots_list):
            self.add_robot(robot)

        # Supprime les robots qui ne sont plus présents
        for robot in set(self.current_robots_list) - set(new_robots):
            self.remove_robot(robot)

        # Met à jour la liste des robots présents
        self.current_robots_list = new_robots

        # Initialise la mise à jours des robots
        for k, v in self.current_robots_dic.items():
            v.update_boite_robot()

    def add_robot(self, nom_robot):
        """ Ajoute le robot dont le nom est placé en paramètre sous forme d'une boite robot dans la zone inspecteur """
        self.boite_robot = boite_robot.BoiteRobot(self.widget_parent, self.layout_parent, str(nom_robot), self)
        self.current_robots_dic[self.boite_robot.rid] = self.boite_robot

    def remove_robot(self, nom_robot):
        """ Supprime de l'inspecteur la boite robot associée au robot dont le nom est placé en paramètre """
        deleted_robot = self.current_robots_dic.pop(nom_robot)
        deleted_robot.remove_box_robot()
        # Envoie l'information que le robot a été supprimé (via le bouton supprimer)
        self.backend.stopandforget_robot(nom_robot)
