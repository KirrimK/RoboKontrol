"""Module utilisé pour commiuniquer en serial via un X-Bee avec le robot"""
import serial
from time import time, gmtime

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
        self.cmds_buffer = []
        self.msgs_buffer = []
        self.record_msgs = False
        self.record_cmds = False

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
