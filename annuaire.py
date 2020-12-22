"""Module annuaire.py - gestion et mise à jour des informations connues sur les robots trackés"""

class Actionneur:
    """Définit un actionneur basique attaché à un robot,
    pouvant prendre une valeur (int) entre max et min (int), le tout dans une certaine unité

    - nom (str): le nom de l'actionneur
    - valeur (int): l'état actuel de l'actionneur (compris entre min et max)
    - min (int): valeur minimale prise par l'actionneur
    - max (int): valeur max prise par l'actionneur
    - unite (str): l'unité dans laquelle les valeurs de l'actionneurs sont exprimées
    """
    def __init__(self, nom, valeur, min_val, max_val, unite):
        self.nom = nom
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
    
    def get_unit(self):
        """Renvoie l'unité de l'actionneur"""
        return self.unite

class Robot:
    """Classe définissant un robot avec les attributs suivants:
    - id (str): le nom du robot
    - x (float): la position selon l'axe x du robot sur la carte (en mm)
    - y (float): la position selon l'axe x du robot sur la carte (en mm)
    - theta (float): l'orientation du robot (en radians/sens trigo depuis axe x)
    - actionneurs (list of Actionneur): liste des actionneurs connectés au robot
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

    def check_act(self, act_name):
        """Verifie si un actionneur est rattaché au robot"""
        return act_name in self.get_all_act()

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
        """Retourne l'état et le min/max d'un actionneur"""
        if self.check_act(act_name):
            return self.actionneurs[act_name].get_state()

    def set_state_act(self, act_name, valeur):
        """Change la valeur d'un actionneur"""
        if self.check_act(act_name):
            self.actionneurs[act_name].set_state(valeur)

    def get_type_act(self, act_name):
        """Retourne le type d'un actionneur"""
        if self.check_act(act_name):
            return type(self.actionneurs[act_name])
    
    def get_unit_act(self, act_name):
        """Retourne l'unité d'un actionneur"""
        if self.check_act(act_name):
            return self.actionneurs[act_name].get_unit()

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
        sur un robot présent dans l'annuaire (ne pas utiliser pour mettre la valeur à jour)"""
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

    def get_robot_act_type(self, rid, act_name):
        """Retourne la variété d'un actionneur monté sur un robot"""
        if self.check_robot(rid):
            return self.robots[rid].get_type_act(act_name)

    def get_robot_act_unit(self, rid, act_name):
        """Retourne l'unité d'un actionneur monté sur un robot"""
        if self.check_robot(rid):
            return self.robots[rid].get_unit_act(act_name)

    def get_robot_all_act(self, rid):
        """Retourne la liste de tous les actionneurs d'un robot"""
        return self.robots[rid].get_all_act()

    def get_all_robots(self):
        """Retourne la liste de tous les robotids des robots présents dans l'annuaire"""
        return list(self.robots.keys())
