""" Module main.py - exécution principale """

import window
import sys
import backend as ben
from radios import ivyRadio, serialRadio
if len (sys.argv) > 1 and sys.argv [1] in ["ivy", "Ivy"]:
    print("Mode Ivy démarré.")
else:
    print("Mode Série démarré.")
    

if __name__ == "__main__":
    with ben.Backend(ivyRadio() if sys.argv[1] in ["ivy", "Ivy"] else serialRadio(sys.argv[1])) as backend:
        window.main(backend)
