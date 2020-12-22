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
        if radio is not None:
            self.attach_radio(radio)
        if annu is not None:
            self.attach_annu(annu)

    def __enter__(self):
        self.start_time = time()
        if self.radio and self.annu:
            self.radio.start()
            self.runs = True
            self.radio_started = True
            if self.print_flag != -1:
                print("Backend Lancé.")
        else:
            raise Exception("Connectez une radio ET un annuaire avant de lancer le backend.")
        return self

    def __exit__(self, t, value, traceback):
        if self.radio_started:
            self.radio.stop()
            if self.print_flag != -1:
                print("\nBackend Arrêté. Temps d'exécution: "+str(self.runned_time)[:6]+"s.")

    def run_as_loop(self):
        """Met en place une boucle infinie permettant une exécution sans interface"""
        while self.runs:
            if self.print_flag == 1: #--spam-print
                print(str(self.runned_time)[:6]+'s')
                print(self.annu)
            if self.print_flag == 2: #--erase-print
                annu_str = self.annu.__str__()
                number_lines = 1 + annu_str.count("\n")
                print(('\n' + 50 * " ") * number_lines)
                print((number_lines + 1) * "\033[F")
                print(str(self.runned_time)[:6]+'s')
                print(annu_str)
                print((number_lines + 3) * "\033[F")
            try:
                sleep(0.05)
                self.runned_time = time() - self.start_time
            except KeyboardInterrupt:
                self.runs = False

    def attach_annu(self, annu):
        """Attache l'annuaire 'annu' au backend

        Entrée:
            - annu (Annuaire): l'annuaire à attacher
            - flag (bool): lancement de self.run_print_console si true
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
        (et émet un message de demande de configuration à destination de ce robot) (pas implémenté)

        Entrée:
            - robot_name (str): nom du robot à tracker
        """
        self.annu.add_robot(annuaire.Robot(robot_name))
        #self.radio.send_cmd (rd.DESCR_CMD.format (robot_name))

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
        if self.annu.check_robot(robot_name):
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
            - pos (float, float, float): le "vecteur" position du robot
            - eqps (list of str): liste des noms des équipements attachés au robot
            - last_updt_pos (float): le timestamp de dernière mise à jour de la position
        """
        rbt = self.annu.find(robot_name)
        pos = rbt.get_pos()
        eqps = rbt.get_all_eqp()
        return pos, eqps, rbt.last_updt_pos

    def getdata_eqp(self, robot_name, eqp_name):
        """Renvoie toutes les informations sur un équipement

        Entrée:
            - robot_name (str): nom du robot
            - eqp_name (str): nom de l'équipement

        Sortie:
            - eqp_type (type): le type de l'équipement
            - eqp_state (variable): l'état actuel de l'équipement
                (se référer à l'équipement en question)
            - eqp_last_updt (variable): l'état actuel de l'équipement
                (se référer à l'équipement en question)
        """
        eqp = self.annu.find(robot_name, eqp_name)
        eqp_type = eqp.get_type()
        eqp_state = eqp.get_state()
        eqp_last_updt = eqp.get_last_updt()
        if eqp_type == annuaire.Actionneur or eqp_type == annuaire.Binaire:
            eqp_last_cmd = eqp.get_last_cmd()
        else:
            eqp_last_cmd = None
        return eqp_type, eqp_state, eqp_last_updt, eqp_last_cmd

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
