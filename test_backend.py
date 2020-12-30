"""Module test_backend.py - module de tests du module backend"""

import subprocess
import time
import pytest
import backend as bkd
import annuaire as anr
import ivy_radio as rdo
from utilitaire_test import read_ivytest_file, results_to_file

RADIO = rdo.Radio()
# Il a été nécessaire de créer une Radio en commun car sinon, il était
# impossible d'exécuter plusieurs tests à la suite, le serveur ivy n'étant pas fermé
# Il persiste d'ailleurs des alertes indiquant que les sockets ne sont pas fermés
# TODO: investiguer le problème de sockets

def test_backend_send_cmds(recwarn, capsys):
    """Test des envoi de commandes de la classe Backend"""
    #lancer l'enregistreur de messages
    subprocess.Popen(['python', 'utilitaire_test.py', 'backend_send_cmds'])#, '0.5'])
    with bkd.Backend(anr.Annuaire(), RADIO) as backend:
        #backend.sendeqpcmd('test', 'act', 0) #ne marcheront pas si pas robot ni eqp correspondant
        #backend.sendeqpcmd('nope', 'act', 1)
        backend.radio.send_cmd("StopIvyTest") #TODO: semble ne rien faire

    #vérification de l'envoi des messages
    time.sleep(0.1)
    ivy_test_list = read_ivytest_file('backend_send_cmds')
    assert ('Radio@localhost', 'StopIvyTest') in ivy_test_list

    results_to_file("backend_send_cmds", recwarn, capsys)

def test_backend_basic(recwarn, capsys):
    """Tests de la classe Backend, avec un fonctionnement "normal" """
    with bkd.Backend(anr.Annuaire(), RADIO) as backend:
        backend.track_robot("test")
        print(backend)
        print(backend.__str__(True))
        backend.track_robot("test")
        assert backend.get_all_robots() == ["test"]
        assert backend.getdata_robot('test')[0] == (1500, 1000, 0)
        assert backend.getdata_robot('test')[1] == []
        assert isinstance(backend.getdata_robot('test')[2], float)
        backend.annu.find("test").create_eqp('cpt', 'Capteur', "deg")
        assert backend.getdata_robot('test')[1] == ['cpt']
        assert backend.getdata_eqp("test", 'cpt')[0] == anr.Capteur
        assert backend.getdata_eqp("test", 'cpt')[1] == 0
        assert backend.getdata_eqp("test", 'cpt')[3] is None
        assert backend.getdata_eqp("test", 'cpt')[4] == 'deg'
        backend.annu.find("test").create_eqp('act', 'Actionneur', 0, 1, 1, "deg")
        assert backend.getdata_robot('test')[1] == ['cpt', 'act']
        assert backend.getdata_eqp("test", 'act')[0] == anr.Actionneur
        assert backend.getdata_eqp("test", 'act')[1] == (None, 0, 1, 1)
        assert backend.getdata_eqp("test", 'act')[3] is None
        assert backend.getdata_eqp("test", 'act')[4] == 'deg'
        #backend.sendposcmd_robot('test', (1500, 1000, 0)) #TODO: ne fonctionne pas
        backend.forget_robot("test")

    results_to_file("backend_basic", recwarn, capsys)

def test_backend_agressif(recwarn, capsys):
    """Première batterie de tests de la classe Backend

    """
    start_test_time = int(time.time())
    backend_not_ready = bkd.Backend(print_flag=-1)
    with pytest.raises(Exception):
        with backend_not_ready as backend:
            pass
            # cette ligne ne devrait pas s'exécuter,
            # mais apparaît dans le coverage comme un miss
    backend_not_ready.attach_annu("pas_un_annuaire")
    backend_not_ready.attach_annu(anr.Annuaire())
    backend_not_ready.attach_radio("pas_une_radio")
    backend_not_ready.attach_radio(RADIO)
    backend_not_ready.print_flag = 0
    with backend_not_ready as backend:
        assert isinstance(backend.radio, rdo.Radio)
        assert isinstance(backend.annu, anr.Annuaire)
        backend.stopandforget_robot("test")
        assert backend.get_all_robots() == []
        backend.stop_radio()
        backend.stop_radio()
        backend.stopandforget_robot("test")
        backend.start_radio()
        backend.start_radio()
        backend.run_as_loop(0.15)
        backend.print_flag = 1
        backend.run_as_loop(0.15)
        backend.print_flag = 2
        backend.run_as_loop(0.15)
        backend.print_flag = -1
        backend.run_as_loop(0.15)

    # enregistrement des alertes et des sorties console
    results_to_file("backend_agressif.txt", recwarn, capsys, start_test_time)
