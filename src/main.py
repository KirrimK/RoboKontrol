""" Module main.py - exécution principale """

import window
import sys
import backend as ben
if len (sys.argv) > 1 and sys.argv [1]=="Ivy":
    import ivy_radio as rd
else:
    import serial_radio as rd

if __name__ == "__main__":
    with ben.Backend(rd.Radio()) as backend:
        window.main(backend)
