"""Module backend.py - Gestion jointe de l'annuaire et de la communication par ivy"""

import sys
from time import sleep, time
from PyQt5.QtCore import pyqtSignal #, pyqtSlot
from PyQt5.QtWidgets import QWidget
import annuaire
import ivy_radio as rd

class WidgetBackend (QWidget):
    """Classe implémentée car les signaux Qt doivent être envoyés par des objets Qt
    Attributs : _radio (Radio) : l'objet parent auquel sont reliés les connections de signal."""
    NewRobotSignal = pyqtSignal (str)
    ActuDeclSignal = pyqtSignal (list)
    UpdateTrigger = pyqtSignal (list)
    MapTrigger = pyqtSignal (list)

    equipement_updated = pyqtSignal(list)
    position_updated = pyqtSignal(list)
    def __init__ (self, parent_backend):
        super().__init__()
        self.backend = parent_backend
        self.position_updated.connect (lambda liste : self.backend.onPosRegSignal (liste))
        self.equipement_updated.connect (lambda liste : self.backend.onCaptRegSignal (liste))
        self.ActuDeclSignal.connect (lambda liste : self.backend.onActuDeclSignal (liste))

class Backend:
    """Un objet faisant le lien entre un Annuaire (module annuaire)
    et une Radio (module ivy_radio)

    Entrée:
        - annu (annuaire.Annuaire)
        - radio (rd.Radio)
        - flag (int, default = 0)
            - -1: vraiment aucune impression console
            -  0: pas d'impression console à part le message de lancement et celui d'arrêt
            -  1: impression basique toutes les 0.05s de l'annuaire associé dans la console
                (efface très vite toutes les autres entrées dans la console)
            -  2: impression "statique" de l'annuaire dans la console
    """

    def __init__(self, annu=None, radio=None, print_flag=0):
        self.runs = False
        self.radio_started = False
        self.premiersMessages = []
        self.print_flag = print_flag
        self.start_time = 0
        self.runned_time = 0
        self.radio = None
        self.annu = None
        if isinstance(radio, rd.Radio):
            self.attach_radio(radio)
        if isinstance(annu, annuaire.Annuaire):
            self.attach_annu(annu)
        self.widget = None

    def launchQt (self):
        """Méthode appelée après le lancement de l'application
        Les Widgets ne peuvent exister que s'il y a une application Qt

        Initialise l'attribut self.widget
        Réagit aux messages reçus avant le lancement de l'application Qt"""
        self.widget = WidgetBackend (self)
        for message in self.premiersMessages :
            if message [0] == 'pos' :
                self.widget.PosRegSignal.emit (message [1])
            elif message  [0] == 'actdcl':
                self.widget.ActuDeclSignal.emit (message [1])
            else :
                self.widget.CaptRegSignal.emit (message [1])

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
        if self.radio and self.annu:
            self.start_time = time()
            self.runs = True
            self.start_radio()
            if self.print_flag != -1:
                print("Backend Lancé. Ctrl+C pour arrêter.")
        else:
            raise Exception("Connectez une radio ET un annuaire avant de lancer le backend.")
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

    def run_as_loop(self, run_time=None):
        """Met en place une boucle infinie permettant un déboguage dans la console
        Pour les tests, un temps de fonctionnement peut être inscrit
        afin de ne pas rester dans une boucle infinie"""
        limited_time = False
        timer = 0
        if run_time is not None:
            limited_time = True
            timer = run_time
        while (self.runs and not limited_time) or (self.runs and limited_time and timer) >= 0:
            if self.print_flag == 1: #--spam-print
                print(self)
            if self.print_flag == 2: #--erase-print
                print(self, True)
            try:
                sleep(0.05)
                self.runned_time = time() - self.start_time
            except KeyboardInterrupt:
                self.runs = False
            if limited_time:
                timer -= 0.05

    def attach_annu(self, annu):
        """Attache l'annuaire 'annu' au backend
        (et remplace l'annu existant si il y en a un)

        Entrée:
            - annu (Annuaire): l'annuaire à attacher
        """
        if isinstance(annu, annuaire.Annuaire):
            self.annu = annu

    def attach_radio(self, radio):
        """Attache la radio 'radio' au backend
        (si il n'y en a pas déjà une)

        Entrée:
            - radio (radio): la radio à attacher
        """
        if isinstance(radio, rd.Radio) and self.radio is None:
            self.radio = radio
            self.radio.backend = self

    #Réactions aux signaux Qt

    def onPosRegSignal (self, liste ):
        """Méthode appelée automatiquement par on_posreg
        Transmet les valeurs envoyées par le robot vers l'annuaire
        Input :
            [rid (str), x (str), y (str), theta (str)] (list)"""
        rid, x, y, theta, last_update = liste [0], liste [1], liste [2], liste [3], liste [4]
        if not self.annu.check_robot (rid):
            self.track_robot (rid)
            self.radio.send_cmd (rd.DESCR_CMD.format (rid))
        self.annu.find (rid).set_pos (float (x), float(y), float(theta)*180/3.141592654)
        self.widget.UpdateTrigger.emit([])
        self.widget.MapTrigger.emit([])

    def onActuDeclSignal (self, liste):
        """Fonction appelée automatiquement par on_actudecl.
        Ajoute l'actionnneur aid sur le robot rid.
        Si aid est le nom d'un capteur déjà présent sur le robot, la valeur est gardée.

        Input : [rid (str), aid (str), minV (str), maxV (str),
                step (str), droits (str), unit (str)] (list)"""
        rid, aid, minv, maxv = liste [0], liste [1], liste [2], liste [3]
        step, droits, unit = liste [4], liste [5], liste [6]
        if droits == 'RW':
            binaire = False
            if float (minv) + float (step) >= float (maxv) :
                binaire = True
            if self.annu.find (rid,aid) is not None :
                valeur = self.annu.find (rid,aid).get_state () [0]
                self.annu.find (rid,aid).set_state (valeur)
            if binaire :
                self.annu.find (rid).create_eqp (aid, "Binaire")
            else :
                self.annu.find (rid).create_eqp (aid, "Actionneur",float(minv), float(maxv),
                                                 float(step), unit)
        elif droits == 'READ':
            add = False
            if not self.annu.find (rid).check_eqp (aid):
                add, val = True, None
            elif self.annu.find (rid, aid).get_type () is not annuaire.Actionneur :
                add, val = True, self.annu.find (rid, aid).get_state() [0]
            if add:
                self.annu.find (rid).create_eqp (aid, "Capteur", minv, maxv, step, unit)
                self.annu.find (rid, aid).set_state (val)
        self.widget.UpdateTrigger.emit([])

    def onCaptRegSignal (self, liste):
        """Fonction appelée automatiquement par on_captreg.
        Change la valeur du capteur sid sur le robot rid.
        Si aucun robot rid n'est connu, le robot est ajouté.
        Si le robot rid n'a pas de capteur sid, le capteur est ajouté.

        Input : [rid (str), sid (str), valeur (str)] (list)"""
        rid, sid, valeur, last_update = liste [0], liste [1], liste [2], liste [3]
        if not self.annu.check_robot (rid):
            self.track_robot (rid)
            self.radio.send_cmd (rd.DESCR_CMD.format (rid))
        if not self.annu.find (rid).check_eqp (sid):
            self.annu.find (rid).create_eqp (sid, "Capteur", None , None, None, None)
        self.annu.find (rid,sid).set_state (float (valeur))
        self.widget.UpdateTrigger.emit([])

    def track_robot(self, robot_name):
        """Invoqué lors de la demande de tracking d'un robot via l'interface graphique,
        ou lors de la découverte d'un robot inconnu par la radio (si implémenté).
        Ajoute le robot à l'annuaire
        (et émet un message de demande de configuration à destination de ce robot) (pas implémenté)

        Entrée:
            - robot_name (str): nom du robot à tracker
        """
        self.annu.add_robot(annuaire.Robot(robot_name))
        self.widget.NewRobotSignal.emit (robot_name)
        self.widget.UpdateTrigger.emit([])

    def emergency_stop_robot (self, rid):
        """Commande équivalente au boutton d'arrêt d'urgence.
        Est supposée bloquer les actionneurs et moteurs du robot sans pour autant arrêter le
        retour d'informations.

        Entrée :
            _ rid (str) : nom du robot à stopper"""
        if self.radio_started:
            self.radio.send_cmd (rd.STOP_BUTTON_CMD.format (rid))
        if self.annu.check_robot (rid):
            self.annu.find (rid).isStopped = True
        print ('Robot is stopped : {}'.format (self.annu.find (rid).isStopped))

    def stopandforget_robot(self, robot_name):
        """Permet d'arrêter le robot en question
        (via un message Shutdown ivy, si la radio est activée)
        et de le supprimer de l'annuaire

        Entrée:
            - robot_name (str): nom du robot à stopper/oublier
        """
        self.annu.remove_robot(robot_name)
        if self.radio_started:
            self.radio.send_cmd (rd.KILL_CMD.format (robot_name))
        self.widget.UpdateTrigger.emit([])
        self.widget.MapTrigger.emit([])

    def forget_robot(self, robot_name):
        """Oublie toutes les informations connues sur le robot en question.

        Entrée:
            - robot_name (str): nom du robot
        """
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
        if self.annu.check_robot(rid) and self.radio_started:
            if  self.annu.find (rid).isStopped :
                self.annu.find (rid).isStopped = False
            if pos[2] is None:
                self.radio.send_cmd (rd.POS_CMD.format (rid, pos[0], pos[1]))
            else:
                self.radio.send_cmd (rd.POS_ORIENT_CMD.format (rid, pos[0],
                                                                pos[1], pos[2]*3.141592654/180))

    def send_speed_cmd (self, rid, Vx, Vy, Vtheta):
        if self.radio_started :
            if  self.annu.find (rid).isStopped :
                self.annu.find (rid).isStopped = False
            self.radio.send_cmd (rd.SPEED_CMD.format (rid, Vx, Vy, Vtheta*3.141592654/180))

    def send_descr_cmd (self, rid):
        if self.radio_started :
            self.radio.send_cmd (rd.DESCR_CMD.format (rid))

    def sendeqpcmd(self, rid, eqp_name, state):
        """Envoie une commande d'état à un équipement (qui recoit des commandes)
        connecté à un robot.

        Entrée:
            - rid (str): nom du robot
            - eqp_name (str): nom de l'équipement
            - state (variable): l'état souhaité (se reférer au type d'equipement)
        """
        if self.annu.find(rid) and self.annu.find(rid, eqp_name):
            if  self.annu.find (rid).isStopped :
                self.annu.find (rid).isStopped = False
            self.annu.find(rid, eqp_name).updt_cmd()
            self.radio.send_cmd (rd.ACTUATOR_CMD.format (rid, eqp_name, state))

    def get_all_robots(self):
        """Retourne la liste de tous les noms des robots

        Sortie:
            - list of (str): les noms des robots
        """
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
        eqp = self.annu.find(robot_name, eqp_name)
        eqp_type = eqp.get_type()
        eqp_state = eqp.get_state()
        eqp_last_updt = eqp.get_last_updt()
        if eqp_type in (annuaire.Actionneur, annuaire.Binaire):
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
            save = False
            if "S" in flag:
                save = True
            delb = False
            if "D" in flag:
                delb = True
            self.radio.register_stop(save, delb, msgs, cmds, path)

    def record_state(self):
        """Revoie dans quelle mode d'enregistrement la radio se trouve

        Sorties:
            - tuple (bool, bool)
                - [0]: record_msgs
                - [1]: record_cmds"""
        return (self.radio.record_msgs, self.radio.record_cmds)

if __name__ == '__main__':
    PRINT_FL = 0
    if len(sys.argv) == 2 and sys.argv[1] == "--no-print":
        PRINT_FL = -1
    if len(sys.argv) == 2 and sys.argv[1] == "--spam-print":
        PRINT_FL = 1
    if len(sys.argv) == 2 and sys.argv[1] == "--erase-print":
        PRINT_FL = 2
    with Backend(annuaire.Annuaire(), rd.Radio(), PRINT_FL) as backend:
        backend.run_as_loop()
