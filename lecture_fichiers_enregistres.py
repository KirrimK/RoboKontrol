"""Module dédié au replay d'un fichier"""
import PyQt5
from time import sleep

def ReadFile (nom_fichier, TYPE, window):
    """Fonction de lecture de fichiers.
    Arguments :
        nom_fichier (str) : Path complet du fichier à lire
        TYPE (str) : "MSG" ou "CMD", choix du mode lecture
        window : utile pour lancer des appels de fonctions"""
    with open (nom_fichier, 'r') as fichier:
        data = fichier.readlines ()
    tempsAnc = 0
    if TYPE == "MSG" :   
        for line in data [3:]:
            try :
                words = line.split ()
                tempsNouv = int (words[0])/1000
                pause = tempsNouv - tempsAnc
                sleep (pause)
                tempsAnc = tempsNouv
                if words [2]== 'PosReport':
                    window.backend.widget.PosRegSignal.emit (words [3:])
                elif words [2] == "ActuatorReport":
                    window.backend.widget.CaptRegSignal.emit (words [3:])
                elif words[2] == 'ActuatorDecl':
                    window.backend.widget.ActuDeclSignal.emit (words [3:])
                elif words [1] == 'Commande_de_l\'interface':
                    print (' '.join (words [2:]))
            except Exception :
                print ("La ligne [{}] pose un problème.".format (line))
    if TYPE == "CMD":
        for line in data :
            try:
                words = line.split ()
                tempsNouv = int (words[0])/1000
                pause = tempsNouv - tempsAnc
                sleep (pause)
                tempsAnc = tempsNouv
                if words [1] in ('PosCmd', 'PosCmdOrient'):
                    window.backend.sendposcmd_robot (words[2],words[3],words[4], 
                        (float (words[5]) if len (words) == 6 else None))
                elif words [1] == 'Shutdown' :
                    window.backend.stopandforget_robot (words [2])
                elif words [1] == "Emergency" :
                    window.backend.emergency_stop_robot (words [2])
                elif words [1] == "ActuatorsRequest":
                    window.backend.send_descr_cmd (words [2])
                elif words [1] == "SpeedCmd":
                    window.backend.send_speed_cmd (words [2], words [3], words [4], float (words [5]))
                elif words [1] == "ActuatorCmd" :
                    window.backend.sendeqpcmd (words [2], words [3], words [4])
            except Exception :
                print ("La ligne [{}] pose un problème.".format (line))