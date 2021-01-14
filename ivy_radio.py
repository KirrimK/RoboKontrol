"""Module ivy_radio.py - module de gestion des communications via Ivy-python"""
#TODO : Modifier fichier d'enregistrement (plusieurs + timestamps)

#TODO: remplacer par des signaux Qt et les connecter


from time import time, gmtime
from ivy.std_api import IvyStart, IvyStop, IvyInit, IvyBindMsg, IvySendMsg
from annuaire import Actionneur
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget

IVYAPPNAME = 'Radio'

	#Informations
"""Le premier groupe de capture est le nom du robot"""

ACTU_DECL = 'ActuatorDecl (.+) (.+) (.+) (.+) (.+) (.+) (.*)'
POS_REG = 'PosReport (.+) (.+) (.+) (.+)'
CAPT_REG = 'ActuatorReport (.+) (.+) (.+)'

	#Commands
"""Le premier argument sera le nom du robot"""
SPEED_CMD = "SpeedCmd {} {} {} {}"
POS_CMD =  "PosCmd {} {} {}"
POS_ORIENT_CMD = "PosCmdOrient {} {} {} {}"
ACTUATOR_CMD = "ActuatorCmd {} {} {}"
STOP_BUTTON_CMD = "Emergency {}"
KILL_CMD = "Shutdown {}"
DESCR_CMD = "ActuatorsRequest {}"

MSG = '(.*)'
def temps (t, pt):
    """Input : _timestamp (float) : donné par time ()
                    _ premier_timestamp : date du premier timestamp de la session d'enregistrement
        OutPut : str du temps en ms depuis le début de la session d'eregistrement"""
    return str (int(1000 * (t-pt)))

def temps_deb (timestamp):
    """Input : t (float) : value given by time()

    Output : a formated string that gives a more explicit time than t

    !!! Cette fonction est à l'heure d'hiver."""
    itm = gmtime(timestamp+1*3600)
    return '{:04d}/{:02d}/{:02d}\t{:02d}:{:02d}:{:02d}'.format (itm.tm_year, itm.tm_mon,
            itm.tm_mday, itm.tm_hour, itm.tm_min, itm.tm_sec) +'{:.3}'.format (timestamp%1)[1:]    


class WidgetRadio (QWidget):
    """Classe implémentée car les signaux Qt doivent être envoyés par des objets Qt
    Attributs : _radio (Radio) : l'objet parent auquel sont reliés les connections de signal."""
    PosRegSignal = pyqtSignal (list)
    CaptRegSignal = pyqtSignal (list)
    ActuDeclSignal = pyqtSignal (list)
    def __init__ (self, radio):
        super().__init__()
        self.radio = radio
        self.PosRegSignal.connect (lambda liste : self.radio.onPosRegSignal (liste))
        self.CaptRegSignal.connect (lambda liste : self.radio.onCaptRegSignal (liste))
        self.ActuDeclSignal.connect (lambda liste : self.radio.onActuDeclSignal (liste))
        

class Radio :

    """Classe de l'objet qui est connecté au channel Ivy

    Attributs :
    _ backend (backend.Backend) : objet faisant le lien entre l'annuaire et la radio
    _ widget (RadioWidget) : objet permettant d'envoyer des signaux Qt
    _ cmds_buffer (list) : Stocke les commandes envoyées sous forme de tuple (timestamp, commande)
    _ msgs_buffer (list) : Stocke tous les messages sous forme de tuple (timestamp, sender, message)
    _ record_msgs (bool) : Condition d'enregistrement de tous les messages
    _ record_cmds (bool) : Condition d'enregistrement des commandes envoyées
    _ bus (str) : Utile pour faire tourner Ivy
    _ nom (str) : Stocke l'IVYAPPNAME"""
    def __init__ (self):
        self.backend = None
        self.widget = None
        self.cmds_buffer = []
        self.msgs_buffer = []
        self.record_msgs = False
        self.record_cmds = False
        IvyInit (IVYAPPNAME,IVYAPPNAME+" is ready!")
        self.bus = "127.255.255.255:2010"
        self.nom = IVYAPPNAME
        
        IvyBindMsg (self.on_posreg, POS_REG)
        IvyBindMsg (self.on_msg, MSG)
        IvyBindMsg (self.on_captreg, CAPT_REG)
        IvyBindMsg (self.on_actudecl, ACTU_DECL)

    def launchQt (self):
        """Méthode appelée après le lancement de l'application
        Les Widgets ne peuvent exister que s'il y a une application Qt
        
        Initialise l'attribut self.widget"""
        self.widget = WidgetRadio (self)
        
    #ENREGISTREMENT

    def register_start (self, *args):
        """Change l'attribut record_msgs et/ou record_cmds vers True
        Input : 'all', 'msgs' et/ou 'cmds' (strings)"""
        if 'all' in args :
            args += ('msgs','cmds')
        if 'msgs' in args :
            self.record_msgs = True
        if 'cmds' in args :
            self.record_cmds = True

    def on_msg (self, sender, message):
        """Input fait par IvyBindMsg ('(.*)')
        Stocke les messages sous forme de tupple dans msgs_buffer
        si le booléen self.record_msgs est True
        Vérifie si l'expéditeur est enregistré et l'enregistre si ce n'est pas fait."""
        if self.record_msgs :
            self.msgs_buffer.append ((time(),str(sender), message))

    def register_stop (self, save = True, del_buffers = True, *args):
        """Arrête un enregistrement, supprime optionellemnt le tampon,
        et le sauvegarde vers un document .txt
        Input :
            _ save (bool) : condition d'enregistrement dans un document texte (True par défaut)
            _ del_buffers (bool) : condition d'effacement du tampon (True par défaut)
            _ args : autres arguments entrés ('all', 'msgs' et/ou 'cmds' (strings))
                considérés comme un tuple"""
        path = args [-1]
        if 'all' in args :
            args += ('msgs','cmds')
        if 'msgs' in args :
            self.record_msgs = False
            if save :
                if path != "":
                    if path [-1] != "/":
                        path += "/"
                timestamp_deb = time()
                with open ('{}messages{}.txt'.format (path, int (timestamp_deb)),'a') as fichier :
                    fichier.write ('{}\nJour\t\tHeure\t\tExpediteur\t\tMessage\n\n'.format (timestamp_deb))
                    for (i, ligne) in enumerate (self.msgs_buffer) :
                        if i == 0:
                            PremierTemps = ligne [0]
                        fichier.write (temps (ligne[0], PremierTemps)+'\t'+ligne[1]+'\t'+ligne[2]+'\n')
            if del_buffers :
                self.msgs_buffer = []
        if 'cmds' in args :
            self.record_cmds = False
            if save :
                if path != "":
                    if path [-1] != "/":
                        path += "/"
                tps = time ()
                with open ('{}commandes{}.txt'.format (path, int(tps)),'a') as fichier :
                    fichier.write ('{}\nJour\t\tHeure\t\tCommande\n\n'.format (temps_deb(tps)))
                    for ligne in self.cmds_buffer :
                        if i == 0:
                            PremierTemps = ligne [0]
                        fichier.write (temps (ligne[0], PremierTemps)+'\t'+ligne[1]+'\n')
            if del_buffers :
                self.cmds_buffer = []
     #REACTIONS AUX REGEXPS

    def on_posreg (self, sender, *args):
        """Fonction faisant le lien entre Ivy et le thread de main
        Envoie un signal Qt contenant la position"""
        self.widget.PosRegSignal.emit ([i for i in args])

    def onPosRegSignal (self, liste ):
        """Méthode appelée automatiquement par on_posreg
        Transmet les valeurs envoyées par le robot vers l'annuaire
        Input :
            [rid (str), x (str), y (str), theta (str)] (list)"""
        rid, x, y, theta = liste [0], liste [1], liste [2], liste [3]
        if self.backend is not None:
            if not self.backend.annu.check_robot (rid):
                self.backend.track_robot (rid)
                self.send_cmd (DESCR_CMD.format (rid))
            self.backend.annu.find (rid).set_pos (float (x), float(y), float(theta)*180/3.141592654)

    def on_actudecl (self, sender, *args):
        """Fonction faisant le lien entre Ivy et le thread de main
        Envoie un signal Qt contenant la description d'un equipement"""
        self.widget.ActuDeclSignal.emit ([i for i in args])
        
    def onActuDeclSignal (self, liste):
        """Fonction appelée automatiquement par on_actudecl.
        Ajoute l'actionnneur aid sur le robot rid.
        Si aid est le nom d'un capteur déjà présent sur le robot, la valeur est gardée.

        Input : [rid (str), aid (str), minV (str), maxV (str), step (str), droits (str), unit (str)] (list)"""
        rid, aid, minv, maxv, step, droits, unit = liste [0], liste [1], liste [2], liste [3], liste [4], liste [5], liste [6]
        if self.backend is not None:
            if droits == 'RW':
                val = False
                binaire = False
                if float (minv) + float (step) >= float (maxv) :
                    binaire = True
                if self.backend.annu.find (rid,aid) is not None :
                    val = True
                    valeur = self.backend.annu.find (rid,aid).get_state () [0]
                if binaire :
                    self.backend.annu.find (rid).create_eqp (aid, "Binaire")
                else :
                    self.backend.annu.find (rid).create_eqp (aid, "Actionneur",
                                                        float(minv), float(maxv), float(step), unit)
                if val:
                    self.backend.annu.find (rid,aid).set_state (valeur)
            elif droits == 'READ':
                add = False
                if not self.backend.annu.find (rid).check_eqp (aid):
                    add = True
                    val = None
                elif self.backend.annu.find (rid, aid).get_type () is not Actionneur :
                    add = True
                    val = self.backend.annu.find (rid, aid).get_state() [0]
                if add:
                    self.backend.annu.find (rid).create_eqp (aid, "Capteur", minv, maxv, step, unit)
                    self.backend.annu.find (rid, aid).set_state (val)


    def on_captreg (self, sender, *args):
        """Fonction faisant le lien entre Ivy et le thread de main
        Envoie un signal Qt contenant un retour de capteur"""
        self.widget.CaptRegSignal.emit ([i for i in args])
        
    def onCaptRegSignal (self, liste):
        """Fonction appelée automatiquement par on_captreg.
        Change la valeur du capteur sid sur le robot rid.
        Si aucun robot rid n'est connu, le robot est ajouté.
        Si le robot rid n'a pas de capteur sid, le capteur est ajouté.
        
        Input : [rid (str), sid (str), valeur (str)] (list)"""
        rid, sid, valeur = liste [0], liste [1], liste [2]
        if self.backend is not None:
            if not self.backend.annu.check_robot (rid):
                self.backend.track_robot (rid)
                self.send_cmd (DESCR_CMD.format (rid))
            if not self.backend.annu.find (rid).check_eqp (sid):
                self.backend.annu.find (rid).create_eqp (sid, "Capteur", None , None, None, None)
            self.backend.annu.find (rid,sid).set_state (float (valeur))

    def send_cmd (self,cmd):
        """Envoie du texte vers le bus Ivy et le stocke optionnellement sur les tampons
        Input : _ cmd (str) : Le message à envoyer"""
        if self.record_cmds :
            self.cmds_buffer.append ((time(),cmd))
        if self.record_msgs :
            self.msgs_buffer.append ((time(),'Commande de l\'interface',cmd))
        IvySendMsg (cmd)


    #Autres méthodes très utiles
    def start (self):
        """Démare la radio"""
        IvyStart (self.bus)

    def stop (self, *args):
        """Appelé automatiquement à l'arrêt du programme. Enlève la radio du bus Ivy."""
        IvyStop()

#if __name__ == '__main__' :
#    #Tests du programme
#    Radio1 = Radio ()
#    Radio1.start()
#    sleep (0.5) #/!\ Très important, la ligne précédente s'execute lentement
#    #Actual tests :
#    Radio1.send_cmd (POS_CMD.format ('test', 2000,0))
#    #End tests
#    sleep (1)
#    Radio1.stop ()
