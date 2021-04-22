""" Module main.py - exécution principale """

import window
import sys
import backend as ben
if len (sys.argv) > 1 and sys.argv [1] in ["ivy", "Ivy"]:
    import ivy_radio as rd
    print("Mode Ivy démarré.")
else:
    print("Mode Série démarré.")
    import serial_radio as rd

if __name__ == "__main__":
    with ben.Backend(rd.Radio() if sys.argv[1] in ["ivy", "Ivy"] else rd.Radio(sys.argv[1])) as backend:
        window.main(backend)
