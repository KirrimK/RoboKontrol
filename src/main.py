""" Module main.py - exécution principale """

import window
import sys
import backend as ben
import time
from radios import ivyRadio, serialRadio, ecalRadio

    

if __name__ == "__main__":

    radio =None

    if len (sys.argv) > 1 and sys.argv [1] in ["ivy", "Ivy"]:
        print("Mode Ivy démarré.")
        radio = ivyRadio()
    elif sys.argv [1].lower() =="ecal":
        print("Mode Ecal démarré.")
        radio = ecalRadio()
    else:
        print("Mode Série démarré.")
        radio = serialRadio(sys.argv[1])
        
    with ben.Backend (radio) as backend:
        window.main(backend)
