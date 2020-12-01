"""Module annuaire.py - gestion et mise à jour des informations connues sur les robots trackés"""

from enum import Enum

class Variete(Enum):
    """Une simple énumération pour définir la façon dont l'inspecteur
    intéragira avec l'actionneur"""
    FIXE = 1 #aucun choix proposé, seulement un affichage de la présence de l'actionneur
    BINAIRE = 2 #uniquement deux états possibles: éteint ou activé
    DEROULANT = 3 #plusieurs choix possibles, affichés sous la forme d'un menu déroulant

class Actionneur:
    """Définit un actionneur attaché à un robot
    - nom (str): le nom de l'actionneur
    - etat (int): l'état actuel de l'actionneur (index dans la liste possibles)
    - possibles (list of str): la liste des états possibles
    - variete: indicateur de la façon dont l'actionneur doit être présenté
        dans l'inspecteur graphique"""
    def __init__(self, nom, etat, possibles):
        self.nom = nom
        self.etat = etat
        self.possibles = possibles
        if len(possibles) < 1:
            raise ValueError("La liste des possibles de {} ne peut être vide.".format(nom))
        if len(possibles) == 1:
            self.variete = Variete.FIXE
        elif len(possibles) == 2:
            self.variete = Variete.BINAIRE
        elif len(possibles) > 2:
            self.variete = Variete.DEROULANT

class Robot:
    """Classe définissant un robot avec les attributs suivants:
    - id (str): le nom du robot
    - x (float): la position selon l'axe x du robot sur la carte (en mm)
    - y (float): la position selon l'axe x du robot sur la carte (en mm)
    - theta (float): l'orientation du robot (en radians/sens trigo depuis axe x)
    - actionneurs ():
    """
    def __init__(self, rid, x=1500, y=1000, theta=0, actionneurs=None):
        self.rid = rid
        #position par défaut
        self.x = x
        self.y = y
        self.theta = theta
        self.actionneurs = {}
        if actionneurs is not None:
            for actionneur in actionneurs:
                self.updt_act(actionneur)

    def get_pos(self):
        """Récupère la position du robot sous la forme
        (x, y, theta)"""
        return (self.x, self.y, self.theta)

    def set_pos(self, x, y, theta):
        """Met à jour la position (x, y, theta) du robot"""
        self.x = x
        self.y = y
        self.theta = theta

    def updt_act(self, actionneur):
        """Ajoute/met à jour un actionneur du robot"""
        self.actionneurs[actionneur.nom] = actionneur

    def remove_act(self, act_name):
        """Enlève un actionneur repéré par son nom du robot"""
        self.actionneurs.pop(act_name, None)

    def get_state_act(self, act_name):
        """Retourne l'état et les possibles d'un actionneur"""
        etat = self.actionneurs[act_name].etat
        possibles = self.actionneurs[act_name].possibles
        return (etat, possibles)

    def set_state_act(self, act_name, etat):
        """Change l'état d'un actionneur"""
        if etat < len(self.actionneurs[act_name].possibles):
            self.actionneurs[act_name].etat = etat
        else:
            print("L'état {} n'est pas possible pour l'actionneur {}".format(str(etat), act_name))

    def get_variete(self, act_name):
        """Retourne la variété d'un actionneur"""
        return self.actionneurs[act_name].variete


class Annuaire:
    """Classe définissant un espace ou toutes les informations sur les robots trackés
    sont centralisées"""
    def __init__(self):
        self.robots = {}

    def check_robot(self, rid):
        """Vérifie si un robot est dans l'annuaire"""
        presence = rid in self.robots
        if not presence:
            print("Le robot {} n'est pas dans l'annuaire.".format(rid))
        return presence

    def add_robot(self, robot):
        """Ajoute un robot à l'annuaire"""
        self.robots[robot.rid] = robot

    def remove_robot(self, robot):
        """Enlève un robot de l'annuaire"""
        self.robots.pop(robot.rid, None)

    def get_robotpos(self, rid):
        """Récupère la position d'un robot dans l'annuaire"""
        if rid in self.robots:
            return self.robots[rid].get_pos()
        else:
            print("Le robot {} n'est pas dans l'annuaire.".format(rid))

    def set_robotpos(self, rid, x, y, theta):
        """Met à jour la position d'un robot dans l'annuaire"""
        if rid in self.robots:
            self.robots[rid].set_pos(x, y, theta)
        else:
            print("Le robot {} n'est pas dans l'annuaire.".format(rid))

    def updt_robotact(self, rid, actionneur):
        """Ajoute/met à jour un actionneur
        sur un robot présent dans l'annuaire"""
        if rid in self.robots:
            self.robots[rid].updt_act(actionneur)
        else:
            print("Le robot {} n'est pas dans l'annuaire.".format(rid))

    def remove_robotact(self, rid, act_name):
        """Enlève un actionneur repéré par son nom d'un robot présent dans l'annuaire"""
        if rid in self.robots:
            self.robots[rid].remove_act(act_name)
        else:
            print("Le robot {} n'est pas dans l'annuaire.".format(rid))

    def get_robotact_state(self, rid, act_name):
        """Retourne l'état et les possibles d'un actionneur
        monté sur un robot dans l'annuaire"""
        if self.check_robot(rid):
            self.robots[rid].get_state_act(act_name)

    def set_robotact_state(self, rid, act_name, etat):
        """Change l'état d'un actionneur monté sur un robot"""
        if self.check_robot(rid):
            self.robots[rid].set_state_act(act_name, etat)

    def get_robot_act_variete(self, rid, act_name):
        """Retourne la variété d'un actionneur monté sur un robot"""
        if self.check_robot(rid):
            self.robots[rid].get_variete(act_name)
