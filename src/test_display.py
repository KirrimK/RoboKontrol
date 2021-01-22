""" Module test_display.py - module de tests de display.py """
import sys
from PyQt5.QtWidgets import QApplication
import display as dsp
from utilitaire_test import results_to_file

def test_disp_annu(recwarn, capsys):
    """Tests de la classe DisplayAnnuaire"""
    try:
        app = QApplication(sys.argv)
        annu = dsp.DisplayAnnuaire(None)
        assert not annu.check_robot("bruh")
        assert annu.get_all_robots() == []
    finally:
        # enregistrement des alertes et des sorties console
        results_to_file("display_annuaire.txt", recwarn, capsys)
