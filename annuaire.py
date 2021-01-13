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

    def get_type(self):
        """Retourne le type de l'équipement"""
        return type(self)

class Capteur(Equipement):
    """Définit un capteur avec un nom, une valeur et une unité

    Attributs:
    Hérités d'Equipement
    - nom (str): le nom du capteur
    - unite (str): unité du capteur
    - last_updt (float): timestamp de la derniere update de la valeur

    Nouveaux:
    - min (float): minimum attendu du capteur (UI only)
    - max (float): maximum attendu du capteur (UI only)
    - step (float): le step du capteur (UI only)
    - valeur (float): la valeur du capteur
    """
    def __init__(self, nom, min_val, max_val, step, unite=None):
        super().__init__(nom)
        self.valeur = 0
        self.min_val = min_val
        self.max_val = max_val
        self.unite = unite
        self.step = step

    def __str__(self):
        nom = self.nom
        val = self.valeur
        min_v = self.min_val
        max_v = self.max_val
        unt = self.unite
        stp = self.step
        return "Cpt. [{}] Val.: {} ({}) {} -> {} ({})".format(nom, val, unt, min_v, max_v, stp)

    def get_state(self):
        """Renvoie l'état de l'équipement

        Sortie:
            - state (float, float, float, float)
            - [0]: valeur actuelle
            - [1]: valeur min
            - [2]: valeur max
            - [3]: step
        """
        return (self.valeur, self.min_val, self.max_val, self.step)

    def set_state(self, valeur):
        """Change la valeur

        Entrée:
        - valeur (float)"""
        self.valeur = valeur
        self.updt()

class Actionneur(Capteur):
    """Définit un actionneur basique attaché à un robot,
    dont les commandes peuvent prendre une valeur (int) entre max et min (int),
    le tout dans une certaine unité.
    Un capteur peut aussi être associé à l'actionneur,
    auquel cas la valeur de ce capteur sera aussi stockée dans ce même objet

    Attributs:
    Hérités de Capteur:
    - nom (str): le nom de l'actionneur
    - unite (str): l'unité dans laquelle les valeurs de l'actionneurs sont exprimées
    - last_updt (float): timestamp de la derniere update de la valeur
    - valeur (float|None): valeur retournée par le capteur associé (None si sans retour)
    - min_val (float): valeur minimale de la commande
    - max_val (float): valeur max de la commannde
    - step (float): le step de l'actionneur (la commande doit être un multiple)

    Nouveaux:
    - last_cmd (float): le timestamp de la dernière commande envoyée
    """
    def __init__(self, nom, min_val, max_val, step=1, unite=None):
        super().__init__(nom, min_val, max_val, step, unite)
        self.last_cmd = None
        self.valeur = None

    def __str__(self):
        nom = self.nom
        val = self.valeur
        min_v = self.min_val
        max_v = self.max_val
        unt = self.unite
        stp = self.step
        return "Act. [{}] Val.: {} ({}) {} -> {} ({})".format(nom, val, unt, min_v, max_v, stp)

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

    def __str__(self):
        nom = self.nom
        val = self.valeur
        return "Binaire [{}] Val.: {}".format(nom, val)

class LED(Actionneur):
    """Une class définissant une LED, dont les commandes se font sur 3x 255 valeurs"""
    def __init__(self, nom):
        super().__init__(nom, 0, 255, 1, None)

    def __str__(self):
        nom = self.nom
        val = self.valeur
        return "LED [{}] RGB: {}".format(nom, val)

    def get_state(self):
        """Retourne les trois valeurs RGB de la LED (si elles sont connues)

        Sortie:
        - valeur (int, int, int) | None
            - [0]: rouge
            - [1]: vert
            - [2]: bleu
        """
        return self.valeur

    def set_state(self, valeur):
        """Change la valeur du retour de led associé (si existe)

        Entrée:
        - valeur tuple (int, int, int) (chaque int entre 0 et 255)
        """
        if isinstance(valeur, tuple) and len(valeur) == 3:
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
        self.isStopped = False
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

    def create_eqp(self, eqp_name, eqp_type, *args):
        """Crée un nouvel équipement, et l'ajoute au robot
        (sans avoir besoin de manipuler des objets Equipement

        Entrée:
            - eqp_name (str)
            - eqp_type (str): le type d'équipement,
            à choisir en inscrivant la chaine de caractère du nom de classe associé:
                'Equipement' / 'Actionneur' / 'Binaire' / 'Capteur'
            - args (tuple): tous les autres arguments liés à la création des eqps
                si actionneur ou capteur: (min, max, step (, unit))
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
            min_v = args[0]
            max_v = args[1]
            step = args[2]
            if len(args) == 4:
                unit = args[3]
            else:
                unit = None
            eqp = Capteur(eqp_name, min_v, max_v, step, unit)

        if eqp is not None:
            self.updt_eqp(eqp)

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

    def find(self, eqp_name):
        """Trouve un Equipement (ou dérivé) attaché au robot par son nom,
        et le renvoie:

        Entrée:
            - eqp_name (str): nom de l'équipement

        Sortie:
            - Equipement (ou dérivé) | None
        """
        if eqp_name in self.equipements:
            return self.equipements[eqp_name]
        else:
            return None

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

    def find(self, robot_name, eqp_name=None):
        """Retourne l'objet Robot identifié par robot_name,
        ou l'equipement désigné par eqp_name qui y est rattaché (si mentionné)

        Entrée:
            - robot_name (str)
            - eqp_name (str)

        Sortie:
            - Robot | Equipement (ou dérivé)
        """
        if eqp_name is None and robot_name in self.robots:
            return self.robots[robot_name]
        if eqp_name is not None and robot_name in self.robots:
            return self.find(robot_name).find(eqp_name)
        else:
            return None

    def get_all_robots(self):
        """Retourne la liste de tous les robotids des robots présents dans l'annuaire

        Sortie:
        - list of (str)
        """
        return list(self.robots.keys())
