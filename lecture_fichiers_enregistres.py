"""Module dédié au replay d'un fichier"""
from PyQt5.QtCore import QTimer
from time import time

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
    def readMsg (self):
        if len (self.data) == 0 :
            self.timer.timeout.disconnect (lambda : self.readMsg())
            self.reading = False
        else : 
            line = self.data.pop (-1)
            try :
                words = line.split ()
                if len (self.data)>0:
                    self.timer.start (int ((self.data[-1].split()[0]-int (words[0]))/1000))
                timestamp = self.heureDebut + int (words [0])/1000
                if words [2]== 'PosReport':
                    self.window.backend.onPosRegSignal (words [3:]+[timestamp])
                elif words [2] == "ActuatorReport":
                    self.window.backend.onCaptRegSignal (words [3:]+[timestamp])
                elif words[2] == 'ActuatorDecl':
                    self.window.backend.onActuDeclSignal (words [3:])
                elif words [1] == 'Interface':
                    print (' '.join (words [2:]))
            except Exception :
                print ("La ligne [{}] pose un problème.".format (line))
                self.timer.start (1)
    
    def readCommands (self, nomFichier):
        if self.reading:
            self.timer.start (self.pausedTimeSave)
        else :
            self.reading = "CMD"
            with open (nomFichier, 'r') as f :
                self.data = f.readlines ()[3:].reverse ()
            tempsCommande = int (self.data [-1].split ()[0])
            self.timer.timeout.connect (lambda : self.readCmd())
            self.timer.start (tempsCommande)
    def readCmd (self):
        if len (self.data) == 0:
            self.timer.timeout.disconnect (lambda : self.readCmd)
            self.reading = False
        else :
            try :
                words = self.data.pop (-1).split()
                self.timer.start (int ((self.data[-1].split()[0]-int (words[0]))/1000))
                if words [1] in ('PosCmd', 'PosCmdOrient'):
                    self.window.backend.sendposcmd_robot (words[2],words[3],words[4], 
                        (float (words[5]) if len (words) == 6 else None))
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
                line = self.data.pop (-1)
                print ("La ligne [{}] pose un problème.".format (line))
                self.timer.start (1)
    def onPlayButton (self):
        path = self.window.settings_dict ["Enregistrement/Playback (Dernière Lecture)"]
        if path not in (None, ""):
            if "essages" in path :
                self.readMessages (path)
            elif "ommand" in path :
                self.readCommands (path)
    def onStopButton (self):
        if self.reading == "MSG":
            self.timer.disconnect (lambda : self.readMsg)
        elif self.reading == "CMD":
            self.timer.disconnect (lambda : self.readCmd)
        self.reading = False
    def onPauseButton (self):
        self.pausedTimeSave = self.timer.remainingTime ()
        self.timer.stop ()
