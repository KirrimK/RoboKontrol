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

    def __str__(self):
        nom = self.nom
        vrt = str(self.variete)
        eta = str(self.etat)
        enb = self.possibles[self.etat]
        psb = self.possibles
        lps = str(len(self.possibles))
        return "Act.[{}] Var.: {} Etat: ({}) {} / {} états: {}".format(nom, vrt, eta, enb, lps, psb)

    def get_state(self):
        """Retourne l'état et les possibles d'un actionneur"""
        return (self.etat, self.possibles)

    def set_state(self, etat):
        """Change l'état d'un actionneur"""
        if etat < len(self.possibles):
            self.etat = etat
        else:
            print("L'état {} n'est pas possible pour l'actionneur {}".format(str(etat), self.nom))

    def get_variete(self):
        """Retourne la variété d'un actionneur"""
        return self.variete

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

    def __str__(self):
        repr_str = "Robot [{}]\n".format(self.rid)
        x = str(self.x)
        y = str(self.y)
        theta = str(self.theta)
        repr_str += "| Position: x:{} y:{} theta:{}\n".format(x, y, theta)
        for act in self.actionneurs:
            repr_str += "| {}\n".format(str(self.actionneurs[act]))
        return repr_str

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

    def get_all_act(self):
        """Retourne la liste de tous les actionneurs sur le robot"""
        return list(self.actionneurs.keys())

    def get_state_act(self, act_name):
        """Retourne l'état et les possibles d'un actionneur"""
        return self.actionneurs[act_name].get_state()

    def set_state_act(self, act_name, etat):
        """Change l'état d'un actionneur"""
        self.actionneurs[act_name].set_state(etat)

    def get_variete_act(self, act_name):
        """Retourne la variété d'un actionneur"""
        return self.actionneurs[act_name].get_variete()


class Annuaire:
    """Classe définissant un espace ou toutes les informations sur les robots trackés
    sont centralisées"""
    def __init__(self):
        self.robots = {}

    def __str__(self):
        repr_str = "Annuaire:\n"
        for robot in self.robots:
            repr_str += str(self.robots[robot])
        return repr_str

    def check_robot(self, rid):
        """Vérifie si un robot est dans l'annuaire"""
        return rid in self.robots

    def add_robot(self, robot):
        """Ajoute un robot à l'annuaire"""
        self.robots[robot.rid] = robot

    def remove_robot(self, robot):
        """Enlève un robot de l'annuaire"""
        self.robots.pop(robot.rid, None)

    def get_robot_pos(self, rid):
        """Récupère la position d'un robot dans l'annuaire"""
        if self.check_robot(rid):
            return self.robots[rid].get_pos()

    def set_robot_pos(self, rid, x, y, theta):
        """Met à jour la position d'un robot dans l'annuaire"""
        if self.check_robot(rid):
            self.robots[rid].set_pos(x, y, theta)

    def updt_robot_act(self, rid, actionneur):
        """Ajoute/met à jour la disposition d'un actionneur
        sur un robot présent dans l'annuaire (ne pas utiliser pour mettre l'état à jour)"""
        if self.check_robot(rid):
            self.robots[rid].updt_act(actionneur)

    def remove_robot_act(self, rid, act_name):
        """Enlève un actionneur repéré par son nom d'un robot présent dans l'annuaire"""
        if self.check_robot(rid):
            self.robots[rid].remove_act(act_name)

    def get_robot_act_state(self, rid, act_name):
        """Retourne l'état et les possibles d'un actionneur
        monté sur un robot dans l'annuaire"""
        if self.check_robot(rid):
            return self.robots[rid].get_state_act(act_name)

    def set_robot_act_state(self, rid, act_name, etat):
        """Change l'état d'un actionneur monté sur un robot"""
        if self.check_robot(rid):
            self.robots[rid].set_state_act(act_name, etat)

    def get_robot_act_variete(self, rid, act_name):
        """Retourne la variété d'un actionneur monté sur un robot"""
        if self.check_robot(rid):
            return self.robots[rid].get_variete_act(act_name)

    def get_robot_all_act(self, rid):
        """Retourne la liste de tous les actionneurs d'un robot"""
        return self.robots[rid].get_all_act()

    def get_all_robots(self):
        """Retourne la liste de tous les robotids des robots présents dans l'annuaire"""
        return list(self.robots.keys())
