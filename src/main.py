""" Module main.py - exécution principale """

import window
import sys
import backend as ben
import time
from radios import ivyRadio, serialRadio, ecalRadio

    

if __name__ == "__main__":

    radio =None

    if len (sys.argv) > 1 and sys.argv[1] in ["ivy", "Ivy"]:
        print("Mode Ivy démarré.")
        radio = ivyRadio()

    elif len (sys.argv) > 1 and sys.argv[1].lower() =="ecal":
        print("Mode Ecal démarré.")
        radio = ecalRadio()

    elif len (sys.argv) > 1 and ("COM" in sys.argv [1] or "tty" in sys.argv [1]):
        print("Mode Série démarré.")
        radio = serialRadio(sys.argv[1])
    elif len (sys.argv) > 1 and sys.argv[1].lower() == "-h":
        print("Usage : python main.py [mode]\n\t[mode] needs to be either :\n\t\t-h\t:  Displays this help\n\t\tivy\t:  launches roboKontrol in ivy mode\n\t\tecal\t:  launches roboKontrol in eCAL mode\n\t\t[name of a serial port]\t: launches roboKontrol on serial mode")
    else:
        print ("Erreur :\nUsage : python main.py [mode]\n\t[mode] needs to be either :\n\t\t-h\t:  Displays this help\n\t\tivy\t:  launches roboKontrol in ivy mode\n\t\tecal\t:  launches roboKontrol in eCAL mode\n\t\t[name of a serial port]\t: launches roboKontrol on serial mode")


    if radio is not None:    
        with ben.Backend (radio) as backend:
            window.main(backend)
