"""Module test_radio.py - module de tests du module radio"""

import os
import subprocess
import time
import pytest
import ivy_radio as rdo
from utilitaire_test import results_to_file, read_ivytest_file

#RADIO = rdo.Radio()
# Il a été nécessaire de créer une Radio en commun car sinon, il était
# impossible d'exécuter plusieurs tests à la suite, le serveur ivy n'étant pas fermé
# Il persiste d'ailleurs des alertes indiquant que les sockets ne sont pas fermés
# il semblerait que la façon dont sont effectués les test
# empêchent plusieurs tests fonctionnant avec des radios de s'exécuter. pourquoi?
# TODO: investiguer le problème de sockets et des radios

def test_radio_basic(recwarn, capsys):
    """Quelques tests basiques de bon fonctionnement de la radio"""
    pass
    results_to_file("radio_basic", recwarn, capsys)
