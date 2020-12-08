"""Module test_annuaire.py - module de tests du module annuaire"""

import pytest
import annuaire

def test_actionneur():
    """Tests de la classe Actionneur"""
    act_a = annuaire.Actionneur('act_a', 0, 0, 1, "pascal")
    assert act_a.get_state() == (0, 0, 1)
    act_a.set_state(1)
    assert act_a.get_state() == (1, 0, 1)
    assert act_a.get_unit() == 'pascal'

    act_b = annuaire.Actionneur('act_b', 1, 0, 2, "radians")
    assert act_b.get_state() == (1, 0, 2)
    assert act_b.get_unit() == 'radians'

    act_c = annuaire.Actionneur('act_c', 0, 0, 0, "volts")
    act_c.set_state(1)
    assert act_c.get_state() == (0, 0, 0)
    assert act_c.get_unit() == 'volts'

def test_robot():
    """Tests de la classe Robot"""
    robot_a = annuaire.Robot('robot_a')
    assert robot_a.x == robot_a.get_pos()[0] == 1500
    assert robot_a.y == robot_a.get_pos()[1] == 1000
    assert robot_a.theta == robot_a.get_pos()[2] == 0
    assert robot_a.actionneurs == {}

    robot_a.set_pos(0, 0, 0)
    assert robot_a.x == robot_a.get_pos()[0] == 0
    assert robot_a.y == robot_a.get_pos()[1] == 0
    assert robot_a.theta == robot_a.get_pos()[2] == 0

    act_a = annuaire.Actionneur('act_a', 0, 0, 1, "(-)")
    robot_a.updt_act(act_a)
    assert robot_a.get_all_act() == ["act_a"]
    assert robot_a.get_state_act('act_a') == (0, 0, 1)

    act_a2 = annuaire.Actionneur('act_a', 0, 0, 2, '(nope)')
    robot_a.updt_act(act_a2)
    assert robot_a.get_state_act('act_a') == (0, 0, 2)

    robot_a.set_state_act('act_a', 1)
    assert robot_a.get_state_act('act_a') == (1, 0, 2)
    assert robot_a.get_type_act('act_a') == annuaire.Actionneur

    robot_a.remove_act('act_a')
    assert robot_a.get_all_act() == []

def test_annuaire():
    """Tests de la classe Annuaire"""
    annu = annuaire.Annuaire()
    assert annu.get_all_robots() == []

    robot_a = annuaire.Robot('robot_a')
    act_a = annuaire.Actionneur('act_a', 0, 0, 1, "(rien)")
    robot_a.updt_act(act_a)
    annu.add_robot(robot_a)
    assert annu.get_all_robots() == ["robot_a"]

    act_b = annuaire.Actionneur('act_b', 1, 0, 1, "(nope)")
    annu.updt_robot_act('robot_a', act_b)
    assert annu.get_robot_all_act('robot_a') == ['act_a', 'act_b']

    annu.remove_robot_act('robot_a', 'act_b')
    assert annu.get_robot_all_act('robot_a') == ['act_a']

    assert annu.get_robot_act_type('robot_a', 'act_a') == annuaire.Actionneur

    assert annu.get_robot_act_state('robot_a', 'act_a') == (0, 0, 1)

    assert annu.get_robot_pos('robot_a') == (1500, 1000, 0)

    annu.set_robot_pos('robot_a', 0, 0, 0)
    assert annu.get_robot_pos('robot_a') == (0, 0, 0)

    assert not annu.check_robot('robot_b')
