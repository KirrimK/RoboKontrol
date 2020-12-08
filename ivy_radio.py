from ivy.std_api import IvyStart, IvyStop, IvyInit, IvyBindMsg, IvySendMsg
#import annuaire
from time import sleep, time, gmtime, struct_time

IVYAPPNAME = 'Radio'

	#Informations
POS_REG = 'PosReport (.+) (.+);(.+);(.+)'
CAPT_REG = 'CaptReport (.+) (.*)'

	#Commands 
SPEED_CMD = "SpeedCmd {} {},{},{}"
POS_CMD =  "PosCmd {} {},{}"
POS_ORIENT_CMD = "PosCmdOrient {} {},{},{}"
KILL_CMD = "Shutdown {}"

MSG = '(.*)'

def temps ():
    t= time()
    i = gmtime(t)
    return ('{}/{}/{}\t{:02d}:{:02d}:{:02d}'.format (i.tm_year, i.tm_mon, i.tm_mday, i.tm_hour, i.tm_min, i.tm_sec)+'{:.3}'.format (t%1)[1:])

class Radio :
    def __init__ (self):
        self.record_all = False
        self.record_cmds = False
        IvyInit ("radio","radio ready!")
        self.bus = "127.255.255.255:2010"
        self.nom = "radio"
        IvyBindMsg (self.on_posreg, POS_REG)
        IvyBindMsg (self.on_msg, MSG)
        #IvyBindMsg (

    def on_msg (self, sender, message):
        if self.record_all :
            with open ('messages.txt','a') as fichier :
                fichier.write (str(sender) +'\t'+message + '\t' + temps ()+'\n')

    def on_posreg (self,*args):
        #print (args[1:])
        pass

    def start (self):
        IvyStart (self.bus)

    def stop(self):
        IvyStop()

    def send_cmd (self,cmd):
        if self.record_cmds :
            with open ('commands.txt','a') as fichier :
                fichier.write (cmd+'\t'+temps()+'\n')
        IvySendMsg (cmd)


if __name__ == '__main__' :

    #Tests du programme
    Radio1 = Radio ()
    Radio1.start()
    sleep (5)
    Radio1.send_cmd (POS_CMD.format('test',0,0))
    sleep (5)
    Radio1.stop ()
    
    

