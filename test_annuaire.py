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
    act_a = annuaire.Actionneur('act_a', 0, 0, 1, "pascal")
    assert act_a.get_state() == (0, 0, 1)
    act_a.set_state(1)
    assert act_a.get_state() == (1, 0, 1)
    assert act_a.get_unit() == 'pascal'
    assert act_a.__str__() == "Actionneur [act_a] Val.: 1 (pascal) entre 0 et 1"

    act_b = annuaire.Actionneur('act_b', 1, 0, 2, "radians")
    assert act_b.get_state() == (1, 0, 2)
    assert act_b.get_unit() == 'radians'

    act_c = annuaire.Actionneur('act_c', 0, 0, 0, "volts")
    act_c.set_state(1)
    assert act_c.get_state() == (0, 0, 0)
    assert act_c.get_unit() == 'volts'

def test_actiocapteur():
    """Tests de la classe ActioCapteur"""
    act = annuaire.Actionneur("act", 0, 0, 100)
    cpt = annuaire.Capteur("cpt", 0)
    acpt = annuaire.ActioCapteur("acpt", act, cpt, "%")
    acpt.set_state((50, 55))
    assert acpt.get_state() == (50, 0, 100, 55)
    assert acpt.get_unit() == "%"
    assert isinstance(acpt.get_last_updt()[0], float)
    assert isinstance(acpt.get_last_updt()[1], float)
    assert acpt.__str__() == "ActCpt [acpt](%) Cpt: 55 Act: 50 entre 0 et 100"

def test_robot():
    """Tests de la classe Robot"""
    robot_a = annuaire.Robot('robot_a', equipements=[annuaire.Capteur("cpt", 1, "%")])
    assert robot_a.x == robot_a.get_pos()[0] == 1500
    assert robot_a.y == robot_a.get_pos()[1] == 1000
    assert robot_a.theta == robot_a.get_pos()[2] == 0
    assert robot_a.get_all_eqp() == ['cpt']

    robot_a.set_pos(0, 0, 0)
    assert robot_a.x == robot_a.get_pos()[0] == 0
    assert robot_a.y == robot_a.get_pos()[1] == 0
    assert robot_a.theta == robot_a.get_pos()[2] == 0

    act_a = annuaire.Actionneur('act_a', 0, 0, 1, "-")
    robot_a.updt_eqp(act_a)
    assert robot_a.get_all_eqp() == ['cpt', "act_a"]
    assert robot_a.get_state_eqp('act_a') == (0, 0, 1)
    assert robot_a.get_unit_eqp("act_a") == "-"
    assert robot_a.get_type_eqp('nope') is None

    act_a2 = annuaire.Actionneur('act_a', 0, 0, 2, '(nope)')
    robot_a.updt_eqp(act_a2)
    assert robot_a.get_state_eqp('act_a') == (0, 0, 2)

    robot_a.set_state_eqp('act_a', 1)
    assert robot_a.get_state_eqp('act_a') == (1, 0, 2)
    assert robot_a.get_type_eqp('act_a') == annuaire.Actionneur
    assert robot_a.get_type_eqp('cpt') == annuaire.Capteur

    robot_a.remove_eqp('act_a')
    robot_str = "Robot [robot_a]\n| Position: x:0 y:0 theta:0\n| Capteur [cpt] Val.:1 (%)\n"
    assert robot_a.__str__() == robot_str
    robot_a.remove_eqp('cpt')
    assert robot_a.get_all_eqp() == []

def test_annuaire():
    """Tests de la classe Annuaire"""
    annu = annuaire.Annuaire()
    assert annu.get_all_robots() == []
    assert annu.__str__() == "Annuaire:\n"

    robot_a = annuaire.Robot('robot_a')
    act_a = annuaire.Actionneur('act_a', 0, 0, 1, "rien")
    robot_a.updt_eqp(act_a)
    annu.add_robot(robot_a)
    assert annu.get_all_robots() == ["robot_a"]
    annu_str = "Annuaire:\nRobot [robot_a]\n"
    annu_str += "| Position: x:1500 y:1000 theta:0\n"
    annu_str += "| Actionneur [act_a] Val.: 0 (rien) entre 0 et 1\n"
    assert annu.__str__() == annu_str

    act_b = annuaire.Actionneur('act_b', 1, 0, 1, "(nope)")
    annu.updt_robot_eqp('robot_a', act_b)
    assert annu.get_robot_all_eqp('robot_a') == ['act_a', 'act_b']

    annu.remove_robot_eqp('robot_a', 'act_b')
    assert annu.get_robot_all_eqp('robot_a') == ['act_a']

    assert annu.get_robot_eqp_type('robot_a', 'act_a') == annuaire.Actionneur

    assert annu.get_robot_eqp_state('robot_a', 'act_a') == (0, 0, 1)

    assert annu.get_robot_pos('robot_a') == (1500, 1000, 0)

    annu.set_robot_pos('robot_a', 0, 0, 0)
    assert annu.get_robot_pos('robot_a') == (0, 0, 0)

    assert not annu.check_robot('robot_b')

    assert annu.set_robot_eqp_state('robot_a', 'act_a', 1) is None
    assert annu.get_robot_eqp_unit('robot_a', 'act_a') == 'rien'

    annu.remove_robot('robot_a')
    assert not annu.check_robot('robot_a')
    assert annu.get_all_robots() == []
