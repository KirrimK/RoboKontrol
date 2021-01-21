"""Module ivy_radio.py - module de gestion des communications via Ivy-python"""

from time import time, gmtime
from ivy.std_api import IvyStart, IvyStop, IvyInit, IvyBindMsg, IvySendMsg

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
        self.cmds_buffer = []
        self.msgs_buffer = []
        self.record_msgs = False
        self.record_cmds = False
        IvyInit (IVYAPPNAME,IVYAPPNAME+" is ready!")
        self.bus = "127.255.255.255:2010"
        self.nom = IVYAPPNAME

        IvyBindMsg (self.on_posreg, POS_REG)
        IvyBindMsg (self.on_captreg, CAPT_REG)
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
                if path is not None :
                    if path != "":
                        if path [-1] != "/":
                            path += "/"
                else :
                    path = ""
                timestamp_deb = time()
                with open ('{}messages{}.txt'.format (path, int (timestamp_deb)),'a') as fichier :
                    fichier.write ('{}\n\nTemps (ms)\tExpediteur\t\t\tMessage\n'.format (temps_deb (timestamp_deb)))
                    for (i, ligne) in enumerate (self.msgs_buffer) :
                        if i == 0:
                            PremierTemps = ligne [0]
                        fichier.write (temps (ligne[0], PremierTemps)+'\t\t'+ligne[1]+'\t\t'+ligne[2]+'\n')
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
                    fichier.write ('{}\n\nTemps (ms)\tCommande\n'.format (temps_deb(tps)))
                    for ligne in self.cmds_buffer :
                        if i == 0:
                            PremierTemps = ligne [0]
                        fichier.write (temps (ligne[0], PremierTemps)+'\t\t'+ligne[1]+'\n')
            if del_buffers :
                self.cmds_buffer = []
     #REACTIONS AUX REGEXPS

    def on_posreg (self, sender, *args):
        """Fonction faisant le lien entre Ivy et le thread de main
        Envoie un signal Qt contenant la position"""
        if self.record_msgs :
            message = "Posreport {} {} {} {}".format (args[0], args[1], args [2], args [3])
            self.msgs_buffer.append ((time(),str(sender).split ('@')[0], message))
        if self.backend.widget is not None :
            self.backend.widget.position_updated.emit ([i for i in args]+[time()])
        else:
            self.backend.premiers_messages.append (('pos',[i for i in args]+[time()]))

    def on_actudecl (self, sender, *args):
        """Fonction faisant le lien entre Ivy et le thread de main
        Envoie un signal Qt contenant la description d'un equipement"""
        if self.record_msgs :
            message = "ActuatorDecl {} {} {} {} {} {} {}".format (args [0], args [1], args [2], args [3],
                        args [4], args [5], args [6])
            self.msgs_buffer.append ((time(),str(sender).split ('@')[0], message))
        if self.backend.widget is not None :
            self.backend.widget.ActuDeclSignal.emit ([i for i in args])
        else :
            self.backend.premiers_messages.append (('actdcl',[i for i in args]))

    def on_captreg (self, sender, *args):
        """Fonction faisant le lien entre Ivy et le thread de main
        Envoie un signal Qt contenant un retour de capteur"""
        if self.record_msgs :
            message = "ActuatorReport {} {} {}".format (args[0], args [1], args [2])
            self.msgs_buffer.append ((time(),str(sender).split ('@')[0], message))
        if self.backend.widget is not None :
            self.backend.widget.equipement_updated.emit ([i for i in args]+[time()])
        else :
            self.backend.premiers_messages.append (('actrep',[i for i in args]))

    def send_cmd (self,cmd):
        """Envoie du texte vers le bus Ivy et le stocke optionnellement sur les tampons
        Input : _ cmd (str) : Le message à envoyer"""
        if self.record_cmds :
            self.cmds_buffer.append ((time(),cmd))
        if self.record_msgs :
            self.msgs_buffer.append ((time(),'Interface',cmd))
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
