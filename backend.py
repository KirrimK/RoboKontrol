"""Module backend.py - Gestion jointe de l'annuaire et de la communication par ivy"""

import sys
from time import sleep, time
import annuaire
import ivy_radio as rd

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
        self.print_flag = print_flag
        self.start_time = 0
        self.runned_time = 0
        self.radio = None
        self.annu = None
        if isinstance(radio, rd.Radio):
            self.attach_radio(radio)
        if isinstance(annu, annuaire.Annuaire):
            self.attach_annu(annu)

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

    def track_robot(self, robot_name):
        """Invoqué lors de la demande de tracking d'un robot via l'interface graphique,
        ou lors de la découverte d'un robot inconnu par la radio (si implémenté).
        Ajoute le robot à l'annuaire
        (et émet un message de demande de configuration à destination de ce robot) (pas implémenté)

        Entrée:
            - robot_name (str): nom du robot à tracker
        """
        self.annu.add_robot(annuaire.Robot(robot_name))
        #self.radio.send_cmd (rd.DESCR_CMD.format (robot_name)) dépréciée

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
        if self.annu.check_robot(robot_name) and self.radio_started:
            if pos[2] is None:
                self.radio.send_cmd (rd.POS_CMD.format (robot_name, pos[0], pos[1]))
            else:
                self.radio.send_cmd (rd.POS_ORIENT_CMD.format (robot_name, pos[0], pos[1], pos[2]))

    def sendeqpcmd(self, robot_name, eqp_name, state):
        """Envoie une commande d'état à un équipement (qui recoit des commandes)
        connecté à un robot.

        Entrée:
            - robot_name (str): nom du robot
            - eqp_name (str): nom de l'équipement
            - state (variable): l'état souhaité (se reférer au type d'equipement)
        """
        if self.annu.find(robot_name) and self.annu.find(robot_name, eqp_name):
            self.annu.find(robot_name, eqp_name).updt_cmd()
            self.radio.send_cmd (rd.ACTUATOR_CMD.format (robot_name, eqp_name, state))

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
                - [1] eqp_state (any): l'état actuel de l'équipement
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
        if len(eqp_state) == 1:
            eqp_state = eqp_state[0]
        eqp_last_updt = eqp.get_last_updt()
        if eqp_type == annuaire.Actionneur or eqp_type == annuaire.Binaire:
            eqp_last_cmd = eqp.get_last_cmd()
        else:
            eqp_last_cmd = None
        eqp_unit = eqp.get_unit()
        return (eqp_type, eqp_state, eqp_last_updt, eqp_last_cmd, eqp_unit)

    def record(self, flag):
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
            args = []
            if "M" in flag:
                args.append("msgs")
            if "C" in flag:
                args.append("cmds")
            args = tuple(args)
            print(args)
            self.radio.register_start(args)
        if flag[0] == "E": #end
            args = []
            if "M" in flag:
                print("Emsgs")
                args.append("msgs")
            if "C" in flag:
                print("Ecmds")
                args.append("cmds")
            args = tuple(args)
            save = False
            if "S" in flag:
                print("Esave")
                save = True
            delb = False
            if "D" in flag:
                print("Edel")
                delb = True
            self.radio.register_stop(save, delb, args)

    def record_state(self):
        """Revoie dans quelle mode d'enregistrement la radio se trouve

        Sorties:
            - tuple (bool, bool)
                - [0]: record_msgs
                - [1]: record_cmds"""
        return (self.radio.record_msgs, self.radio.record_cmds)

#if __name__ == '__main__':
#    PRINT_FL = 0
#    if len(sys.argv) == 2 and sys.argv[1] == "--no-print":
#        PRINT_FL = -1
#    if len(sys.argv) == 2 and sys.argv[1] == "--spam-print":
#        PRINT_FL = 1
#    if len(sys.argv) == 2 and sys.argv[1] == "--erase-print":
#        PRINT_FL = 2
#    with Backend(annuaire.Annuaire(), rd.Radio(), PRINT_FL) as backend:
#        backend.run_as_loop()
