"""Module annuaire.py - gestion et mise à jour des informations connues sur les robots trackés"""

import time

class Equipement:
    """Définit un équipement branché sur le robot

    Attributs:
    - nom (str): le nom de l'équipement
    - unite (str): unite dans laquelle les valeurs sont exprimées (non utilisé ici)
    - last_updt (float): timestamp de la derniere mise à jour de la valeur"""
    def __init__(self, nom):
        self.nom = nom
        self.last_updt = time.time()
        self.unite = None

    def updt(self):
        """Met à jour le timestamp de la dernière mise à jour"""
        self.last_updt = time.time()

    def set_state(self, valeur):
        """Non utilisé ici, mais implémenté pour robustesse

        Entrée:
        - valeur (inutilisé)

        Sortie:
        - None
        """
        return None

    def get_state(self):
        """Non utilisé ici, mais implémenté pour robustesse

        Sortie:
        - None
        """
        return None

    def get_unit(self):
        """Retourne l'unité de l'équipement

        Sortie:
        - unite (str)
        """
        return self.unite

    def get_last_updt(self):
        """Retourne le timestamp de la dernière mise à jour

        Sortie:
        - last_updt (float)
        """
        return self.last_updt

#TODO: rajouter un step aux actionneurs standards
class Actionneur(Equipement):
    """Définit un actionneur basique attaché à un robot,
    pouvant prendre une valeur (int) entre max et min (int), le tout dans une certaine unité

    Attributs:
    Hérités d'Equipement
    - nom (str): le nom de l'actionneur
    - unite (str): l'unité dans laquelle les valeurs de l'actionneurs sont exprimées
    - last_updt (float): timestamp de la derniere update de la valeur

    Nouveaux:
    - valeur (int): valeur imposée à l'actionneur (compris entre min et max)
    - min_val (int): valeur minimale prise par l'actionneur
    - max_val (int): valeur max prise par l'actionneur
    """
    def __init__(self, nom, valeur, min_val, max_val, unite=None):
        super().__init__(nom)
        self.valeur = valeur
        self.min_val = min_val
        self.max_val = max_val
        self.unite = unite

    def __str__(self):
        nom = self.nom
        val = self.valeur
        min_v = self.min_val
        max_v = self.max_val
        unite = self.unite
        return "Actionneur [{}] Val.: {} ({}) entre {} et {}".format(nom, val, unite, min_v, max_v)

    def get_state(self):
        """Retourne la valeur et le min/max d'un actionneur

        Sortie:
        - state (int, int, int)
            - [0]: valeur de l'actionneur
            - [1]: valeur min
            - [2]: valeur max
        """
        return (self.valeur, self.min_val, self.max_val)

    def set_state(self, valeur):
        """Change la valeur de l'actionneur

        Entrée:
        - valeur (int) (devrait être compris entre min et max actionneur inclus)
        """
        if self.min_val <= valeur <= self.max_val:
            self.valeur = valeur
            self.updt()

class Capteur(Equipement):
    """Définit un capteur avec un nom, une valeur et une unité

    Attributs:
    Hérités d'Equipement
    - nom (str): le nom du capteur
    - unite (str): unité du capteur
    - last_updt (float): timestamp de la derniere update de la valeur

    Nouveaux:
    - valeur (int): valeur du capteur"""
    def __init__(self, nom, valeur, unite=None):
        super().__init__(nom)
        self.valeur = valeur
        self.unite = unite

    def __str__(self):
        nom = self.nom
        val = self.valeur
        unite = self.unite
        return "Capteur [{}] Val.:{} ({})".format(nom, val, unite)

    def get_state(self):
        """Renvoie la valeur du capteur

        Sortie:
        - valeur (int)"""
        return self.valeur

    def set_state(self, valeur):
        """Change la valeur du capteur

        Entrée:
        - valeur (int)"""
        self.valeur = valeur
        self.updt()

class ActioCapteur(Equipement):
    """Définit un actionneur basique couplé à un capteur, possédant la même unité,
    et le capteur mesurant une valeur supposément régie par l'actionneur

    Attributs:
    Hérités d'Equipement
    - nom (str): le nom de l'ensemble
    - unite (str): l'unité commune (remplace les unités des actionneurs)
    - last_updt (float): timestamp de la derniere update de la valeur

    Nouveaux:
    - actionneur (Equipement): l'actionneur à relier (pas besoin de préciser l'unité)
    - capteur (Equipement): le capteur à relier (pas besoin de préciser l'unité)
    """
    def __init__(self, nom, actionneur, capteur, unite_cmn):
        super().__init__(nom)
        self.actionneur = actionneur
        self.capteur = capteur
        self.unite = unite_cmn

    def __str__(self):
        nom = self.nom
        unt = self.unite
        cpt = self.capteur.valeur
        act = self.actionneur.valeur
        mnv = self.actionneur.min_val
        mxv = self.actionneur.max_val
        return "ActCpt [{}]({}) Cpt: {} Act: {} entre {} et {}".format(nom, unt, cpt, act, mnv, mxv)

    def set_state(self, valeur):
        """Met à jour la valeur de l'un des composants

        Entrée:
        - valeur (int, int)
            - [0]: valeur de l'actionneur (None pour ne pas changer)
            - [1]: valeur du capteur (None pour ne pas changer)
        """
        if valeur[0] is not None:
            self.actionneur.set_state(valeur[0])
            self.capteur.updt()
        if valeur[1] is not None:
            self.capteur.set_state(valeur[1])
            self.capteur.updt()

    def get_state(self):
        """Retourne la valeur de l'actionneur, son min, max et la valeur du capteur

        Sortie:
        - state (int, int, int, int)
            - [0]: valeur de l'actionneur
            - [1]: min actionneur
            - [2]: max actionneur
            - [3]: valeur capteur
        """
        a_vl, a_mn, a_mx = self.actionneur.get_state()
        return (a_vl, a_mn, a_mx, self.capteur.get_state())

    def get_last_updt(self):
        """Retourne les dernières actualisations de l'actionneur et du capteur

        Sortie:
        - (float, float)
            - [0]: last_updt actionneur
            - [1]: last_updt capteur
        """
        return (self.actionneur.last_updt, self.actionneur.last_updt)

class Robot:
    """Classe définissant un robot avec les attributs suivants:

    Attributs:
    - id (str): le nom du robot
    - x (float): la position selon l'axe x du robot sur la carte (en mm)
    - y (float): la position selon l'axe x du robot sur la carte (en mm)
    - theta (float): l'orientation du robot (en radians/sens trigo depuis axe x)
    - equipements (dict): liste des équipements connectés au robot
        - clé: nom (str)
        - valeur: equipement (Equipement)

    (passer les equipements lors de la construction sous forme de list)
    """
    def __init__(self, rid, x=1500, y=1000, theta=0, equipements=None):
        self.rid = rid
        #position par défaut
        self.x = x
        self.y = y
        self.theta = theta
        self.equipements = {}
        if equipements is not None:
            for equipement in equipements:
                self.updt_eqp(equipement)
        self.last_updt_pos = time.time()

    def __str__(self):
        repr_str = "Robot [{}]\n".format(self.rid)
        pos_x = str(self.x)
        pos_y = str(self.y)
        theta = str(self.theta)
        repr_str += "| Position: x:{} y:{} theta:{}\n".format(pos_x, pos_y, theta)
        for eqp in self.equipements:
            repr_str += "| {}\n".format(str(self.equipements[eqp]))
        return repr_str

    def get_pos(self):
        """Récupère la position du robot

        Sortie:
        - (float, float, float):
            - [0]: x
            - [1]: y
            - [2]: theta
        """
        return (self.x, self.y, self.theta)

    def set_pos(self, x, y, theta):
        """Met à jour la position du robot

        Entrée:
        - x (float)
        - y (float)
        - theta (float)
        """
        self.x = x
        self.y = y
        self.theta = theta
        self.last_updt_pos = time.time()

    def check_eqp(self, eqp_name):
        """Verifie si un équipement est rattaché au robot

        Sortie:
        - bool
        """
        return eqp_name in self.get_all_eqp()

    def updt_eqp(self, equipement):
        """Ajoute/met à jour un actionneur du robot

        Entrée:
        - equipement (Equipement)
        """
        self.equipements[equipement.nom] = equipement

    def remove_eqp(self, eqp_name):
        """Enlève un équipement repéré par son nom du robot

        Entrée:
        - eqp_name (str)"""
        self.equipements.pop(eqp_name, None)

    def get_all_eqp(self):
        """Retourne la liste de tous les équipements sur le robot

        Sortie:
        - list of (str): liste des noms des équipements"""
        return list(self.equipements.keys())

    def get_state_eqp(self, eqp_name):
        """Retourne la valeur d'un équipement (et autres informations le cas échéant)

        Sortie: dépend du type de l'équipement portant le nom eqp_name

        > Equipement:
        - None

        > Capteur:
        - int (Se référer à Capteur.get_state())

        > Actionneur:
        - (int, int, int) (Se référer à Actionneur.get_state())

        > ActioCapteur:
        - (int, int, int, int) (Se référer à ActioCapteur.get_state())
        """
        return self.equipements[eqp_name].get_state()

    def set_state_eqp(self, eqp_name, valeur):
        """Change la valeur d'un équipement

        Entrée: dépend du type de l'équipement portant le nom eqp_name
        > Equipement:
            - non utilisé, passer None
        > Capteur:
            - int (Se référer à Capteur.set_state()
        > Actionneur:
            - int (Se référer à Actionneur.set_state()
        > ActioCapteur:
            - (int, int) (Se référer à ActioCapteur.set_state())
        """
        if self.check_eqp(eqp_name):
            self.equipements[eqp_name].set_state(valeur)

    def get_type_eqp(self, eqp_name):
        """Retourne le type d'un équipement

        Sortie:
        - type (Type)"""
        if self.check_eqp(eqp_name):
            return type(self.equipements[eqp_name])
        return None

    def get_unit_eqp(self, eqp_name):
        """Retourne l'unité d'un équipement

        Sortie:
        - unite (str)"""
        return self.equipements[eqp_name].get_unit()

    def get_last_updt_pos(self):
        """Retourne la dernière mise à jour de la position

        Sortie:
            - last_updt_pos (float)
        """
        return self.last_updt_pos

    def get_last_updt_eqp(self, eqp_name):
        """Retourne la dernière mise à jour de la position

        Sortie:
            - last_updt_pos (float)
        """
        return self.equipements[eqp_name].get_last_updt()

class Annuaire:
    """Classe définissant un espace ou toutes les informations sur les robots trackés
    sont centralisées

    Attributs:
    - robots (dict): dictionnaire contenant tous les objets Robot gardés en mémoire
        - clé: nom (str)
        - valeur: robot (Robot)
    """
    def __init__(self):
        self.robots = {}

    def __str__(self):
        repr_str = "Annuaire:\n"
        for robot in self.robots:
            repr_str += str(self.robots[robot])
        return repr_str

    def check_robot(self, rid):
        """Vérifie si un robot est dans l'annuaire

        Sortie:
        - bool"""
        return rid in self.robots

    def add_robot(self, robot):
        """Ajoute un robot à l'annuaire

        Entrée:
        - robot (Robot)"""
        self.robots[robot.rid] = robot

    def remove_robot(self, rid):
        """Enlève un robot de l'annuaire

        Entrée:
        - rid (str)
        """
        self.robots.pop(rid, None)

    def get_robot_pos(self, rid):
        """Récupère la position d'un robot stocké dans l'annuaire

        Entrée:
        - rid (str)

        Sortie:
        - (float, float, float)
            - [0]: x
            - [1]: y
            - [2]: theta
        """
        if self.check_robot(rid):
            return self.robots[rid].get_pos()
        return None

    def set_robot_pos(self, rid, x, y, theta):
        """Met à jour la position d'un robot dans l'annuaire

        Entrée:
        - rid (str)
        - x (float)
        - y (float)
        - theta (float)
        """
        if self.check_robot(rid):
            self.robots[rid].set_pos(x, y, theta)

    def updt_robot_eqp(self, rid, equipement):
        """Ajoute/met à jour la disposition d'un équipement
        sur un robot présent dans l'annuaire (ne pas utiliser pour mettre la valeur à jour)

        Entrée:
        - rid (str)
        - equipement (Equipement)
        """
        if self.check_robot(rid):
            self.robots[rid].updt_eqp(equipement)

    def remove_robot_eqp(self, rid, eqp_name):
        """Enlève un équipement repéré par son nom d'un robot présent dans l'annuaire

        Entrée:
        - rid (str)
        - eqp_name (str)
        """
        if self.check_robot(rid):
            self.robots[rid].remove_eqp(eqp_name)

    def get_robot_eqp_state(self, rid, eqp_name):
        """Retourne l'état et les possibles d'un équipement
        monté sur un robot dans l'annuaire

        Entrée:
        - rid (str)
        - eqp_name (str)

        Sortie:
            (Se référer à Robot.get_state_eqp())"""
        if self.check_robot(rid):
            return self.robots[rid].get_state_eqp(eqp_name)
        return None

    def set_robot_eqp_state(self, rid, eqp_name, valeur):
        """Change l'état d'un équipement monté sur un robot

        Entrée:
        - rid (str)
        - eqp_name (str)
        - valeur (Se référer à Robot.set_state_eqp())
        """
        if self.check_robot(rid):
            self.robots[rid].set_state_eqp(eqp_name, valeur)

    def get_robot_eqp_type(self, rid, eqp_name):
        """Retourne la variété d'un équipement monté sur un robot

        Entrée:
        - rid (str)
        - eqp_name (str)

        Sortie:
        - (Se référer à Robot.get_type_eqp())
        """
        if self.check_robot(rid):
            return self.robots[rid].get_type_eqp(eqp_name)
        return None

    def get_robot_eqp_unit(self, rid, eqp_name):
        """Retourne l'unité d'un équipement monté sur un robot

        Entrée:
        - rid (str)
        - eqp_name (str)

        Sortie:
        - (Se référer à Robot.get_unit_eqp())
        """
        if self.check_robot(rid):
            return self.robots[rid].get_unit_eqp(eqp_name)
        return None

    def get_robot_all_eqp(self, rid):
        """Retourne la liste de tous les équipements d'un robot

        Entrée:
        - rid (str)

        Sortie:
        - (Se réferer à Robot.get_all_eqp())
        """
        return self.robots[rid].get_all_eqp()

    def get_all_robots(self):
        """Retourne la liste de tous les robotids des robots présents dans l'annuaire

        Sortie:
        - list of (str)
        """
        return list(self.robots.keys())

    def check_robot_eqp(self, robot_name, eqp_name):
        """Vérifie si un équipement est présent sur un robot

        Entrée:
            - robot_name (str): nom du robot
            - eqp_name (str): nom de l'équipement
        Sortie:
            - bool
        """
        if self.check_robot(robot_name):
            return self.robots[robot_name].check_eqp(eqp_name)
        return False

    def get_robot_eqp_last_updt(self, robot_name, eqp_name):
        """Retourne le timestamp de la dernière mise à jour de l'équipement"""
        if self.check_robot_eqp(robot_name, eqp_name):
            return self.robots[robot_name].get_last_updt_eqp()

    def get_robot_last_updt_pos(self, robot_name):
        """Retourne le timestamp de la dernière mise à jour de positions"""
        if self.check_robot(robot_name):
            return self.robots[robot_name].get_last_updt_pos()

#TODO: ajouter plus de features recommandées
