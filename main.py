"""main.py"""
#regarder lib argsparse pour arguments ligne de cmd meilleurs
import window
import backend as ben
import ivy_radio as rd

if __name__ == "__main__":
    with ben.Backend(rd.Radio()) as backend:
        window.main(backend)
