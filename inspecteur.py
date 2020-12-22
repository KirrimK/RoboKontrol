import backend
import boite_robot
from PyQt5 import QtWidgets, QtCore
import time


class Inspecteur(QtWidgets.QWidget):
    """Définit l'objet inspecteur qui comport les boites robots et qui les relie à backend avec des signaux"""

    # Création d'un signal qui sera émit lorsque la liste des robots à changé
    robot_list_updated_signal = QtCore.pyqtSlot(list)

    # actionneur_list_changed_signal = QtCore.pyqtSignal(list)
    # capteur_list_changed_signal = QtCore.pyqtSignal(list)

    def __init__(self, parent_widget, parent_layout, main_window, backend):
        super(Inspecteur, self).__init__()
        self.backend = backend
        self.main_window = main_window
        self.widget_parent = parent_widget
        self.layout_parent = parent_layout

        # Dictionnaire des robots présents (k=nom, v=boite robot)
        self.current_robots_dic = {}
        # Création de l'objet Backend
        # Création et récupération de la liste actuelle des noms des robots présents
        self.current_robots_list = self.backend.get_all_robots()

        # Connexion du signal mise à jour des robots avec la comande pour mettre à jour l'affichage des robots



    @QtCore.pyqtSlot()
    def update_robot(self):
        """Met à jour la liste des robots présents et envoie un signal de mise à jour des robots (cf appliaction airport PSI)"""

        new_robots = self.backend.get_all_robots()
        # Ajoute les nouveaux robots
        for robot in set(new_robots) - set(self.current_robots_list):
            print(type(robot))
            self.add_robot(robot)
        # Supprime les robots qui ne sont plus présents
        for robot in set(self.current_robots_list) - set(new_robots):
            self.remove_robot(robot)
        self.current_robots_list = new_robots
        # Actualise la position des robots (k=nom robot, v = boite robot)
        for k, v in self.current_robots_dic.items():
            v.update_position(k)

        # Emet un signal de mise à jour de la liste des robots
        # self.boite_robot.robot_list_updated_signal.emit(self.current_robots_list)

    @QtCore.pyqtSlot(str)
    def add_robot(self, nom_robot):
        self.boite_robot = boite_robot.BoiteRobot(self.widget_parent, self.layout_parent, str(nom_robot), self)
        self.boite_robot.create_boite_robot()
        self.current_robots_dic[self.boite_robot.rid] = self.boite_robot

    @QtCore.pyqtSlot(str)
    def remove_robot(self, nom_robot):
        deleted_robot = self.current_robots_dic.pop(nom_robot)
        deleted_robot.remove_box_robot()
