"""main.py"""
#TODO: regarder lib argsparse pour arguments ligne de cmd meilleurs
import window
import backend as ben
import annuaire as an
import ivy_radio as rd

if __name__ == "__main__":
    with ben.Backend(an.Annuaire(), rd.Radio()) as backend:
        window.main(backend)
