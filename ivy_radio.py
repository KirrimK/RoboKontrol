from ivy.std_api import IvyStart, IvyStop, IvyInit, IvyBindMsg, IvySendMsg
#import annuaire
from time import sleep, time, gmtime, struct_time

IVYAPPNAME = 'Radio'

	#Informations
"""Le premier groupe de capture est le nom du robot"""
DESCR_REG = 'Description (.+) (.*)'
POS_REG = 'PosReport (.+) (.+);(.+);(.+)'
CAPT_REG = 'CaptReport (.+) (.*)'

	#Commands
"""Le premier argument sera le nom du robot"""
DESCR_CMD = "DescrCmd {}"
SPEED_CMD = "SpeedCmd {} {},{},{}"
POS_CMD =  "PosCmd {} {},{}"
POS_ORIENT_CMD = "PosCmdOrient {} {},{},{}"
KILL_CMD = "Shutdown {}"

MSG = '(.*)'

def temps (t):
    i = gmtime(t)
    return ('{:04d}/{:02d}/{:02d}\t{:02d}:{:02d}:{:02d}'.format (i.tm_year, i.tm_mon, i.tm_mday, i.tm_hour, i.tm_min, i.tm_sec)+'{:.3}'.format (t%1)[1:])

class Radio :
    def __init__ (self):
        self.backend = None
        self.cmdsBuffer = []
        self.msgsBuffer = []
        self.record_msgs = False
        self.record_cmds = False
        IvyInit (IVYAPPNAME,IVYAPPNAME+" is ready!")
        self.bus = "127.255.255.255:2010"
        self.nom = "radio"
        IvyBindMsg (self.on_posreg, POS_REG)
        IvyBindMsg (self.on_msg, MSG)
        IvyBindMsg (self.on_captreg, CAPT_REG)
        IvyBindMsg (self.on_descrreg, DESCR_REG)

    #ENREGISTREMENT

    def register_start (self, *args):
        if 'all' in args :
            args += ('msgs','cmds')
        if 'msgs' in args :
            self.record_msgs = True
        if 'cmds' in args :
            self.record_cmds = True

    def on_msg (self, sender, message):
        """Stocke les messages sous forme de tupple dans msgs"""
        if self.record_msgs :
            self.msgsBuffer.append ((time(),sender, message))
            
    def register_stop (self, save, *args):
        if 'all' in args :
            args += ('msgs','cmds')
        if 'msgs' in args :
            self.record_msgs = False
            if save :
                path = 'messages.txt' #à modifier avec un appel à une méthode qui demande le chemin à l'utilisateur
                with open (path,'a') as fichier :
                    fichier.write ('Jour\t\tHeure\t\tExpediteur\t\tMessage\n\n')
                    for ligne in self.msgsBuffer :
                        fichier.write (temps (ligne[0])+'\t'+str (ligne[1])+'\t'+ligne[2]+'\n')
            self.msgsBuffer = []
        if 'cmds' in args :
            self.record_cmds = False
            if save :
                path = 'commandes.txt' #à modifier avec un appel à une méthode qui demande le chemin à l'utilisateur
                with open (path,'a') as fichier :
                    fichier.write ('Jour\t\tHeure\t\tCommande\n\n')
                    for ligne in self.cmdsBuffer :
                        fichier.write (temps (ligne[0])+'\t'+str (ligne[1])+'\n')
            self.cmdsBuffer = []
        
    def on_posreg (self,*args):
        #print (args[1:])
        pass


    def on_captreg (self,*args):
        pass

    def on_descrreg (self,*args):
        pass

    def send_cmd (self,cmd):
        if self.record_cmds :
            self.cmdsBuffer.append ((time(),cmd))
        if self.record_msgs :
            self.msgsBuffer.append ((time(),'Commande de l\'interface',cmd))
        IvySendMsg (cmd)

    def start (self):
        IvyStart (self.bus)

    def stop(self):
        IvyStop()

if __name__ == '__main__' :
    #Tests du programme
    Radio1 = Radio ()
    Radio1.start()
    #Actual tests :
    


    #End tests
    Radio1.stop ()
    
    

