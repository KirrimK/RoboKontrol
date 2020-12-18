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

class Actionneur(Equipement):
    """Définit un actionneur basique attaché à un robot,
    dont les commandes peuvent prendre une valeur (int) entre max et min (int),
    le tout dans une certaine unité.
    Un capteur peut aussi être associé à l'actionneur,
    auquel cas la valeur de ce capteur sera aussi stockée dans ce même objet

    Attributs:
    Hérités d'Equipement:
    - nom (str): le nom de l'actionneur
    - unite (str): l'unité dans laquelle les valeurs de l'actionneurs sont exprimées
    - last_updt (float): timestamp de la derniere update de la valeur

    Nouveaux:
    - valeur (float|None): valeur retournée par le capteur associé (None si sans retour)
    - min_val (float): valeur minimale de la commande
    - max_val (float): valeur max de la commannde
    - step (float): le step de l'actionneur (la commande doit être un multiple)
    - last_cmd (float): le timestamp de la dernière commande envoyée
    """
    def __init__(self, nom, min_val, max_val, step=1, unite=None):
        super().__init__(nom)
        self.valeur = None
        self.min_val = min_val
        self.max_val = max_val
        self.unite = unite
        self.step = step
        self.last_cmd = None

    def __str__(self):
        nom = self.nom
        val = self.valeur
        min_v = self.min_val
        max_v = self.max_val
        unt = self.unite
        stp = self.step
        return "Act. [{}] Val.: {} ({}) {} -> {} ({})".format(nom, val, unt, min_v, max_v, stp)

    def get_state(self):
        """Retourne la valeur et le min/max d'un actionneur

        Sortie:
        - state (float|None, float, float, float)
            - [0]: valeur de l'actionneur (None si sans retour)
            - [1]: valeur min
            - [2]: valeur max
            - [3]: step actionneur
        """
        return (self.valeur, self.min_val, self.max_val, self.step)

    def set_state(self, valeur):
        """Change la valeur du capteur associé

        Entrée:
        - valeur (float) (devrait être compris entre min et max actionneur inclus)
        """
        self.valeur = valeur
        self.updt()

    def updt_cmd(self):
        """Met à jour le timestamp de dernière commande"""
        self.last_cmd = time.time()

    def get_last_cmd(self):
        """Retourne le timestamp de la dernière commande envoyée"""
        return self.last_cmd

class Binaire(Actionneur):
    """Définit un actionneur prenant deux états (0 et 1),
    par exemple une pompe."""
    def __init__(self, nom):
        super().__init__(nom, 0, 1)

class Capteur(Equipement):
    """Définit un capteur avec un nom, une valeur et une unité

    Attributs:
    Hérités d'Equipement
    - nom (str): le nom du capteur
    - unite (str): unité du capteur
    - last_updt (float): timestamp de la derniere update de la valeur

    Nouveaux:
    - valeur (float): valeur du capteur"""
    def __init__(self, nom, valeur=0, unite=None):
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
        - (float|None, float, float, float) (Se référer à Actionneur.get_state())

        """
        return self.equipements[eqp_name].get_state()

    def set_state_eqp(self, eqp_name, valeur):
        """Change la valeur d'un équipement

        Entrée:
            - eqp_name (str): nom de l'équipement
            - valeur (variable): dépend du type de l'équipement portant le nom eqp_name
            > Equipement:
                - non utilisé, passer None
            > Capteur:
                - int (Se référer à Capteur.set_state()
            > Actionneur:
                - int (Se référer à Actionneur.set_state()
        """
        if self.check_eqp(eqp_name):
            self.equipements[eqp_name].set_state(valeur)

    def set_cmd_eqp(self, eqp_name):
        """Met à jour le fait qu'un équipement à recu une commande
        (Ne fonctionne qu'avec les Actionneur et dérivés)

        Entrée:
            -eqp_name (str): nom de l'équipement
        """
        if self.check_eqp(eqp_name):
            self.equipements[eqp_name].updt_cmd()

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

    def set_robot_eqp_cmd(self, rid, eqp_name):
        """Actualise le timestamp de la dernière commande envoyée à l'actionneur

        Entrée:
            - rid (str)
            - eqp_name (str)
        """
        if self.check_robot(rid):
            self.robots[rid].set_cmd_eqp(eqp_name)

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

    def robot_create_eqp(self, robot_name, eqp_name, eqp_type, *args):
        """Crée un nouvel équipement sur un robot

        Entrée:
            - rid (str)
            - eqp_name (str)
            - eqp_type (str): le type d'équipement,
            à choisir en inscrivant la chaine de caractère du nom de classe associé:
                'Equipement' / 'Actionneur' / 'Binaire' / 'Capteur'
            - args (Any): tous les autres arguments liés à la création des eqps
                si actionneur: (min, max, step (, unit))
                si capteur: (unit)
        """
        eqp = None
        if eqp_type == "Equipement":
            eqp = Equipement(eqp_name)
        elif eqp_type == "Actionneur":
            min_v = args[0]
            max_v = args[1]
            step = args[2]
            if len(args) == 4:
                unit = args[3]
            else:
                unit = None
            eqp = Actionneur(eqp_name, min_v, max_v, step, unit)
        elif eqp_type == "Binaire":
            eqp = Binaire(eqp_name)
        elif eqp_type == "Capteur":
            unit = args[0]
            eqp = Capteur(eqp_name, unite=unit)

        if self.check_robot(robot_name) and eqp is not None:
            self.robots[robot_name].updt_eqp(eqp)

#TODO: ajouter plus de features recommandées
