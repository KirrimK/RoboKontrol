"""Module annuaire.py - gestion et mise à jour des informations connues sur les robots trackés"""

class Actionneur:
    """Classe définissant un actionneur avec les attributs suivants:
    - nom (str): le nom de l'actionneur
    - etats_possibles (list of str): liste des états possibles pour l'actionneur
    - etat_actuel (int): index de l'état actuel de l'actionneur dans la liste
    - type_sel (str): définit la manière dont les états sont sélectionnables dans l'interface
            #TODO: une énumération serait-elle plus pratique? à voir plus tard
    """
    def __init__(self, nom, etats_possibles, etat_actuel, type_sel):
        self.nom = nom
        self.etats_possibles = etats_possibles
        self.etat_actuel = etat_actuel
        self.type_sel = type_sel

class Robot:
    """Classe définissant un robot avec les attributs suivants:
    - id (str): le nom du robot
    - actionneurs (list of Actionneur): liste des actionneurs installés sur le robot
    - x (float): la position selon l'axe x du robot sur la carte (en mm)
    - y (float): la position selon l'axe x du robot sur la carte (en mm)
    - theta (float): l'orientation du robot (en radians/sens trigo depuis axe x)
    """
    def __init__(self, robotId, actionneurs):
        self.robotId = robotId
        self.actionneurs = actionneurs
        #position par défaut
        self.x = 1500
        self.y = 1000
        self.theta = 0


class Annuaire:
    """docstring"""
    def __init__(self):
        pass

    def get_robotpos(self, robot_id):
        pass

    def set_robotpos(self, robot_id, x, y, theta):
        pass
