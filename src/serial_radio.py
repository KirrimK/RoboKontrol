"""Module utilisé pour commiuniquer en serial via un X-Bee avec le robot"""
import serial
import threading
from time import time, gmtime


ACTU_DECL = 'ActuatorDecl (.+) (.+) (.+) (.+) (.+) (.+) (.*)'
POS_REG = 'PosReport (.+) (.+) (.+) (.+)'
CAPT_REG = 'ActuatorReport (.+) (.+) (.+)'


SPEED_CMD = "SpeedCmd {} {} {} {}"
POS_CMD =  "PosCmd {} {} {}"
POS_ORIENT_CMD = "PosCmdOrient {} {} {} {}"
ACTUATOR_CMD = "ActuatorCmd {} {} {}"
STOP_BUTTON_CMD = "Emergency {}"
KILL_CMD = "Shutdown {}"
DESCR_CMD = "ActuatorsRequest {}"

def temps (tps, prem_tps):
    """Input : _timestamp (float) : donné par time ()
                    _ premier_timestamp : date du premier timestamp de la session d'enregistrement
        OutPut : str du temps en ms depuis le début de la session d'eregistrement"""
    return str (int(1000 * (tps - prem_tps)))

def temps_deb (timestamp):
    """Input : t (float) : value given by time()

    Output : a formated string that gives a more explicit time than t

    !!! Cette fonction est à l'heure d'été."""
    itm = gmtime(timestamp+2*3600)
    return '{:04d}/{:02d}/{:02d}\t{:02d}:{:02d}:{:02d}'.format (itm.tm_year, itm.tm_mon,
            itm.tm_mday, itm.tm_hour, itm.tm_min, itm.tm_sec) +'{:.3}'.format (timestamp%1)[1:]

class Radio:
    def __init__(self, ):
        self.backend = None
        self.thread_ecoute = threading.Thread ( target=self.ecoute,)
        self.cmds_buffer = []
        self.msgs_buffer = []
        self.record_msgs = False
        self.record_cmds = False
        self.listen = True        
        self.serialObject = serial.Serial('COM1', baudrate=9600)

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
        #correction du chemin d'enregistrement si nécessaire
        if path is not None:
            if path != "":
                if path [-1] != "/":
                    path += "/"
        else :
            path = ""
        tps = time()
        if 'all' in args:
            args += ('msgs','cmds')

        if 'msgs' in args :
            self.record_msgs = False
            if save:
                with open ('{}messages{}.txt'.format (path, int (tps)),'a') as fichier:
                    fichier.write('{}\n\nTemps (ms)\tExpediteur\t\t\tMessage\n'.format(temps_deb(tps)))
                    if self.msgs_buffer != []:
                        premier_temps = self.msgs_buffer[0][0]
                        for ligne in self.msgs_buffer:
                            fichier.write(temps(ligne[0], premier_temps)+'\t\t'+ligne[1]+'\t\t'+ligne[2]+'\n')
            if del_buffers:
                self.msgs_buffer = []

        if 'cmds' in args:
            self.record_cmds = False
            if save:
                with open('{}commandes{}.txt'.format (path, int(tps)),'a') as fichier:
                    fichier.write('{}\n\nTemps (ms)\tCommande\n'.format (temps_deb(tps)))
                    if self.cmds_buffer != []:
                        premier_temps = self.cmds_buffer[0][0]
                        for ligne in self.cmds_buffer:
                            fichier.write(temps(ligne[0], premier_temps)+'\t\t'+ligne[1]+'\n')
            if del_buffers:
                self.cmds_buffer = []
    def on_posreg (self, *args):
        """Fonction faisant le lien entre le thread d'écoute serial et le thread de main
        Envoie un signal Qt contenant la position"""
        if self.record_msgs :
            message = "PosReport {} {} {} {}".format (args[0]+'_ghost', args[1], args [2], args [3])
            self.msgs_buffer.append ((time(),args[0], message))
            self.backend.widget.record_signal.emit(1)
        if self.backend.widget is not None :
            self.backend.widget.position_updated.emit ([i for i in args]+[time()])
        else:
            self.backend.premiers_messages.append (('pos',[i for i in args]+[time()]))

    def on_actudecl (self, *args):
        """Fonction faisant le lien entre le thread d'écoute serial et le thread de main
        Envoie un signal Qt contenant la description d'un equipement"""
        if self.record_msgs :
            message = "ActuatorDecl {} {} {} {} {} {} {}".format (args [0]+'_ghost',
                            args [1], args [2], args [3], args [4], args [5], args [6])
            self.msgs_buffer.append ((time(),args[0], message))
            self.backend.widget.record_signal.emit(1)
        if self.backend.widget is not None :
            self.backend.widget.ActuDeclSignal.emit ([i for i in args])
        else :
            self.backend.premiers_messages.append (('actdcl',[i for i in args]))

    def on_captreg (self, *args):
        """Fonction faisant le lien entre le thread d'écoute serial et le thread de main
        Envoie un signal Qt contenant un retour de capteur"""
        if self.record_msgs :
            message = "ActuatorReport {} {} {}".format (args[0]+'_ghost', args [1], args [2])
            self.msgs_buffer.append ((time(),args [0], message))
            self.backend.widget.record_signal.emit(1)
        if self.backend.widget is not None :
            self.backend.widget.equipement_updated.emit ([i for i in args]+[time()])
        else :
            self.backend.premiers_messages.append (('actrep',[i for i in args]))

    #Envoi de commandes

    def send_cmd (self, cmd):
        """Méthode appelée par les méthodes de serial_radio. Envoie la commande cmd sur le port serial"""
        self.serialObject.write (cmd)

    def send_speed_cmd (self, rid, v_x, v_y, v_theta):
        """Méthode appelée par le backend. Envoie une commande de vitesse au robot rid."""
        self.send_cmd (SPEED_CMD.format (rid, v_x, v_y, v_theta))

    def send_pos_cmd (self, rid, x, y):
        """Méthode appelée par le backend. Envoie une commande de position non orientée au robot."""
        self.send_cmd (POS_CMD.format (rid, x, y))

    def send_pos_orient_cmd (self, rid, x, y, theta):
        """Méthode appelée par le backend. Envoie une commande de position orientée au robot."""
        self.send_cmd (POS_ORIENT_CMD.format (rid, x, y, theta))

    def send_act_cmd (self, rid, eid, val):
        """Méthode appelée par le backend. 
        Envoie la commande 'val' à l'actionneur 'eid' du robot 'rid'."""
        self.send_cmd (ACTUATOR_CMD.format (rid, eid, val))
    
    def send_stop_cmd (self, rid):
        """Méthode appelée par le backend. Stoppe les mouvements du robot rid"""
        self.send_cmd (STOP_BUTTON_CMD.format (rid))
        self.send_cmd (SPEED_CMD.format (rid, 0, 0, 0))

    def send_kill_cmd (self, rid):
        """Méthode appelée par le backend. Éteint le robot rid"""
        self.send_cmd (KILL_CMD.format (rid))

    def send_descr_cmd (self, rid):
        """Méthode appelée par le backend. Demande au robot rid de déclarer tout ses équipements."""
        self.send_cmd (DESCR_CMD.format (rid))

    #Autres méthodes très utiles

    def ecoute (self):
        while self.listen:
            message = self.serialObject.readline ()
            if message [0] == POS_REG [0]:
                self.on_posreg ()
            elif message [0] == ACTU_DECL [0]:
                self.on_actudecl ()
            elif message [0] == CAPT_REG [0]:
                self.on_captreg ()

    def start (self):
        """Démarre le thread d'écoute"""
        self.thread_ecoute.start()

    def stop (self, *args):
        """Appelé automatiquement à l'arrêt du programme. 
        Met la condition de bouclage du thread d'écoute à False"""
        self.listen = False