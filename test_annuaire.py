"""Module test_annuaire.py - module de tests du module annuaire"""

import annuaire

def test_equipement():
    """Tests de la classe Equipement"""
    eqp_a = annuaire.Equipement('eqp_a')
    assert isinstance(eqp_a.get_last_updt(), float)
    assert eqp_a.get_unit() is None
    assert eqp_a.get_state() is None
    assert eqp_a.set_state(None) is None

def test_capteur():
    """Tests de la classe Capteur"""
    cpt_a = annuaire.Capteur('cpt_a', 0, "V")
    assert cpt_a.get_unit() == "V"
    assert cpt_a.get_state() == 0
    cpt_a.set_state(10)
    assert cpt_a.get_state() == 10
    assert cpt_a.__str__() == "Capteur [cpt_a] Val.:10 (V)"

def test_actionneur():
    """Tests de la classe Actionneur"""
    act_a = annuaire.Actionneur('act_a', 0, 1, 1, "pascal")
    assert act_a.get_state() == (None, 0, 1, 1)
    act_a.set_state(1)
    assert act_a.get_state() == (1, 0, 1, 1)
    assert act_a.get_unit() == 'pascal'
    assert act_a.__str__() == "Act. [act_a] Val.: 1 (pascal) 0 -> 1 (1)"

    act_b = annuaire.Actionneur('act_b', 0, 1, 2, "radians")
    assert act_b.get_state() == (None, 0, 1, 2)
    assert act_b.get_unit() == 'radians'

    act_c = annuaire.Actionneur('act_c', 0, 0, 0, "volts")
    act_c.set_state(1)
    assert act_c.get_state() == (1, 0, 0, 0)
    assert act_c.get_unit() == 'volts'
    assert act_c.updt_cmd() is None
    assert act_c.get_last_cmd()

def test_binaire():
    """Tests de la clase Binaire"""
    bin_a = annuaire.Binaire('bin_a')
    assert bin_a.get_state() == (None, 0, 1, 1)
    assert bin_a.get_unit() is None

def test_robot():
    """Tests de la classe Robot"""
    robot_a = annuaire.Robot('robot_a', equipements=[annuaire.Capteur("cpt", 1, "%")])
    assert robot_a.x == robot_a.get_pos()[0] == 1500
    assert robot_a.y == robot_a.get_pos()[1] == 1000
    assert robot_a.theta == robot_a.get_pos()[2] == 0
    assert robot_a.get_all_eqp() == ['cpt']
    assert robot_a.check_eqp('cpt')

    robot_a.set_pos(0, 0, 0)
    assert robot_a.x == robot_a.get_pos()[0] == 0
    assert robot_a.y == robot_a.get_pos()[1] == 0
    assert robot_a.theta == robot_a.get_pos()[2] == 0

    robot_a.create_eqp('act_a', 'Actionneur', 0, 0, 1, '-')
    #act_a = annuaire.Actionneur('act_a', 0, 0, 1, "-")
    #robot_a.updt_eqp(act_a)
    assert robot_a.get_all_eqp() == ['cpt', "act_a"]
    eqp = robot_a.find('act_a')
    assert eqp.get_state() == (None, 0, 0, 1)
    assert eqp.get_unit() == "-"
    assert eqp.get_type() is annuaire.Actionneur

    act_a2 = annuaire.Actionneur('act_a', 0, 0, 2, '(nope)')
    robot_a.updt_eqp(act_a2)
    assert robot_a.find('act_a').get_state() == (None, 0, 0, 2)

    robot_a.find('act_a').set_state(1)
    assert robot_a.find('act_a').get_state() == (1, 0, 0, 2)
    assert robot_a.find('act_a').get_type() == annuaire.Actionneur
    assert robot_a.find('cpt').get_type() == annuaire.Capteur

    robot_a.remove_eqp('act_a')
    robot_str = "Robot [robot_a]\n| Position: x:0 y:0 theta:0\n| Capteur [cpt] Val.:1 (%)\n"
    assert robot_a.__str__() == robot_str
    robot_a.remove_eqp('cpt')
    assert robot_a.get_all_eqp() == []
    robot_a.create_eqp('eqp', 'Equipement')
    robot_a.create_eqp('bin', 'Binaire')
    robot_a.create_eqp('cpt', 'Capteur')
    robot_a.create_eqp('act', 'Actionneur', 0, 1, 1)
    robot_a.create_eqp('cpt2', 'Capteur', 'stonks')
    assert robot_a.get_all_eqp() == ['eqp', 'bin', 'cpt', 'act', 'cpt2']
    assert robot_a.find('osef') is None

def test_annuaire():
    """Tests de la classe Annuaire"""
    annu = annuaire.Annuaire()
    assert annu.get_all_robots() == []
    assert annu.__str__() == "Annuaire:\n"

    robot_a = annuaire.Robot('robot_a')
    act_a = annuaire.Actionneur('act_a', 0, 1, 1, "rien")
    robot_a.updt_eqp(act_a)
    annu.add_robot(robot_a)
    assert annu.get_all_robots() == ["robot_a"]
    annu_str = "Annuaire:\nRobot [robot_a]\n"
    annu_str += "| Position: x:1500 y:1000 theta:0\n"
    annu_str += "| Act. [act_a] Val.: None (rien) 0 -> 1 (1)\n"
    assert annu.__str__() == annu_str

    act_b = annuaire.Actionneur('act_b', 1, 0, 1, "(nope)")
    annu.find('robot_a').updt_eqp(act_b)
    assert annu.find('robot_a').get_all_eqp() == ['act_a', 'act_b']

    annu.find('robot_a').remove_eqp('act_b')
    assert annu.find('robot_a').get_all_eqp() == ['act_a']

    assert annu.find('robot_a', 'act_a').get_type() == annuaire.Actionneur

    assert annu.find('robot_a', 'act_a').get_state() == (None, 0, 1, 1)

    assert annu.find('robot_a').get_pos() == (1500, 1000, 0)

    annu.find('robot_a').set_pos(0, 0, 0)
    assert annu.find('robot_a').get_pos() == (0, 0, 0)

    assert not annu.check_robot('robot_b')

    assert annu.find('robot_a', 'act_a').set_state(1) is None
    assert annu.find('robot_a', 'act_a').get_unit()== 'rien'

    annu.remove_robot('robot_a')
    assert not annu.check_robot('robot_a')
    assert annu.get_all_robots() == []
    assert annu.find("osef") is None
