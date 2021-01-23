"""Module dédié au replay d'un fichier"""

from time import time
from PyQt5.QtCore import QTimer
from display import DisplayActionneur as ACT

class Lecteur :
    """Classe permettant la lecture des fichiers. S'initialise avec la fenêtre."""
    def __init__ (self, window):
        self.window = window
        self.timer = QTimer ()
        self.timer.setSingleShot (True)
        self.reading = False
        self.paused_time_save = None
        self.data = []
        self.heure_debut = None

    def read_messages (self, nom_fichier) :
        """Méthode utilisée pour lire les fichiers contenants des messages,
        et executer les messages comme s'ils avaient envoyés par Ivy.
        /!\\ Les commandes de l'interface ne seront pas envoyées avec ce mode."""
        if not self.reading :
            self.reading = "MSG"
            with open (nom_fichier, 'r') as file :
                self.data = file.readlines ()
            self.heure_debut = time ()
            self.data = self.data [3:]
            self.data.reverse ()
            temps_message = int (self.data [-1].split ()[0])
            self.timer.timeout.connect (self.read_msg)
            self.timer.start (temps_message)
        else :
            self.timer.start (self.paused_time_save)

    def read_msg(self):
        """Méthode utilisée pour lire le message à la fin de self.data
        /!\\ Si ce message est une commande de l'interface, elle ne sera pas envoyée."""
        if len (self.data) == 0:
            self.timer.timeout.disconnect ()
            self.window.button_play.setChecked (False)
            self.window.button_play.setStyleSheet ("")
            self.window.playback_sgnl.emit([-1, 0, 0])
            self.reading = False
            return None
        line = self.data.pop (-1)
        try:
            words = line.split ()
            self.timer.start( (int(self.data[-1].split()[0]) - int(words[0])) if len (self.data)!= 0 else 1)
            self.window.playback_sgnl.emit([1, len(self.data), 1])
            rid = words[3]
            if words[2] == 'PosReport':
                self.window.backend.radio.on_posreg ("Lecteur", rid, words[4], words[5], words[6])
            elif words[2] == "ActuatorReport":
                self.window.backend.radio.on_captreg ("Lecteur", rid, words[4], words[5])
            elif words[2] == 'ActuatorDecl':
                self.window.backend.radio.on_actudecl ("Lecteur", rid, words[4], words[5], words[6],
                words[7], words[8], words[9])
            elif words[1] == 'Interface':
                if words[2] in ('PosCmd', 'PosCmdOrient'):
                    x, y, theta = words[4], words[5], (words[6] if len(words)==7 else None)
                    if self.window.inspecteur.check_robot(words[3]):
                        anc_texte = self.window.inspecteur.find(rid).qlineedit_pos_cmd.text()
                        texte = "{:04d} : {:04d}".format (int(float(x)), int(float(y)))
                        if theta is not None:
                            texte += " : {:03d}".format (int (float(theta)/3.141592654*180))
                        else :
                            texte += anc_texte[10:]
                        self.window.inspecteur.find(rid).qlineedit_pos_cmd.setText(texte)
                elif words[2] == "ActuatorCmd":
                    sid, valeur = words[4], words[5]
                    eqp_display = self.window.inspecteur.find(rid,sid)
                    if eqp_display is not None and isinstance(eqp_display, ACT):
                        eqp_display.updt_cmd(valeur)
        except Exception as bug:
            print ("La ligne [{}] pose un problème.\n{}".format (line, bug))
            self.timer.start (1)

    def read_commands (self, nom_fichier):
        """Méthode utilisée pour lire un fichier contenant des commandes de l'interface."""
        if self.reading:
            self.timer.start (self.paused_time_save)
        else :
            self.reading = "CMD"
            with open (nom_fichier, 'r') as file:
                self.data = file.readlines ()[3:]
            self.data.reverse ()
            temps_commande = int (self.data [-1].split ()[0])
            self.timer.timeout.connect (self.read_cmd)
            self.timer.start (temps_commande)

    def read_cmd (self):
        """Méthode appelée pour envoyer la dernière commande de self.data"""
        if len (self.data) == 0:
            self.timer.timeout.disconnect ()
            self.window.button_play.setChecked (False)
            self.window.button_play.setStyleSheet ("")
            self.window.playback_sgnl.emit([-1, 0, 0])
            self.reading = False
            return None
        line = self.data.pop (-1)
        try :
            words = line.split()
            self.timer.start( (int(self.data[-1].split()[0]) - int(words[0])) if len (self.data) != 0 else 1)
            self.window.playback_sgnl.emit([1, len(self.data), 0])
            rid = words[2]
            if words [1] in ('PosCmd', 'PosCmdOrient'):
                x, y, theta = words[3], words[4], (words[5] if len(words) == 6 else None)
                if self.window.backend.annu.check_robot(rid):
                    anc_texte = self.window.inspecteur.find(rid).qlineedit_pos_cmd.text()
                    texte = "{:04d} : {:04d}".format (int(float (x)), int(float(y)))
                    if theta is not None:
                        texte += " : {:03d}".format (int(float(theta)/3.141592654*180))
                    else :
                        texte += anc_texte[10:]
                    self.window.inspecteur.find(rid).qlineedit_pos_cmd.setText(texte)
                self.window.backend.sendposcmd_robot (rid, (x, y, (float(theta) if len (words) == 6 else None)))
            elif words [1] == 'Shutdown' :
                self.window.backend.stopandforget_robot (rid)
            elif words [1] == "Emergency" :
                self.window.backend.emergency_stop_robot (rid)
            elif words [1] == "ActuatorsRequest":
                self.window.backend.send_descr_cmd (rid)
            elif words [1] == "SpeedCmd":
                self.window.backend.send_speed_cmd (rid, words [3], words [4], float (words [5]))
            elif words [1] == "ActuatorCmd" :
                sid, val = words [3], words [4]
                self.window.backend.sendeqpcmd (rid, sid, val)
                eqp_display = self.window.inspecteur.find (rid,sid)
                if eqp_display is not None and isinstance(eqp_display, ACT):
                    eqp_display.updt_cmd (val)
        except Exception as bug:
            print ("La ligne [{}] pose un problème.\n{}".format (line, bug))
            self.timer.start (1)

    def on_play_button (self):
        """Message appelé après un appui sur le bouton play. Appelle la bonne fonction de lecture de fichier."""
        path = self.window.settings_dict["Enregistrement/Playback (Dernière Lecture)"]
        if path not in (None, ""):
            if "essages" in path :
                self.window.button_play.setChecked (True)
                self.window.button_play.setStyleSheet ("background-color: red")
                self.read_messages (path)
                self.window.playback_sgnl.emit([0, 0, 1])
            elif "ommand" in path :
                self.window.button_play.setChecked (True)
                self.window.button_play.setStyleSheet ("background-color: red")
                self.read_commands (path)
                self.window.playback_sgnl.emit([0, 0, 0])

    def on_stop_button (self):
        """Méthode appelée par un appui du bouton stop. Arrête la lecture du fichier."""
        if self.reading == "MSG":
            self.timer.timeout.disconnect ()
        elif self.reading == "CMD":
            self.timer.timeout.disconnect ()
        self.window.playback_sgnl.emit([-1, 0, 0])
        self.reading = False

    def on_pause_button (self):
        """Méthode appelée par un appui du bouton pause. Met la lecture du fichier en pause."""
        self.paused_time_save = self.timer.remainingTime ()
        self.window.playback_sgnl.emit([-2, 0, 0])
        self.timer.stop ()
