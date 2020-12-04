"""Module test_annuaire.py - module de tests du module annuaire"""

import pytest
import annuaire

def test_actionneur():
    """Tests de la classe Actionneur"""
    act_a = annuaire.Actionneur('act_a', 0, ["Désactivé", "Activé"])
    assert act_a.get_state() == (0, ["Désactivé", "Activé"])
    act_a.set_state(1)
    assert act_a.get_state() == (1, ["Désactivé", "Activé"])
    assert act_a.get_variete() == annuaire.Variete.BINAIRE

    act_b = annuaire.Actionneur('act_b', 1, ["Rentré", "Semi-déployé", "Sorti"])
    assert act_b.get_variete() == annuaire.Variete.DEROULANT
    assert act_b.get_state() == (1, ["Rentré", "Semi-déployé", "Sorti"])

    act_c = annuaire.Actionneur('act_c', 0, ["Fixe"])
    assert act_c.get_variete() == annuaire.Variete.FIXE
    act_c.set_state(1)
    assert act_c.get_state() == (0, ["Fixe"])

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

    act_a = annuaire.Actionneur('act_a', 0, ["Off", 'On'])
    robot_a.updt_act(act_a)
    assert robot_a.get_all_act() == ["act_a"]
    assert robot_a.get_state_act('act_a') == (0, ["Off", 'On'])

    act_a2 = annuaire.Actionneur('act_a', 0, ["Off", 'On', 'Jsp'])
    robot_a.updt_act(act_a2)
    assert robot_a.get_state_act('act_a') == (0, ["Off", 'On', 'Jsp'])

    robot_a.set_state_act('act_a', 1)
    assert robot_a.get_state_act('act_a') == (1, ["Off", 'On', 'Jsp'])
    assert robot_a.get_variete_act('act_a') == annuaire.Variete.DEROULANT

    robot_a.remove_act('act_a')
    assert robot_a.get_all_act() == []

def test_annuaire():
    """Tests de la classe Annuaire"""
    annu = annuaire.Annuaire()
    assert annu.get_all_robots() == []

    robot_a = annuaire.Robot('robot_a')
    act_a = annuaire.Actionneur('act_a', 0, ["Off", "On"])
    robot_a.updt_act(act_a)
    annu.add_robot(robot_a)
    assert annu.get_all_robots() == ["robot_a"]

    act_b = annuaire.Actionneur('act_b', 1, ["Off", "On"])
    annu.updt_robot_act('robot_a', act_b)
    assert annu.get_robot_all_act('robot_a') == ['act_a', 'act_b']

    annu.remove_robot_act('robot_a', 'act_b')
    assert annu.get_robot_all_act('robot_a') == ['act_a']

    assert annu.get_robot_act_variete('robot_a', 'act_a') == annuaire.Variete.BINAIRE

    assert annu.get_robot_act_state('robot_a', 'act_a') == (0, ["Off", "On"])

    assert annu.get_robot_pos('robot_a') == (1500, 1000, 0)

    annu.set_robot_pos('robot_a', 0, 0, 0)
    assert annu.get_robot_pos('robot_a') == (0, 0, 0)

    assert not annu.check_robot('robot_b')
