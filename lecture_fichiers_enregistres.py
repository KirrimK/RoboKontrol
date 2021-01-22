"""Module dédié au replay d'un fichier"""

from time import time
from PyQt5.QtCore import QTimer

class Lecteur :
    """Classe permettant la lecture des fichiers. S'initialise avec la fenêtre."""
    def __init__ (self, window):
        self.window = window
        self.timer = QTimer ()
        self.timer.setSingleShot (True)
        self.reading = False
        self.pausedTimeSave = None
        self.data = []
        self.heureDebut = None

    def readMessages (self, nomFichier) :
        """Méthode utilisée pour lire les fichiers contenants des messages, 
        et executer les messages comme s'ils avaient envoyés par Ivy.
        /!\\ Les commandes de l'interface ne seront pas envoyées avec ce mode."""
        if not self.reading :
            self.reading = "MSG"
            with open (nomFichier, 'r') as f :
                self.data = f.readlines ()
            self.heureDebut = time ()
            self.data = self.data [3:]
            self.data.reverse ()
            print (self.data[-1])
            tempsMessage = int (self.data [-1].split ()[0])
            self.timer.timeout.connect (lambda : self.readMsg())
            self.timer.start (tempsMessage)
        else :
            self.timer.start (self.pausedTimeSave)

    def readMsg(self):
        """Méthode utilisée pour lire le message à la fin de self.data
        /!\\ Si ce message est une commande de l'interface, elle ne sera pas envoyée."""
        
        line = self.data.pop (-1)
        try:
            words = line.split ()
            if len (self.data)>0:
                self.timer.start ((int (self.data[-1].split()[0])-int (words[0])))
                self.window.playback_sgnl.emit([1, len(self.data), 1])
            else :
                self.timer.timeout.disconnect ()
                self.window.button_play.setChecked (False)
                self.window.button_play.setStyleSheet ("background-color: lightgrey")
                self.reading = False
            if words [2]== 'PosReport':
                self.window.backend.radio.on_posreg ("Lecteur",words [3], words [4], words [5], words [6])
            elif words [2] == "ActuatorReport":
                self.window.backend.radio.on_captreg ("Lecteur",words [3], words [4], words [5])
            elif words[2] == 'ActuatorDecl':
                self.window.backend.radio.on_actudecl ("Lecteur",words [3], words [4], words [5], words [6],
                words [7],words [8])
            elif words [1] == 'Interface':
                if words [2] in ('PosCmd', 'PosCmdOrient'):
                    rid, x, y, theta = words [3], words [4], words [5], (words [6] if len (words)==7 else None)
                    if self.window.backend.annu.check_robot (words [3]):
                        anc_texte = self.window.inspecteur.find (rid).qlineedit_pos_cmd.text ()
                        texte = "{:04d} : {:04d}".format (int(float (x)), int(float(y)))
                        if theta is not None:
                            texte += " : {:03d}".format (int (float(theta)/3.141592654*180))
                        else :
                            texte += anc_texte [10:]
                        self.window.inspecteur.find (rid).qlineedit_pos_cmd.setText (texte)
                print (' '.join (words [2:]))
        except Exception :
            print ("La ligne [{}] pose un problème.".format (line))
            self.timer.start (1)


    def readCommands (self, nomFichier):
        """Méthode utilisée pour lire un fichier contenant des commandes de l'interface."""
        if self.reading:
            self.timer.start (self.pausedTimeSave)
        else :
            self.reading = "CMD"
            with open (nomFichier, 'r') as f :
                self.data = f.readlines ()[3:]
            self.data.reverse ()
            tempsCommande = int (self.data [-1].split ()[0])
            self.timer.timeout.connect (self.readCmd)
            self.timer.start (tempsCommande)

    def readCmd (self):
        """Méthode appelée pour envoyer la dernière commande de self.data"""
        line = self.data.pop (-1)
        try :
            words = line.split()
            if len (self.data)>0:
                self.timer.start ((int (self.data[-1].split()[0])-int (words[0])))
                self.window.playback_sgnl.emit([1, len(self.data), 0])
            else:
                self.timer.timeout.disconnect ()
                self.window.button_play.setChecked (False)
                self.window.button_play.setStyleSheet ("background-color: lightgrey")
                self.reading = False
            if words [1] in ('PosCmd', 'PosCmdOrient'):
                self.window.backend.sendposcmd_robot (words[2],(words[3],words[4],
                    (float (words[5]) if len (words) == 6 else None)))
            elif words [1] == 'Shutdown' :
                self.window.backend.stopandforget_robot (words [2])
            elif words [1] == "Emergency" :
                self.window.backend.emergency_stop_robot (words [2])
            elif words [1] == "ActuatorsRequest":
                self.window.backend.send_descr_cmd (words [2])
            elif words [1] == "SpeedCmd":
                self.window.backend.send_speed_cmd (words [2], words [3], words [4], float (words [5]))
            elif words [1] == "ActuatorCmd" :
                self.window.backend.sendeqpcmd (words [2], words [3], words [4])
        except Exception:
            print ("La ligne [{}] pose un problème.".format (line))
            self.timer.start (1)

    def onPlayButton (self):
        """Message appelé après un appui sur le bouton play. Appelle la bonne fonction de lecture de fichier."""
        path = self.window.settings_dict["Enregistrement/Playback (Dernière Lecture)"]
        if path not in (None, ""):
            if "essages" in path :
                self.window.button_play.setChecked (True)
                self.window.button_play.setStyleSheet ("background-color: red")
                self.readMessages (path)
                self.window.playback_sgnl.emit([0, 0, 1])
            elif "ommand" in path :
                self.window.button_play.setChecked (True)
                self.window.button_play.setStyleSheet ("background-color: red")
                self.readCommands (path)
                self.window.playback_sgnl.emit([0, 0, 0])

    def onStopButton (self):
        """Méthode appelée par un appui du bouton stop. Arrête la lecture du fichier."""
        if self.reading == "MSG":
            self.timer.timeout.disconnect ()
        elif self.reading == "CMD":
            self.timer.timeout.disconnect ()     
        self.window.playback_sgnl.emit([-1, 0, 0])
        self.reading = False

    def onPauseButton (self):
        """Méthode appelée par un appui du bouton pause. Met la lecture du fichier en pause."""
        self.pausedTimeSave = self.timer.remainingTime ()
        self.window.playback_sgnl.emit([-2, 0, 0])
        self.timer.stop ()
