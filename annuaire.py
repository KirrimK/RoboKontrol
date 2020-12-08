"""Module annuaire.py - gestion et mise à jour des informations connues sur les robots trackés"""

import time

class Equipement:
    """Définit un équipement branché sur le robot
    - nom (str): le nom de l'équipement
    - last_updt (float): timestamp de la derniere update de la valeur"""
    def __init__(self, nom):
        self.nom = nom
        self.last_updt = time.time()

    def updt(self):
        """Met à jour le timestamp de la dernière update"""
        self.last_updt = time.time()

class Actionneur(Equipement):
    """Définit un actionneur basique attaché à un robot,
    pouvant prendre une valeur (int) entre max et min (int), le tout dans une certaine unité

    - nom (str): le nom de l'actionneur
    - valeur (int): l'état actuel de l'actionneur (compris entre min et max)
    - min (int): valeur minimale prise par l'actionneur
    - max (int): valeur max prise par l'actionneur
    - unite (str): l'unité dans laquelle les valeurs de l'actionneurs sont exprimées
    - last_updt (float): timestamp de la derniere update de la valeur
    """
    def __init__(self, nom, valeur, min_val, max_val, unite):
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
        """Retourne la valeur et le min/max d'un actionneur"""
        return (self.valeur, self.min_val, self.max_val)

    def set_state(self, valeur):
        """Change la valeur de l'actionneur"""
        if self.min_val <= valeur <= self.max_val:
            self.valeur = valeur
            self.updt()

    def get_unit(self):
        """Renvoie l'unité de l'actionneur"""
        return self.unite

class Capteur(Equipement):
    """Définit un capteur avec un nom, une valeur et une unité
    - nom (str): le nom du capteur
    - valeur (int): valeur du capteur
    - unite (str): unité du capteur
    - last_updt (float): timestamp de la derniere update de la valeur"""
    def __init__(self, nom, valeur, unite):
        super().__init__(nom)
        self.valeur = valeur
        self.unite = unite

    def get_unit(self):
        """Renvoie l'unité du capteur"""
        return self.unite

    def get_state(self):
        """Renvoie la valeur du capteur"""
        return self.valeur

    def set_state(self, valeur):
        """Change la valeur du capteur"""
        self.valeur = valeur
        self.updt()

class Robot:
    """Classe définissant un robot avec les attributs suivants:
    - id (str): le nom du robot
    - x (float): la position selon l'axe x du robot sur la carte (en mm)
    - y (float): la position selon l'axe x du robot sur la carte (en mm)
    - theta (float): l'orientation du robot (en radians/sens trigo depuis axe x)
    - modules (list of Equipement): liste des équipements connectés au robot
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
        x = str(self.x)
        y = str(self.y)
        theta = str(self.theta)
        repr_str += "| Position: x:{} y:{} theta:{}\n".format(x, y, theta)
        for eqp in self.equipements:
            repr_str += "| {}\n".format(str(self.equipements[eqp]))
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
        self.last_updt_pos = time.time()

    def check_eqp(self, eqp_name):
        """Verifie si un équipement est rattaché au robot"""
        return eqp_name in self.get_all_eqp()

    def updt_eqp(self, equipement):
        """Ajoute/met à jour un actionneur du robot"""
        self.equipements[equipement.nom] = equipement

    def remove_eqp(self, eqp_name):
        """Enlève un équipement repéré par son nom du robot"""
        self.equipements.pop(eqp_name, None)

    def get_all_eqp(self):
        """Retourne la liste de tous les équipements sur le robot"""
        return list(self.equipements.keys())

    def get_state_eqp(self, eqp_name):
        """Retourne la valeur d'un équipement (et autres informations le cas échéant)"""
        if self.check_eqp(eqp_name) and self.get_type_eqp(eqp_name) is not Equipement:
            return self.equipements[eqp_name].get_state()

    def set_state_eqp(self, eqp_name, valeur):
        """Change la valeur d'un équipement"""
        if self.check_eqp(eqp_name) and self.get_type_eqp(eqp_name) is not Equipement:
            self.equipements[eqp_name].set_state(valeur)

    def get_type_eqp(self, eqp_name):
        """Retourne le type d'un équipement"""
        if self.check_eqp(eqp_name):
            return type(self.equipements[eqp_name])

    def get_unit_eqp(self, eqp_name):
        """Retourne l'unité d'un équipement"""
        if self.check_eqp(eqp_name) and self.get_type_eqp(eqp_name) is not Equipement:
            return self.equipements[eqp_name].get_unit()

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

    def updt_robot_eqp(self, rid, equipement):
        """Ajoute/met à jour la disposition d'un équipement
        sur un robot présent dans l'annuaire (ne pas utiliser pour mettre la valeur à jour)"""
        if self.check_robot(rid):
            self.robots[rid].updt_eqp(equipement)

    def remove_robot_eqp(self, rid, eqp_name):
        """Enlève un équipement repéré par son nom d'un robot présent dans l'annuaire"""
        if self.check_robot(rid):
            self.robots[rid].remove_eqp(eqp_name)

    def get_robot_eqp_state(self, rid, eqp_name):
        """Retourne l'état et les possibles d'un équipement
        monté sur un robot dans l'annuaire"""
        if self.check_robot(rid):
            return self.robots[rid].get_state_eqp(eqp_name)

    def set_robot_eqp_state(self, rid, eqp_name, valeur):
        """Change l'état d'un équipement monté sur un robot"""
        if self.check_robot(rid):
            self.robots[rid].set_state_eqp(eqp_name, valeur)

    def get_robot_eqp_type(self, rid, eqp_name):
        """Retourne la variété d'un équipement monté sur un robot"""
        if self.check_robot(rid):
            return self.robots[rid].get_type_eqp(eqp_name)

    def get_robot_eqp_unit(self, rid, eqp_name):
        """Retourne l'unité d'un équipement monté sur un robot"""
        if self.check_robot(rid):
            return self.robots[rid].get_unit_eqp(eqp_name)

    def get_robot_all_eqp(self, rid):
        """Retourne la liste de tous les équipements d'un robot"""
        return self.robots[rid].get_all_eqp()

    def get_all_robots(self):
        """Retourne la liste de tous les robotids des robots présents dans l'annuaire"""
        return list(self.robots.keys())
