"""Module test_backend_radio.py - module de tests du module backend et du module radio"""

import os
import subprocess
import time
import pytest
import backend as bkd
import annuaire as anr
import ivy_radio as rdo
from utilitaire_test import read_ivytest_file, results_to_file

RADIO = rdo.Radio()
TEST_TIME = int(time.time())
# Il a été nécessaire de créer une Radio en commun car sinon, il était
# impossible d'exécuter plusieurs tests à la suite, le serveur ivy n'étant pas fermé
# Il persiste d'ailleurs des alertes indiquant que les sockets ne sont pas fermés

def test_backend_send_cmds(recwarn, capsys):
    """Test des envoi de commandes de la classe Backend"""
    #lancer l'enregistreur de messages
    try:
        subprocess.Popen(['python', 'utilitaire_test.py', 'backend_send_cmds'])
        with bkd.Backend(anr.Annuaire(), RADIO) as backend:
            time.sleep(0.5) # la radio a besoin de 0.5secondes pour se lancer à chaque fois.
            backend.track_robot('test')
            backend.annu.find('test').create_eqp('act', 'Actionneur', 0, 1, 1, None)
            backend.sendeqpcmd('test', 'act', 0) #ne marchera pas si pas robot ni eqp correspondant
            backend.sendeqpcmd('nope', 'act', 0)
            backend.sendposcmd_robot('test', (0, 0, None))
            backend.sendposcmd_robot('test', (0, 0, 0))
            backend.sendposcmd_robot('nope', (0, 0, 0))
            #signal émis pour arrêt de l'utilitaire de test
            backend.radio.send_cmd("StopIvyTest")

        #vérification de l'envoi des messages
        time.sleep(0.1)
        ivy_test_list = read_ivytest_file('backend_send_cmds')
        assert ('Radio@localhost', 'StopIvyTest') in ivy_test_list
        assert ('Radio@localhost', 'ActuatorCmd test act 0') in ivy_test_list
        assert ('Radio@localhost', 'PosCmd test 0,0') in ivy_test_list
        assert ('Radio@localhost', 'PosCmdOrient test 0,0,0') in ivy_test_list

    finally:
        results_to_file("backend_send_cmds", recwarn, capsys, TEST_TIME)

def test_backend_basic(recwarn, capsys):
    """Tests de la classe Backend, avec un fonctionnement "normal" """
    try:
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
            #backend.sendposcmd_robot('test', (1500, 1000, 0))
            backend.forget_robot("test")
    finally:
        results_to_file("backend_basic", recwarn, capsys, TEST_TIME)

def test_backend_agressif(recwarn, capsys):
    """Première batterie de tests de la classe Backend"""
    try:
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

    finally:
        # enregistrement des alertes et des sorties console
        results_to_file("backend_agressif.txt", recwarn, capsys, TEST_TIME)

def test_backend_record(recwarn, capsys):
    """Tests des méthodes record de backend"""
    try:
        with bkd.Backend(anr.Annuaire(), RADIO) as backend:
            time.sleep(0.5)
            backend.record("B")
            assert backend.record_state() == (False, False)
            backend.record("BMC")
            assert backend.record_state() == (True, True)
            backend.record("ED")
            assert backend.record_state() == (True, True)
            backend.record("EDM")
            assert backend.record_state() == (False, True)
            backend.record("BM")
            backend.record("EDC")
            assert backend.record_state() == (True, False)
            backend.record("EDMCS")
            assert backend.record_state() == (False, False)
            assert os.path.exists("messages.txt")
            assert os.path.exists("commandes.txt")
            #la fonction devrait être modifiée pour avoir un chemin demandé
            #risque d'effacer fichier non lié au test
            os.remove("messages.txt")
            os.remove("commandes.txt")
            backend.record("E")

    finally:
        results_to_file("backend_record", recwarn, capsys, TEST_TIME)

def test_radio_no_recep(recwarn, capsys):
    """Tests de la radio sans réception de messages"""
    try:
        assert rdo.temps(0.0) == '1970/01/01\t01:00:00.0'

    finally:
        # enregistrement des alertes et des sorties console
        results_to_file("radio_no_recep", recwarn, capsys, TEST_TIME)

def test_radio_recep(recwarn, capsys):
    """Tests de réception de messages"""
    try:
        RADIO.start()
        RADIO.register_start('all')
        test_util_args = ['python', 'utilitaire_test.py', 'test_radio_recep']
        test_util_args.append("TestCmd")
        test_util_args.append("PosReport test 0;0;0")
        test_util_args.append("CaptDecl test cpt osef")
        test_util_args.append("CaptReport test cpt 0")
        test_util_args.append("ActuatorDecl test cpt 0 1 1 osef")
        subprocess.Popen(test_util_args)
        time.sleep(0.8)
        RADIO.register_stop(False, False, 'all')
        RADIO.send_cmd("StopIvyTest")
        RADIO.stop()
        buffer = RADIO.msgsBuffer[1:]
        print(RADIO.msgsBuffer)
        assert buffer[0][1:] == ("IvyTest@localhost", "TestCmd")
        assert buffer[1][1:] == ("IvyTest@localhost", "PosReport test 0;0;0")
        assert buffer[2][1:] == ("IvyTest@localhost", "CaptDecl test cpt osef")

        ivy_test_list = read_ivytest_file('test_radio_recep')
        assert ('Radio@localhost', 'StopIvyTest') in ivy_test_list

    finally:
        results_to_file("radio_recep", recwarn, capsys, TEST_TIME)

def test_radio_backend_attached(recwarn, capsys):
    """Tests des méthodes de Radi necessitant une radio attachée"""
    RADIO.cmdsBuffer = []
    RADIO.msgsBuffer = []
    try:
        with bkd.Backend(anr.Annuaire(), RADIO) as backend:
            backend.record("SMC")
            test_util_args = ['python', 'utilitaire_test.py', 'radio_backend_attached']
            test_util_args.append("TestCmd")
            test_util_args.append("PosReport test 0;0;0")
            test_util_args.append("CaptDecl test cpt osef")
            test_util_args.append("CaptReport test cpt 0")
            test_util_args.append("ActuatorDecl test cpt 0 1 1 osef")
            subprocess.Popen(test_util_args)
            time.sleep(1)
            backend.record("ESMCD")
            assert os.path.exists("messages.txt")
            assert os.path.exists("commandes.txt") #meme précaution à prendre
            os.remove("messages.txt")
            os.remove("commandes.txt")
            RADIO.send_cmd("StopIvyTest")
            _ = read_ivytest_file('radio_backend_attached')

    finally:
        results_to_file("radio_backend_attached", recwarn, capsys, TEST_TIME)
