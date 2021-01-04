"""Module utilitaire_test.py - Module annexe utilisé pendant les tests
(enregistre tous les messages passés sur Ivy, et les enregistre dans un fichier)"""

import os
import time
import sys
from ivy.std_api import IvyStart, IvyStop, IvyInit, IvyBindMsg, IvySendMsg

IVYAPPNAME = "IvyTest"
MSG = "(.*)"
STOPMSG = "StopIvyTest"

def results_to_file(test_name, warn_res, std_res, test_time=int(time.time())):
    """Fonction qui enregistre les résultats d'un test dans un fichier"""
    filepath = "pytest_custom_logs/{}.txt".format(test_time)
    dirpath = "pytest_custom_logs"
    os.makedirs(dirpath, exist_ok=True)
    with open(filepath, "a") as file:
        file.write("-- TEST: {} --\n".format(test_name))
        std_out = std_res.readouterr().out
        if std_out != "":
            file.write("Captured stdout:\n")
            file.write(std_out)
        if len(warn_res) > 0:
            file.write("\nCaptured Warnings:\n")
            for elt in warn_res:
                file.write(str(elt)+"\n")
            file.write("\n")

def read_ivytest_file(test_name):
    """Lit les messages enregistrés par l'utilitaire_ivytest,
    puis supprime le fichier temporaire"""
    file_name = "{}.txt".format(test_name)
    msg_list = []
    with open(file_name, 'r') as file:
        for line in file:
            line_split = line.strip().split("#")
            msg_list.append((line_split[0], line_split[1]))
    if os.path.isfile(file_name):
        os.remove(file_name)
    return msg_list

class TestRadio:
    """Objet connecté au channel Ivy, enregistre tous les messages
    Un compte à rebours (en secondes) peut être demandé
    pour déclencher l'arrêt automatique après un certain temps
    (afin d'éviter les threads qui continuent à tourner en arrière plan)
    """
    def __init__(self, test_name):
        IvyInit (IVYAPPNAME,IVYAPPNAME+" is ready!")
        self.bus = "127.255.255.255:2010"
        self.nom = IVYAPPNAME
        IvyBindMsg (self.on_msg, MSG)
        IvyBindMsg (self.on_stopmsg, STOPMSG)
        self.file_name = "{}.txt".format(test_name)
        with open(self.file_name, "w") as file:
            file.write("")

    def on_msg(self, sender, message):
        """Enregistre chaque message reçu sur Ivy"""
        with open(self.file_name, "a") as file:
            file.write("{}#{}\n".format(str(sender), str(message)))

    def send_cmd(self, cmd):
        """Envoie un message sur le bus Ivy"""
        IvySendMsg(cmd)

    def on_stopmsg(self, *args):
        """Exécuté quand la commande d'arrêt du test est enregistrée"""
        self.stop()

    def start(self):
        """Démarrage du serveur ivy"""
        IvyStart(self.bus)

    def stop(self, *args):
        """Arrêt du serveur ivy"""
        IvyStop()

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        test_nm = sys.argv[1]
        test_radio = TestRadio(test_nm)
        test_radio.start()
        if len(sys.argv) > 2:
            time.sleep(0.5)
            for msg in sys.argv[1:]:
                test_radio.send_cmd(msg)
    else:
        print("Arguments invalides")
