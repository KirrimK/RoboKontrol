""" Module main.py - exécution principale """

import window
import sys
import backend as ben
if len (sys.argv) > 1 and sys.argv [1] in ["ivy", "Ivy"]:
    import ivy_radio as rdi
    print("Mode Ivy démarré.")
else:
    print("Mode Série démarré.")
    import serial_radio as rds

if __name__ == "__main__":
    with ben.Backend(rdi.Radio() if sys.argv[1] in ["ivy", "Ivy"] else rds.Radio(sys.argv[1])) as backend:
        window.main(backend)
