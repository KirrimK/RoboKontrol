"""Module ivy_radio.py - module de gestion des communications via Ivy-python"""

from time import sleep, time, gmtime, struct_time
from ivy.std_api import IvyStart, IvyStop, IvyInit, IvyBindMsg, IvySendMsg

IVYAPPNAME = 'Radio'

	#Informations
"""Le premier groupe de capture est le nom du robot"""
#DESCR_REG = 'Description (.+) (.*)'
ACTU_DECL = 'ActuatorDecl (.*) (.*) (.*) (.*) (.*)'
POS_REG = 'PosReport (.+) (.+);(.+);(.+)'
CAPT_REG = 'CaptReport (.+) (.*)'

	#Commands
"""Le premier argument sera le nom du robot"""
#DESCR_CMD = "DescrCmd {}"
SPEED_CMD = "SpeedCmd {} {},{},{}"
POS_CMD =  "PosCmd {} {},{}"
POS_ORIENT_CMD = "PosCmdOrient {} {},{},{}"
ACTUATOR_CMD = "ActuatorCmd {} {} {}"
KILL_CMD = "Shutdown {}"

MSG = '(.*)'

def temps (t):
    """Input : t (float) : value given by time()

    Output : a formated string that gives a more explicit time than t"""
    i = gmtime(t)
    return '{:04d}/{:02d}/{:02d}\t{:02d}:{:02d}:{:02d}'.format (i.tm_year, i.tm_mon, i.tm_mday, i.tm_hour, i.tm_min, i.tm_sec)+'{:.3}'.format (t%1)[1:]

class Radio :
    """Classe de l'objet qui est connecté au channel Ivy

    Attributs :
    _ backend (backend.Backend) : objet faisant le lien entre l'annuaire et la radio
    _ cmdsBuffer (list) : Stocke les commandes envoyées sous forme de tuple (timestamp, commande)
    _ msgsBuffer (list) : Stocke tous les messages sous forme de tuple (timestamp, sender, message)
    _ record_msgs (bool) : Condition d'enregistrement de tous les messages
    _ record_cmds (bool) : Condition d'enregistrement des commandes envoyées
    _ bus (str) : Utile pour faire tourner Ivy
    _ nom (str) : Stocke l'IVYAPPNAME"""
    def __init__ (self):
        self.backend = None
        self.cmdsBuffer = []
        self.msgsBuffer = []
        self.record_msgs = False
        self.record_cmds = False
        IvyInit (IVYAPPNAME,IVYAPPNAME+" is ready!")
        self.bus = "127.255.255.255:2010"
        self.nom = IVYAPPNAME
        IvyBindMsg (self.on_posreg, POS_REG)
        IvyBindMsg (self.on_msg, MSG)
        IvyBindMsg (self.on_captreg, CAPT_REG)
        #IvyBindMsg (self.on_descrreg, DESCR_REG)
        IvyBindMsg (self.on_actudecl, ACTU_DECL)

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
        Stocke les messages sous forme de tupple dans msgsBuffer si le booléen self.record_msgs est True
        Vérifie si l'expéditeur est enregistré et l'enregistre si ce n'est pas fait."""
        if self.record_msgs :
            self.msgsBuffer.append ((time(),sender, message))
        nom_robot = sender.split ('@')[0]
        if not self.backend.annuaire.check_robot (nom_robot):
            self.backend.track_robot (nom_robot)

    def register_stop (self, save = True, del_buffers = True, *args):
        """Arrête un enregistrement, supprime optionellemnt le tampon, et le sauvegarde vers un document .txt
        Input : 
            _ save (bool) : condition d'enregistrement dans un document texte (True par défaut)
            _ del_buffers : condition d'effacement du tampon (True par défaut)
            _ args : autres arguments entrés ('all', 'msgs' et/ou 'cmds' (strings)) considérés comme un tupple"""
        if 'all' in args :
            args += ('msgs','cmds')
        if 'msgs' in args :
            self.record_msgs = False
            if save :
                path = 'messages.txt' #à modifier avec un appel à une méthode qui demande le chemin à l'utilisateur
                with open (path,'a') as fichier :
                    fichier.write ('Jour\t\tHeure\t\tExpediteur\t\tMessage\n\n')
                    for ligne in self.msgsBuffer :
                        fichier.write (temps (ligne[0])+'\t'+ligne[1]+'\t'+ligne[2]+'\n')
            if del_buffers :
                self.msgsBuffer = []
        if 'cmds' in args :
            self.record_cmds = False
            if save :
                path = 'commandes.txt' #à modifier avec un appel à une méthode qui demande le chemin à l'utilisateur
                with open (path,'a') as fichier :
                    fichier.write ('Jour\t\tHeure\t\tCommande\n\n')
                    for ligne in self.cmdsBuffer :
                        fichier.write (temps (ligne[0])+'\t'+ligne[1]+'\n')
            if del_buffers :
                self.cmdsBuffer = []
     #REACTIONS AUX REGEXPS

    def on_posreg (self, sender, rid, x, y, theta):
        """Input fait par IvyBindMsg
        Transmet les valeurs envoyées par le robot vers l'annuaire"""
        self.backend.annuaire.set_robot_pos (rid, float (x), float(y), float(theta))

    def on_actudecl (self, sender, *args):
        pass

    def on_captreg (self, sender, *args):
        #A modifier avec l'appel à une méthode qui change l'affichage des données
        pass

    def on_descrreg (self, sender, *args):
        #A modifier avec l'appel à une méthode qui enregistre le robot dans l'annuaire
        pass

    def send_cmd (self,cmd):
        """Envoie du texte vers le bus Ivy et le stocke optionnellement sur les tampons
        Input : _ cmd (str) : Le message à envoyer"""
        if self.record_cmds :
            self.cmdsBuffer.append ((time(),cmd))
        if self.record_msgs :
            self.msgsBuffer.append ((time(),'Commande de l\'interface',cmd))
        IvySendMsg (cmd)


    #Autres méthodes très utiles
    def start (self):
        """Démare la radio"""
        IvyStart (self.bus)

    def __exit__(self, *args):
        """Appelé automatiquement à l'arrêt du programme. Enlève la radio du bus Ivy."""
        IvyStop()

if __name__ == '__main__' :
    #Tests du programme
    Radio1 = Radio ()
    Radio1.start()
    #Actual tests :
    Radio1.register_start ('all')
    sleep (1)
    Radio1.send_cmd ("PosCmd test 0,1000")
    sleep (5)
    Radio1.send_cmd ("PosCmd test 1000,1500")
    sleep (5)
    Radio1.send_cmd ("PosCmd test 1500,1000")
    sleep (5)
    Radio1.register_stop (True, 'all')
    #End tests
