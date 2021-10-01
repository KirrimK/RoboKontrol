"""Module backend.py - Gestion jointe de l'annuaire et de la communication par ivy"""

from time import time
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget
import display as dsp
from radios import ivyRadio, serialRadio

class WidgetBackend (QWidget):
    """Classe implémentée car les signaux Qt doivent être envoyés par des objets Qt
    Attributs : backend (Backend) : l'objet parent auquel sont reliés les connections de signal."""
    NewRobotSignal = pyqtSignal (str)
    ActuDeclSignal = pyqtSignal (list)
    UpdateTrigger = pyqtSignal (list)
    MapTrigger = pyqtSignal (list)

    equipement_updated = pyqtSignal(list)
    position_updated = pyqtSignal(list)

    record_signal = pyqtSignal(float)
    def __init__ (self, parent_backend):
        super().__init__()
        self.backend = parent_backend
        self.position_updated.connect (self.backend.on_pos_reg_signal)
        self.equipement_updated.connect (self.backend.on_capt_reg_signal)
        self.ActuDeclSignal.connect (self.backend.on_actu_decl_signal)

class Backend:
    """Un objet faisant le lien entre un Annuaire (module annuaire)
    et une Radio (module ivy_radio)

    Entrée:
        - annu (annuaire.Annuaire)
        - radio (radios.Radio)
        - flag (int, default = 0)
            - -1: vraiment aucune impression console
            -  0: pas d'impression console à part le message de lancement et celui d'arrêt
            -  1: impression basique toutes les 0.05s de l'annuaire associé dans la console
                (efface très vite toutes les autres entrées dans la console)
            -  2: impression "statique" de l'annuaire dans la console
    """

    def __init__(self, radio=None, print_flag=0):
        self.runs = False
        self.radio_started = False
        self.premiers_messages = []
        self.print_flag = print_flag
        self.start_time = 0
        self.runned_time = 0
        self.radio = None
        self.annu = None
        if isinstance(radio, ivyRadio) or isinstance (radio, serialRadio):
            self.attach_radio(radio)
        self.widget = None

    def launch_qt (self):
        """Méthode appelée après le lancement de l'application
        Les Widgets ne peuvent exister que s'il y a une application Qt

        Initialise l'attribut self.widget
        Réagit aux messages reçus avant le lancement de l'application Qt"""
        self.widget = WidgetBackend (self)
        for message in self.premiers_messages :
            if message [0] == 'pos' :
                self.widget.position_updated.emit (message [1])
            elif message  [0] == 'actdcl':
                self.widget.ActuDeclSignal.emit (message [1])
            else :
                self.widget.equipement_updated.emit (message [1])

    def __str__(self, erase_flag=False):
        if not erase_flag:
            self_str = str(self.runned_time)[:6]+'s\n'
            self_str += self.annu.__str__()
        else:
            number_lines = 1 + self.annu.__str__().count("\n")
            self_str = ('\n' + 50 * " ") * number_lines
            self_str += '\n' + (number_lines + 1) * "\033[F"
            self_str += '\n' +str(self.runned_time)[:6]+'s'
            self_str += '\n' + self.annu.__str__()
            self_str += '\n' + (number_lines + 3) * "\033[F" + "\n"
        return self_str

    def __enter__(self):
        if self.radio:
            self.start_time = time()
            self.runs = True
            self.start_radio()
            if self.print_flag != -1:
                print("Backend Lancé. Ctrl+C pour arrêter.")
        else:
            raise Exception("Connectez une radio avant de lancer le backend.")
        return self

    def __exit__(self, excp_type, value, traceback):
        self.runned_time = time() - self.start_time
        self.runs = False
        self.stop_radio()
        if self.print_flag != -1:
            print("\nBackend Arrêté. Temps d'exécution: "+str(self.runned_time)[:6]+"s.")

    def stop_radio(self):
        """Arrête la Radio connectée au Backend"""
        if self.radio_started:
            self.radio.stop()
            self.radio_started = False

    def start_radio(self):
        """Met la Radio connectée au Backend en marche"""
        if self.radio and not self.radio_started:
            self.radio.start()
            self.radio_started = True

    def attach_radio(self, radio):
        """Attache la radio 'radio' au backend
        (si il n'y en a pas déjà une)

        Entrée:
            - radio (radio): la radio à attacher
        """
        if (isinstance(radio, ivyRadio) or isinstance (radio, serialRadio)) and self.radio is None:
            self.radio = radio
            self.radio.backend = self

    #Réactions aux signaux Qt

    def on_pos_reg_signal(self, liste):
        """Méthode appelée automatiquement par on_posreg
        Transmet les valeurs envoyées par le robot vers l'annuaire
        Input :
            [rid (str), x (str), y (str), theta (str)] (list)"""
        rid, posx, posy, theta = liste [0], liste [1], liste [2], liste [3]
        if self.annu is not None:
            if not self.annu.check_robot(rid):
                self.track_robot(rid)
                self.radio.send_descr_cmd (rid)
            self.annu.find (rid).set_pos (float (posx), float(posy), float(theta)*180/3.141592654)
            self.widget.UpdateTrigger.emit([])
            self.widget.MapTrigger.emit([])

    def on_actu_decl_signal (self, liste):
        """Fonction appelée automatiquement par on_actudecl.
        Ajoute l'actionnneur aid sur le robot rid.
        Si aid est le nom d'un capteur déjà présent sur le robot, la valeur est gardée.

        Input : [rid (str), aid (str), minV (str), maxV (str),
                step (str), droits (str), unit (str)] (list)"""
        rid, aid, minv, maxv = liste [0], liste [1], liste [2], liste [3]
        step, droits, unit = liste [4], liste [5], liste [6]
        if self.annu is not None:

            if droits == 'RW':
                valeur = None
                if self.annu.find(rid,aid) is not None:
                    #un équipement existe déjà
                    valeur = self.annu.find(rid,aid).get_state()[0]
                if float (minv) + float (step) >= float (maxv):
                    self.annu.find(rid).create_eqp(aid, "Binaire")
                else:
                    self.annu.find(rid).create_eqp(aid, "Actionneur", float(minv), float(maxv),
                                                    float(step), unit)
                if valeur is not None:
                    #restauration de la valeur après la mise à jour de l'équipement
                    self.annu.find(rid,aid).set_state(valeur)

            elif droits == 'READ':
                if not self.annu.find (rid).check_eqp (aid):
                    self.annu.find (rid).create_eqp (aid, "Capteur", minv, maxv, step, unit)
                elif self.annu.find (rid, aid).get_type () is not dsp.DisplayActionneur :
                    val = self.annu.find (rid, aid).get_state() [0]
                    self.annu.find (rid).create_eqp (aid, "Capteur", minv, maxv, step, unit)
                    self.annu.find (rid, aid).set_state (val)

            self.widget.UpdateTrigger.emit([])

    def on_capt_reg_signal (self, liste):
        """Fonction appelée automatiquement par on_captreg.
        Change la valeur du capteur sid sur le robot rid.
        Si aucun robot rid n'est connu, le robot est ajouté.
        Si le robot rid n'a pas de capteur sid, le capteur est ajouté.

        Input : [rid (str), sid (str), valeur (str)] (list)"""
        rid, sid, valeur = liste [0], liste [1], liste [2]
        if self.annu is not None:
            if not self.annu.check_robot (rid):
                self.track_robot (rid)
                self.radio.send_descr_cmd(rid)
            if not self.annu.find (rid).check_eqp (sid):
                self.annu.find (rid).create_eqp (sid, "Capteur", None , None, None, None)
            self.annu.find (rid,sid).set_state (float (valeur))
            self.widget.UpdateTrigger.emit([])

    #Interaction avec robots

    def track_robot(self, robot_name):
        """Invoqué lors de la demande de tracking d'un robot via l'interface graphique,
        ou lors de la découverte d'un robot inconnu par la radio (si implémenté).
        Ajoute le robot à l'annuaire
        (et émet un message de demande de configuration à destination de ce robot) (pas implémenté)

        Entrée:
            - robot_name (str): nom du robot à tracker
        """
        if self.annu is not None:
            self.annu.add_robot(dsp.DisplayRobot(self.annu, robot_name))
            self.widget.NewRobotSignal.emit (robot_name)
            self.widget.UpdateTrigger.emit([])

    def emergency_stop_robot (self, rid):
        """Commande équivalente au boutton d'arrêt d'urgence.
        Est supposée bloquer les actionneurs et moteurs du robot sans pour autant arrêter le
        retour d'informations.

        Entrée :
            _ rid (str) : nom du robot à stopper"""
        if self.radio_started:
            self.radio.send_stop_cmd (rid)
        if self.annu.check_robot (rid):
            self.annu.find (rid).is_stopped = True
        print ('Robot is stopped : {}'.format (self.annu.find (rid).is_stopped))

    def stopandforget_robot(self, robot_name):
        """Permet d'arrêter le robot en question
        (via un message Shutdown ivy, si la radio est activée)
        et de le supprimer de l'annuaire

        Entrée:
            - robot_name (str): nom du robot à stopper/oublier
        """
        if self.annu is not None:
            self.annu.remove_robot(robot_name)
        if self.radio_started:
            self.radio.send_kill_cmd (robot_name)
        self.widget.UpdateTrigger.emit([])
        self.widget.MapTrigger.emit([])

    def stop_robot(self, robot_name):
        """Arrête un robot"""
        if self.radio_started:
            self.radio.send_kill_cmd (robot_name)

    def forget_robot(self, robot_name):
        """Oublie toutes les informations connues sur le robot en question.

        Entrée:
            - robot_name (str): nom du robot
        """
        if self.annu is not None:
            self.annu.remove_robot(robot_name)
            self.widget.UpdateTrigger.emit([])
            self.widget.MapTrigger.emit([])

    def sendposcmd_robot(self, rid, pos):
        """Envoie une commande de position au robot désigné

        Entrée:
            - rid (str): nom du robot
            - pos (float, float, float): "vecteur" position de la destination du robot
                - [0]: x
                - [1]: y
                - [2]: theta (si non spécifié, mettre à None)
        """

        if self.annu is not None and self.annu.check_robot(rid) and self.radio_started:
            if self.annu.find (rid) is not None :
                if  self.annu.find (rid).is_stopped :
                    self.annu.find (rid).is_stopped = False
        if pos[2] is None:
            self.radio.send_pos_cmd (rid, int(pos[0]), int(pos[1]))
        else:
            self.radio.send_pos_orient_cmd (rid, int(pos[0]), int(pos[1]), pos[2]*3.141592654/180)

    def send_speed_cmd (self, rid, v_x, v_y, v_theta):
        """Envoi de commande de vitesse au robot"""
        if self.annu.find (rid) is not None and self.annu is not None:
            if self.annu.find (rid).is_stopped :
                self.annu.find (rid).is_stopped = False
        if self.radio_started:
            self.radio.send_speed_cmd (rid, int(v_x), int(v_y), int(v_theta))

    def send_descr_cmd (self, rid):
        """Envoi de demande de description au robot

        Entrée:
            - rid (str): nom du robot"""
        if self.radio_started and self.annu is not None:
            self.radio.send_descr_cmd (rid)

    def sendeqpcmd(self, rid, eqp_name, state):
        """Envoie une commande d'état à un équipement (qui recoit des commandes)
        connecté à un robot.

        Entrée:
            - rid (str): nom du robot
            - eqp_name (str): nom de l'équipement
            - state (variable): l'état souhaité (se reférer au type d'equipement)
        """
        if self.annu is not None and self.annu.find(rid) and self.annu.find(rid, eqp_name):
            if  self.annu.find (rid).is_stopped :
                self.annu.find (rid).is_stopped = False
        self.radio.send_act_cmd (rid, eqp_name, state)

    def get_all_robots(self):
        """Retourne la liste de tous les noms des robots

        Sortie:
            - list of (str): les noms des robots
        """
        if self.annu is not None:
            return self.annu.get_all_robots()

    def getdata_robot(self, robot_name):
        """Renvoie toutes les informations connues sur le robot

        Entrée:
            - robot_name (str): nom du robot

        Sortie:
            - tuple (tuple, list, float)
                - [0] pos (float, float, float): le "vecteur" position du robot
                - [1] eqps (list of str): liste des noms des équipements attachés au robot
                - [2] last_updt_pos (float): le timestamp de dernière mise à jour de la position
        """
        if self.annu is not None:
            rbt = self.annu.find(robot_name)
            pos = rbt.get_pos()
            eqps = rbt.get_all_eqp()
            return (pos, eqps, rbt.last_updt_pos)

    def getdata_eqp(self, robot_name, eqp_name):
        """Renvoie toutes les informations sur un équipement

        Entrée:
            - robot_name (str): nom du robot
            - eqp_name (str): nom de l'équipement

        Sortie:
            - tuple (type, any, float, float | None)
                - [0] eqp_type (type): le type de l'équipement
                - [1] eqp_state (tuple): l'état actuel de l'équipement
                    (se référer à l'équipement en question)
                - [2] eqp_last_updt (float): le timestamp de la dernière info reçue
                    (se référer à l'équipement en question)
                - [3] eqp_last_cmd (float | None): si l'eqp est un actionneur,
                    le timestamp de la dernière commande envoyée par l'user
                - [4] eqp_unit (str): le type de l'équipement
        """
        if self.annu is not None:
            eqp = self.annu.find(robot_name, eqp_name)
            eqp_type = eqp.get_type()
            eqp_state = eqp.get_state()
            eqp_last_updt = eqp.get_last_updt()
            if eqp_type in (dsp.DisplayActionneur, dsp.DisplayBinaire):
                eqp_last_cmd = eqp.get_last_cmd()
            else:
                eqp_last_cmd = None
            eqp_unit = eqp.get_unit()
            return (eqp_type, eqp_state, eqp_last_updt, eqp_last_cmd, eqp_unit)

    def record(self, flag, path = None):
        """Permet de déclencher/arrêter l'enregistrement des messages depuis l'interface

        Entrées:
            - flag (str): le drapeau correspondant au mode souhaité
                (la première lettre est B (begin) ou E (end), puis
                M pour messages / C pour commandes /
                S pour sauvegarder lors arrêt / D pour effacer mémoire interne radio)
                Exemple: BMC: démarrer enregistrement de tout
                         ECSD: arrêter d'enregistrer les commandes, sauvegarder puis effacer
        """
        if flag[0] == "B": #begin
            self.widget.record_signal.emit(0)
            msgs = None
            cmds = None
            if "M" in flag:
                msgs = "msgs"
            if "C" in flag:
                cmds = "cmds"
            self.radio.register_start(msgs, cmds)
        if flag[0] == "E": #end
            msgs = None
            cmds = None
            if "M" in flag:
                msgs = "msgs"
            if "C" in flag:
                cmds = "cmds"
            delb = False
            if "D" in flag:
                delb = True
                self.widget.record_signal.emit(-2)
            save = False
            if "S" in flag:
                save = True
                self.widget.record_signal.emit(-1)
            self.radio.register_stop(save, delb, msgs, cmds, path)

    def record_state(self):
        """Revoie dans quelle mode d'enregistrement la radio se trouve

        Sorties:
            - tuple (bool, bool)
                - [0]: record_msgs
                - [1]: record_cmds"""
        return (self.radio.record_msgs, self.radio.record_cmds)
