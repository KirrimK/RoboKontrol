import serial
import threading
from time import time, gmtime
from ivy.std_api import IvyStart, IvyStop, IvyInit, IvyBindMsg, IvySendMsg
import logging




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
    def __init__(self):
        self.backend = None
        self.cmds_buffer = []
        self.msgs_buffer = []
        self.record_msgs = False
        self.record_cmds = False
        self.messages={}

    def saveSent (self,cmd):
        """Methode qui sauvegarde les commandes envoyées par l'interface"""
        if self.record_cmds :
            self.cmds_buffer.append ((time(),cmd))
        if self.record_msgs :
            txt = cmd.split ()
            txt [1] = txt[1]+'_ghost'
            txt = " ".join (txt)
            self.msgs_buffer.append ((time(),'Interface',txt))
        if self.record_cmds or self.record_msgs:
            self.backend.widget.record_signal.emit(1)

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

    def on_posreg (self, rid, x, y, theta):
        """Fonction faisant le lien entre le thread d'écoute serial et le thread de main
        Envoie un signal Qt contenant la position"""
        if self.record_msgs :
            message = "PosReport {} {} {} {}".format (rid+'_ghost', x, y, theta)
            self.msgs_buffer.append ((time(),rid, message))
            self.backend.widget.record_signal.emit(1)
        if self.backend.widget is not None :
            self.backend.widget.position_updated.emit ([rid, x, y, theta, time()])
        else:
            self.backend.premiers_messages.append (('pos',[rid, x, y, theta, time()]))

    def on_actudecl (self, rid, eid, mini, maxi, step, rights, unit):
        """Fonction faisant le lien entre le thread d'écoute serial et le thread de main
        Envoie un signal Qt contenant la description d'un equipement"""
        if self.record_msgs :
            message = "ActuatorDecl {} {} {} {} {} {} {}".format (rid+'_ghost',
                            eid, mini, maxi, step, rights, unit)
            self.msgs_buffer.append ((time(),rid, message))
            self.backend.widget.record_signal.emit(1)
        if self.backend.widget is not None :
            self.backend.widget.ActuDeclSignal.emit ([rid, eid, mini, maxi, step, rights, unit])
        else :
            self.backend.premiers_messages.append (('actdcl',[rid, eid, mini, maxi, step, rights, unit]))

    def on_captreg (self, rid, eid, val):
        """Fonction faisant le lien entre le thread d'écoute serial et le thread de main
        Envoie un signal Qt contenant un retour de capteur"""
        if self.record_msgs :
            message = "ActuatorReport {} {} {}".format (rid+'_ghost', eid, val)
            self.msgs_buffer.append ((time(),rid, message))
            self.backend.widget.record_signal.emit(1)
        if self.backend.widget is not None :
            self.backend.widget.equipement_updated.emit ([rid, eid, val, time()])
        else :
            self.backend.premiers_messages.append (('actrep',[rid, eid, val]))

    #Envoi de commandes


    def send_speed_cmd (self, rid, v_x, v_theta):
        """Méthode appelée par le backend. Envoie une commande de vitesse au robot rid."""
        self.send_cmd (self.messages["SPEED_CMD"].format (v_x, v_theta))

    def send_pos_cmd (self, rid, x, y):
        """Méthode appelée par le backend. Envoie une commande de position non orientée au robot."""
        self.send_cmd (self.messages["POS_CMD"].format (x, y))

    def send_pos_orient_cmd (self, rid, x, y, theta):
        """Méthode appelée par le backend. Envoie une commande de position orientée au robot."""
        self.send_cmd (self.messages["POS_ORIENT_CMD"].format (x, y, theta))

    def send_act_cmd (self, rid, eid, val):
        """Méthode appelée par le backend. 
        Envoie la commande 'val' à l'actionneur 'eid' du robot 'rid'."""
        self.send_cmd (self.messages["ACTUATOR_CMD"].format (eid, val))
    
    def send_stop_cmd (self, rid):
        """Méthode appelée par le backend. Stoppe les mouvements du robot rid"""
        self.send_cmd (self.messages["STOP_BUTTON_CMD"].format ())
        self.send_cmd (self.messages["SPEED_CMD"].format (0, 0, 0))

    def send_kill_cmd (self, rid):
        """Méthode appelée par le backend. Éteint le robot rid"""
        self.send_cmd (self.messages["KILL_CMD"].format ())

    def send_descr_cmd (self, rid):
        """Méthode appelée par le backend. Demande au robot rid de déclarer tout ses équipements."""
        self.send_cmd (self.messages["DESCR_CMD"].format ())

    #Autres méthodes très utiles

    

    
class serialRadio(Radio):
    def __init__(self, nom_port):
        Radio.__init__(self)
        #Defnition des messages et commandes pouvant passer par la serial Radio
        self.messages['ACTU_DECL']='b {} {} {} {} {} {}'#B  indicatifEquipement valMin valMax step droits unité 
        self.messages['POS_REG']='r {} {} {}'#R  x y theta
        self.messages['CAPT_REG']='c {} {}'#C indicatifCapteur valeur

        
        self.messages["SPEED_CMD"]="v {} {}\n"#S vX vY vThetaself.messages["POS_CMD"]="P {} {} {}\n"#P indicatifRobot x y
        self.messages["POS_ORIENT_CMD"] = "o {} {} {}\n" #O x   y   theta
        self.messages["POS_CMD"]="p {} {}\n"#P x   y
        self.messages["ACTUATOR_CMD"] = "a {} {}\n"#A indicatifEquipement valeur
        self.messages["STOP_BUTTON_CMD"] = "s\n"#E
        self.messages["KILL_CMD"] = "k\n"#K 
        self.messages["DESCR_CMD"] = "d\n"#D 
        self.thread_ecoute = threading.Thread ( target=self.ecoute,)
        self.listen = True        
        self.serialObject = serial.Serial (port = nom_port, baudrate=57600, timeout =1)
    def start (self):
        """Démarre le thread d'écoute"""
        self.thread_ecoute.start()
    def stop (self, *args):
        """Appelé automatiquement à l'arrêt du programme. 
        Met la condition de bouclage du thread d'écoute à False"""
        self.listen = False

    def ecoute (self):
        """Fonction executée dans un thread séparé. 
        Lit l'entrée serie et appelle les fonctions concernées si elle reconnait un message de robot.
        S'arrête quand le booléen listen est mis à False."""
        while self.listen:
            try:
                message = self.serialObject.readline ()
                message = message.decode ()
                if len (message) != 0:
                    if message [0] == self.messages["POS_REG"] [0]:
                        args = message.split (' ')
                        if len(args[0])==1:
                            self.on_posreg ("serial", args [1], args [2], args [3])
                    elif message [0] == self.messages["ACTU_DECL"] [0]:
                        args = message.split (' ')
                        if len(args[0])==1:
                            self.on_actudecl ("serial", args [1], args [2], args [3], args [4], args [5], args [6])
                    elif message [0] == self.messages["CAPT_REG"] [0]:
                        args = message.split (' ')
                        if len(args[0])==1:
                            self.on_captreg ("serial", args [1], args [2])
            except Exception as e:
                print(e)
    def send_cmd (self, cmd):
        """Méthode appelée par les méthodes de serial_radio. Envoie la commande cmd sur le port serial"""
        self.serialObject.write (cmd.encode ('utf-8'))


class ivyRadio (Radio):
    """Classe de radio permettant la connection à un bus Ivy. Servait à des fins de debug de l'IHM avant le passage au serial"""
    def __init__(self):
        Radio.__init__(self)
        self.nom = 'Radio'
        IvyInit (self.nom,self.nom+" is ready!")
        self.bus = "127.255.255.255:2010"
        #Definition des messages et commandes Ivy
        self.messages['ACTU_DECL']='ActuatorDeclare {} {} {} {} {} {}'#B indicatifEquipement valMin valMax step droits unité 
        self.messages['POS_REG']='PosReport {} {} {}'#R x y theta
        self.messages['CAPT_REG']='CaptReport {} {}'#C indicatifCapteur valeur

        self.messages["POS_CMD"]="PosCommand {} {}\n"#P  x   y
        self.messages["SPEED_CMD"]="SpeedCommand {} {}\n"#S vX vTheta
        self.messages["POS_CMD"]="P {} {}\n"#P x y
        self.messages["POS_ORIENT_CMD"] = "PosOrientCommand {} {} {}\n" #O  x   y   theta
        self.messages["ACTUATOR_CMD"] = "ActuatorCommand {} {}\n"#A indicatifEquipement valeur
        self.messages["STOP_BUTTON_CMD"] = "Emmergency\n"#E
        self.messages["KILL_CMD"] = "Kill\n"#K
        self.messages["DESCR_CMD"] = "DecriptionCommand\n"#D

        IvyBindMsg (self.onBind1, self.messages["POS_REG"].format ('(.+)','(.+)','(.+)'))
        IvyBindMsg (self.onBind2, self.messages["CAPT_REG"].format('(.+)','(.+)'))
        IvyBindMsg (self.onBind3, self.messages["ACTU_DECL"].format('(.+)','(.+)','(.+)','(.+)','(.+)','(.+)'))
    
    def onBind1 (self, sender, x, y, theta):
        """Fonction servant à se débarasser de l'objet sender donné par le bind Ivy"""
        self.on_posreg("rid", x, y, theta)
    def onBind2 (self, sender, sid, val):
        """Fonction servant à se débarasser de l'objet sender donné par le bind Ivy"""
        self.on_captreg("rid", sid, val)
    def onBind3 (self, sender, sid, mini, maxi, step, droits, unit):
        """Fonction servant à se débarasser de l'objet sender donné par le bind Ivy"""
        self.on_actudecl("rid", sid, mini, maxi, step, droits, unit)

    def send_cmd (self,cmd):
        """Envoie du texte vers le bus Ivy et le stocke optionnellement sur les tampons
        Input : _ cmd (str) : Le message à envoyer"""
        self.saveSent(cmd)
        IvySendMsg (cmd)

    def start (self):
        """Démare la radio"""
        IvyStart (self.bus)
        logging.getLogger('Ivy').setLevel(logging.WARN)

    def stop (self, *args):
        """Appelé automatiquement à l'arrêt du programme. Enlève la radio du bus Ivy."""
        IvyStop()
