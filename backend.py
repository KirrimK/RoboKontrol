"""Module backend.py - Gestion jointe de l'annuaire et de la communication par ivy"""

import annuaire
import ivy_radio as rd

class Backend:
    """Un objet faisant le lien entre un Annuaire (module annuaire)
    et une Radio (module ivy_radio)"""

    def __init__(self):
        self.annu = None
        self.radio = None

    def attach_annu(self, annu):
        """Attache l'annuaire 'annu' au backend

        Entrée:
            - annu (Annuaire): l'annuaire à attacher
        """
        if isinstance(annu, annuaire.Annuaire):
            self.annu = annu

    def attach_radio(self, radio):
        """Attache la radio 'radio' au backend

        Entrée:
            - radio (radio): la radio à attacher
        """
        if isinstance(radio, rd.Radio):
            self.radio = radio
            self.radio.backend = self

    def track_robot(self, robot_name):
        """Invoqué lors de la demande de tracking d'un robot via l'interface graphique,
        ou lors de la découverte d'un robot inconnu par la radio (si implémenté).
        Ajoute le robot à l'annuaire
        et émet un message de demande de configuration à destination de ce robot

        Entrée:
            - robot_name (str): nom du robot à tracker
        """
        self.annu.add_robot(annuaire.Robot(robot_name))
        self.radio.send_cmd (rd.DESCR_CMD.format (robot_name))

    def istracked_robot(self, robot_name):
        """Evalue si le robot en question est actuellement tracké ou non.

        Entrée:
            - robot_name (str): nom du robot

        Sortie:
            - bool
        """
        return self.annu.check_robot(robot_name)

    def stopandforget_robot(self, robot_name):
        """Permet d'arrêter le robot en question (via un message Shutdown ivy)
        et de le supprimer de l'annuaire

        Entrée:
            - robot_name (str): nom du robot à stopper/oublier
        """
        self.annu.remove_robot(robot_name)
        self.radio.send_cmd (rd.KILL_CMD.format (robot_name))

    def forget_robot(self, robot_name):
        """Oublie toutes les informations connues sur le robot en question.

        Entrée:
            - robot_name (str): nom du robot
        """
        self.annu.remove_robot(robot_name)

    def sendposcmd_robot(self, robot_name, pos):
        """Envoie une commande de position au robot désigné

        Entrée:
            - robot_name (str): nom du robot
            - pos (float, float, float): "vecteur" position de la destination du robot
                - [0]: x
                - [1]: y
                - [2]: theta (si non spécifié, mettre à None)
        """
        if self.istracked_robot(robot_name):
            if pos[2] is None:
                self.radio.send_cmd (rd.POS_CMD.format (pos[0], pos[1]))
            else:
                self.radio.send_cmd (rd.POS_ORIENT_CMD.format (pos[0], pos[1], pos[2]))

    def sendeqpcmd(self, robot_name, eqp_name, state):
        """Envoie une commande d'état à un équipement (qui recoit des commandes)
        connecté à un robot.

        Entrée:
            - robot_name (str): nom du robot
            - eqp_name (str): nom de l'équipement
            - state (variable): l'état souhaité (se reférer au type d'equipement)
        """
        if self.istracked_robot(robot_name) and self.annu.check_robot_eqp(robot_name, eqp_name):
            eqp_type = self.annu.get_robot_eqp_type(robot_name, eqp_name)
            if eqp_type == annuaire.Actionneur:
                self.annu.set_robot_eqp_state(robot_name, eqp_name, state)
            elif eqp_type == annuaire.ActioCapteur:
                self.annu.set_robot_eqp_state(robot_name, eqp_name, (state, None))

    def getdata_robot(self, robot_name):
        """Renvoie toutes les informations connues sur le robot

        Entrée:
            - robot_name (str): nom du robot

        Sortie:
            - pos (float, float, float): le "vecteur" position du robot
            - eqps (list of str): liste des noms des équipements attachés au robot
            - last_updt_pos (float): le timestamp de dernière mise à jour de la position
        """
        pos = self.annu.get_robot_pos(robot_name)
        eqps = self.annu.get_robot_all_eqp(robot_name)
        last_updt_pos = self.annu.get_robot_last_updt_pos(robot_name)
        return pos, eqps, last_updt_pos

    def getdata_eqp(self, robot_name, eqp_name):
        """Renvoie toutes les informations sur un équipement

        Entrée:
            - robot_name (str): nom du robot
            - eqp_name (str): nom de l'équipement

        Sortie:
            - eqp_type (type): le type de l'équipement
            - eqp_state (variable): l'état actuel de l'équipement
                (se référer à l'équipement en question)
            - eqp_state (variable): l'état actuel de l'équipement
                (se référer à l'équipement en question)
        """
        eqp_type = self.annu.get_robot_eqp_type(robot_name, eqp_name)
        eqp_state = self.annu.get_robot_eqp_state(robot_name, eqp_name)
        eqp_last_updt = self.annu.get_robot_eqp_last_updt(robot_name, eqp_name)
        return eqp_type, eqp_state, eqp_last_updt
