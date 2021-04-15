""" Module display.py - widgets associés à l'affichage des informations """

import time
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QGroupBox, QHBoxLayout, QVBoxLayout, \
        QLineEdit, QLCDNumber, QScrollArea, QFrame, QProgressBar, QTabWidget, QSpacerItem, \
        QSlider, QGridLayout, QCheckBox, QDoubleSpinBox
from PyQt5.QtCore import pyqtSlot, Qt, QSize, QTimer
import annuaire as anr

EMERGENCY_BUTTON = "QPushButton{background-color: rgb(180,0,0); border: 1px solid rgb(100,0,0)}" \
                "QPushButton:hover{background-color: rgb(200,0,0);border: 1px solid rgb(60,0,0)}" \
                "QPushButton:pressed{background-color: red;border: 1px solid rgb(60,0,0)}"

READONLY_BUTTON = "QPushButton{background-color: rgb(0,0,180); border: 1px solid rgb(0,0,100)}" \
                "QPushButton:hover{background-color: rgb(0,0,200);border: 1px solid rgb(0,0,60)}" \
                "QPushButton:pressed{background-color: blue;border: 1px solid rgb(0,0,60)}"

# QtWidgets size
QLCD_SIZE1, QLCD_SIZE2 = QSize(60, 20), QSize(80, 20)
# Alignment
QT_CENTER, QT_RIGHT, QT_LEFT, QT_TOP = Qt.AlignCenter, Qt.AlignRight, Qt.AlignLeft, Qt.AlignTop


class DisplayAnnuaire(anr.Annuaire, QTabWidget):
    """Une combinaison de l'objet annuaire et d'un tabwidget"""
    def __init__(self, window):
        anr.Annuaire.__init__(self)
        QTabWidget.__init__(self)
        self.window = window
        if self.window is not None:
            self.backend = self.window.backend
            self.window.map_view.selected_robot_signal.connect(
                lambda rid: self.setCurrentWidget(self.robots[rid]))
        else:
            self.backend = None
        self.currentChanged.connect(self.update_selected_robot)
        self.ui_setup_tab()

    def update_selected_robot(self, index):
        """Met à jour le robot selectionné sur la carte"""
        rid = None
        for robot in self.robots.values():
            if self.indexOf(robot) == index:
                rid = robot.rid
        self.window.map_view.selected_robot = rid

    def ui_setup_tab(self):
        """ Configure l'inspecteur"""
        self.setMaximumSize(440, 16777215)
        self.setMovable(True)

    def add_robot(self, robot):
        """Ajoute un robot à l'annuaire
        et crée le tab associé

        Entrée:
        - robot (DisplayRobot)"""
        anr.Annuaire.add_robot(self, robot)
        robot.parent_annu = self
        self.addTab(robot, robot.rid)

    def remove_robot(self, rid):
        """Enlève un robot de l'annuaire

        Entrée:
        - rid (str)
        """
        self.robots[rid].hide()
        self.robots[rid].parent = None
        self.removeTab(self.currentIndex())
        anr.Annuaire.remove_robot(self, rid)

class DisplayRobot(anr.Robot, QWidget):
    """Une combinaison de l'objet Robot et d'un QWidget"""
    def __init__(self, parent_annu, rid):
        self.parent_annu = parent_annu
        self.backend = self.parent_annu.backend
        anr.Robot.__init__(self, rid)
        QWidget.__init__(self)

        self.is_ghost = self.rid[-6:] == '_ghost'

        self.ping = 0

        # Création des widgets de la boite robot
        self.groupbox_robots = QWidget()
        self.layout_tab_robot = QVBoxLayout(self)
        self.layout_box_robot = QVBoxLayout(self.groupbox_robots)
        self.scroll_area = QScrollArea()
        self.layout_name_delete = QHBoxLayout()
        self.button_delete = QPushButton()
        self.layout_coord = QHBoxLayout()
        self.layout_last_message = QHBoxLayout()
        self.groupbox_actuators = QGroupBox()
        self.groupbox_sensors = QGroupBox()
        self.layout_box_actuators = QVBoxLayout(self.groupbox_actuators)
        self.layout_box_sensors = QVBoxLayout(self.groupbox_sensors)
        self.label_last_message = QLabel()
        self.lcdnumber_las_message = QLCDNumber()
        self.layout_last_command = QHBoxLayout()
        self.label_position_command = QLabel()
        self.qlineedit_pos_cmd = QLineEdit()
        self.emergency_button = QPushButton()
        self.progressbar_battery = QProgressBar()

        # Configuration des widgets de la boite robot
        self.ui_setup_tab_robot()

        # Création d'un QTimer pour la mise à jour du ping du robot
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ping)
        self.timer.start(100)

    def ui_setup_tab_robot(self):
        """ Configure l'ensemble de l'onglet robot"""

        # Configuration de la scroll bar
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setWidget(self.groupbox_robots)
        self.layout_tab_robot.addWidget(self.scroll_area)

        self.button_delete.setFixedSize(175, 25)
        if self.is_ghost:
            self.button_delete.setText("Oublier")
            self.button_delete.clicked.connect(lambda: self.backend.forget_robot(self.rid))
        else:
            self.button_delete.setText("Eteindre")
            self.button_delete.clicked.connect(lambda: self.backend.stopandforget_robot(self.rid))

        self.emergency_button.setText("STOP")
        self.emergency_button.setStyleSheet(EMERGENCY_BUTTON)
        self.emergency_button.clicked.connect(lambda: self.parent_annu.window.map_view.forceRepaint.emit())
        if self.is_ghost:
            self.emergency_button.setText("Lecture")
            self.emergency_button.setStyleSheet(READONLY_BUTTON)
        self.emergency_button.setFixedSize(175, 25)
        if not self.is_ghost:
            self.emergency_button.clicked.connect(
                    lambda: self.backend.emergency_stop_robot(self.rid))
        self.layout_name_delete.addWidget(self.button_delete)
        self.layout_name_delete.addWidget(self.emergency_button)
        self.layout_box_robot.addLayout(self.layout_name_delete)

        # Configuration de l'affichage des coordonnées"
        self.lcdnumber_x = self.ui_setup_coord("X", "mm")
        self.lcdnumber_y = self.ui_setup_coord("Y", "mm")
        self.lcdnumber_theta = self.ui_setup_coord("θ", "°")
        self.layout_box_robot.addLayout(self.layout_coord)

        # Configuration de l'affichage du dernier message reçu
        self.label_last_message.setText("Dernière MAJ (s)")
        self.layout_last_message.addWidget(self.label_last_message)
        self.lcdnumber_las_message.setFixedSize(QLCD_SIZE2)
        self.layout_last_message.addWidget(self.lcdnumber_las_message)
        self.layout_box_robot.addLayout(self.layout_last_message)

        # Confiuration de l'envoyeur de commandes de postion
        self.label_position_command.setText("Dern. PosCmd:")
        self.layout_last_command.addWidget(self.label_position_command)
        self.qlineedit_pos_cmd = QLineEdit()
        self.qlineedit_pos_cmd.setText("1500 : 1000: 000")
        self.qlineedit_pos_cmd.setInputMask("0000 : 0000 : 000")
        self.qlineedit_pos_cmd.setFixedSize(220, 25)
        self.qlineedit_pos_cmd.editingFinished.connect(self.on_editing_finished)
        self.qlineedit_pos_cmd.setAlignment(QT_CENTER)
        self.layout_last_command.addWidget(self.qlineedit_pos_cmd)
        self.layout_box_robot.addLayout(self.layout_last_command)

        # Configuration de la Configure la boite actionneurs
        self.groupbox_actuators.setAlignment(QT_CENTER)
        self.groupbox_actuators.setTitle("Actionneurs")
        self.layout_box_robot.addWidget(self.groupbox_actuators, 0, QT_TOP)

        # Configuration de la boite capteurs
        self.groupbox_sensors.setAlignment(QT_CENTER)
        self.groupbox_sensors.setTitle("Capteurs:")
        self.layout_box_robot.addWidget(self.groupbox_sensors, 0, QT_TOP)

    def ui_setup_coord(self, coord: str, unite: str):
        """Configure un duo de widget (QLabel et QLCDNumber dans un QLayout)
        et renvoie le QLCDNumber"""

        label_coord = QLabel()
        label_coord.setText('{0} ({1})'.format(coord, unite))
        self.layout_coord.addWidget(label_coord)
        lcd_number_coord = QLCDNumber()
        lcd_number_coord.setFixedSize(QLCD_SIZE1)
        self.layout_coord.addWidget(lcd_number_coord)
        return lcd_number_coord

    def set_pos(self, x, y, theta):
        """Met à jour la position du robot

        Entrée:
        - x (float)
        - y (float)
        - theta (float)
        """
        anr.Robot.set_pos(self, x, y, theta)
        # Mise à jour des valeurs affichées par les QLCDNUmber
        self.lcdnumber_x.display(self.x)
        self.lcdnumber_y.display(self.y)
        self.lcdnumber_theta.display(self.theta)

        self.update_ping()

    def create_eqp(self, eqp_name, eqp_type, *args):
        """Crée un nouvel équipement, et l'ajoute au robot
        (sans avoir besoin de manipuler des objets Equipement

        Entrée:
            - eqp_name (str)
            - eqp_type (str): le type d'équipement,
            à choisir en inscrivant la chaine de caractère du nom de classe associé:
                'Equipement' / 'Actionneur' / 'Binaire' / 'Capteur'
            - args (tuple): tous les autres arguments liés à la création des eqps
                si actionneur ou capteur: (min, max, step (, unit))
        """
        nv_eqp = None
        if eqp_type == "Actionneur":
            min_v = args[0]
            max_v = args[1]
            step = args[2]
            if len(args) == 4:
                unit = args[3]
            else:
                unit = None
            nv_eqp = DisplayActionneur(self, eqp_name, min_v, max_v, step, unit)
        elif eqp_type == "Binaire":
            nv_eqp = DisplayBinaire(self, eqp_name)
        elif eqp_type == "Capteur":
            min_v = args[0]
            max_v = args[1]
            step = args[2]
            if len(args) == 4:
                unit = args[3]
            else:
                unit = None
            nv_eqp = DisplayCapteur(self, eqp_name, min_v, max_v, step, unit)

        if nv_eqp is not None:
            self.updt_eqp(nv_eqp)

    def updt_eqp(self, equipement):
        """Ajoute/met à jour un actionneur du robot

        Entrée:
        - equipement (Equipement)
        """
        #l'équipement existe-t-til déjà?
        if self.equipements.get(equipement.nom, None) is not None:
            self.equipements[equipement.nom].hide() #suppression de la partie graphique
        anr.Robot.updt_eqp(self, equipement) #mise à jour de l'équipement (data)
        #ajout de la partie graphique au bon layout
        if isinstance(equipement, DisplayCapteur):
            self.layout_box_sensors.addWidget(self.equipements[equipement.nom])
        else:
            self.layout_box_actuators.addWidget(self.equipements[equipement.nom])
        self.equipements[equipement.nom].show() #affichage partie graphique

        #cache des groupbox vides
        has_act = False
        has_capt = False
        for eqp_rb in self.equipements.values():
            if isinstance(eqp_rb, DisplayCapteur):
                has_capt = True
            if isinstance(eqp_rb, DisplayBinaire) or isinstance(eqp_rb, DisplayActionneur):
                has_act = True
        if not has_capt:
            self.groupbox_sensors.hide()
        else:
            self.groupbox_sensors.show()
        if not has_act:
            self.groupbox_actuators.hide()
        else:
            self.groupbox_actuators.show()

    def remove_eqp(self, eqp_name):
        """Enlève un équipement repéré par son nom du robot

        Entrée:
        - eqp_name (str)"""
        self.equipements[eqp_name].hide()
        self.equipements[eqp_name].setParent(None)
        anr.Robot.remove_eqp(self, eqp_name)

    def update_ping(self):
        """ Calcul et met à jour le ping de la position """
        self.ping = round(abs(time.time() - self.last_updt_pos), 1)
        self.lcdnumber_las_message.display(format(self.ping))
        for eqp_rb in self.equipements.values():
            eqp_rb.update_ping()

    @pyqtSlot()
    def on_editing_finished(self):
        """"Appelée après la fin de l'édition de self.qlineedit_pos_cmd"""
        cmd = [int(i) for i in self.qlineedit_pos_cmd.text().split(' : ')]
        self.backend.sendposcmd_robot(self.rid, cmd)

class DisplayBinaire(anr.Binaire, QWidget):
    """Une combinaison de l'objet Equipement et d'un QWidget"""
    def __init__(self, parent, nom):
        QWidget.__init__(self)
        anr.Binaire.__init__(self, nom)
        self.parent_robot = parent
        self.backend = self.parent_robot.backend
        self.updated_outside = False
        self.ping = 0

        # Création des widgets de l'équipement
        self.gridlayout_eqp = QGridLayout(self)
        self.spaceritem_equipement = QSpacerItem(1, 15)
        self.label_name_equipement = QLabel()
        self.label_message_equipement = QLabel("Dernière MAJ (s)")
        self.lcdnumber_ping_eqp = QLCDNumber()
        self.layout_binaire = QHBoxLayout()
        self.checkbox_equipement = QCheckBox()
        self.label_command = QLineEdit()
        self.label_last_command = QLabel()
        self.label_binaire = QLabel()

        # Configuration des widgets de l'équipement
        self.ui_setup_equipement()

    def ui_setup_equipement(self):
        """ Configure l'ensemble des widgets de l'équipement"""

        self.gridlayout_eqp.setAlignment(QT_TOP)

        if self.unite == "None" or self.unite is None:
            self.label_name_equipement.setText(self.nom)
        else:
            self.label_name_equipement.setText('{0} ({1})'.format(self.nom, self.unite))
        self.gridlayout_eqp.addWidget(self.label_name_equipement, 0, 0, 1, 1, QT_LEFT)

        self.gridlayout_eqp.addWidget(self.label_message_equipement, 2, 0, 1, 2, QT_LEFT)
        self.lcdnumber_ping_eqp.setMaximumSize(QSize(75, 25))
        self.lcdnumber_ping_eqp.setFixedSize(QLCD_SIZE2)
        self.gridlayout_eqp.addWidget(self.lcdnumber_ping_eqp, 2, 1, 1, 1, QT_RIGHT)

        self.label_binaire.setFixedSize(100, 20)
        self.checkbox_equipement.stateChanged.connect(self.oncheckbox_toggled)
        self.layout_binaire.addWidget(self.label_binaire)
        self.layout_binaire.addWidget(self.checkbox_equipement)
        self.gridlayout_eqp.addLayout(self.layout_binaire, 0, 1, 1, 1, QT_CENTER)

        self.label_command.setText("None")
        self.label_command.setFixedSize(75, 30)
        self.label_command.setReadOnly(True)
        self.label_command.setAlignment(QT_CENTER)
        self.gridlayout_eqp.addWidget(self.label_command, 1, 1, 1, 1, QT_RIGHT)
        self.label_last_command.setText("Dern. Cmd:")
        self.gridlayout_eqp.addWidget(self.label_last_command, 1, 0, 1, 1, QT_LEFT)

    def updt_cmd(self, state):
        """Met à jour le timestamp de dernière commande
        et la dernière commande"""
        anr.Binaire.updt_cmd(self, state)
        self.label_command.setText(str(state))

    def set_state(self, valeur):
        """Change la valeur

        Entrée:
        - valeur (float)"""
        anr.Binaire.set_state(self, valeur)
        self.updated_outside = True
        self.checkbox_equipement.setChecked(int(valeur))
        self.updated_outside = False

    #calcul et mise à jour du ping
    def update_ping(self):
        """Mise à jour du ping de l'équipement"""
        self.ping = round(abs(time.time() - self.last_updt), 1)
        self.lcdnumber_ping_eqp.display(format(self.ping))

    @pyqtSlot()
    def oncheckbox_toggled(self):
        """ Affiche et renvoie vers backend la dernière commande d'un actionneur binaire"""
        if not self.updated_outside:
            state = 1 if self.checkbox_equipement.isChecked() else 0
            self.backend.sendeqpcmd(self.parent_robot.rid, self.nom, state)
            self.updt_cmd(state)

class DisplayCapteur(anr.Capteur, QWidget):
    """Une combinaison de Capteur et d'un QWidget"""
    def __init__(self, parent_robot, nom, min_val, max_val, step=1, unite=None):
        QWidget.__init__(self)
        anr.Capteur.__init__(self, nom, min_val, max_val, step, unite)
        self.parent_robot = parent_robot
        self.backend = self.parent_robot.backend
        self.updated_outside = False
        self.ping = 0

        # Création des widgets de l'équipement
        self.gridlayout_eqp = QGridLayout(self)
        self.spaceritem_equipement = QSpacerItem(1, 15)
        self.label_name_equipement = QLabel()
        self.label_message_equipement = QLabel("Dernière MAJ (s)")
        self.lcdnumber_ping_eqp = QLCDNumber()

        self.lcdnumber_eqp = QLCDNumber()
        self.progressbar_eqp = QProgressBar()

        # Configuration des widgets de l'équipement
        self.ui_setup_equipement()

    def ui_setup_equipement(self):
        """ Configure l'ensemble des widgets de l'équipement"""

        self.gridlayout_eqp.setAlignment(QT_TOP)

        if self.unite == "None" or self.unite is None:
            self.label_name_equipement.setText(self.nom)
        else:
            self.label_name_equipement.setText('{0} ({1})'.format(self.nom, self.unite))
        self.gridlayout_eqp.addWidget(self.label_name_equipement, 0, 0, 1, 1, QT_LEFT)

        self.label_message_equipement.setText("Dernière MAJ (s)")
        self.gridlayout_eqp.addWidget(self.label_message_equipement, 2, 0, 1, 2, QT_LEFT)
        self.lcdnumber_ping_eqp.setMaximumSize(QSize(75, 25))
        self.lcdnumber_ping_eqp.setFixedSize(QLCD_SIZE2)
        self.gridlayout_eqp.addWidget(self.lcdnumber_ping_eqp, 2, 1, 1, 1, QT_RIGHT)

        if self.min_val is None or self.max_val is None or self.step is None:
            self.lcdnumber_eqp.setMinimumSize(150, 30)
            self.gridlayout_eqp.addWidget(self.lcdnumber_eqp, 0, 1, 1, 1, QT_RIGHT)
            self.progressbar_eqp.hide()
        else:
            self.progressbar_eqp.setRange(int(self.min_val), int(self.max_val))
            self.progressbar_eqp.setAlignment(QT_CENTER)
            self.progressbar_eqp.setFormat("%v")
            self.progressbar_eqp.setFixedSize(150, 30)
            self.gridlayout_eqp.addWidget(self.progressbar_eqp, 0, 1, 1, 1, QT_RIGHT)
            self.lcdnumber_eqp.hide()

    #calcul et mise à jour du ping
    def update_ping(self):
        """Mise à jour du ping de l'équipement"""
        self.ping = round(abs(time.time() - self.last_updt), 1)
        self.lcdnumber_ping_eqp.display(format(self.ping))

    def set_state(self, valeur):
        """Change la valeur

        Entrée:
        - valeur (float)"""
        anr.Binaire.set_state(self, valeur)
        self.updated_outside = True
        if self.valeur is not None:
            self.lcdnumber_eqp.display(self.valeur)
            self.progressbar_eqp.setValue(int(self.valeur))
        self.updated_outside = False

class DisplayActionneur(anr.Actionneur, QWidget):
    """ Combinaison d'un objet Actionneur et d'un QWidget """
    def __init__(self, parent_robot, nom, min_val, max_val, step=1, unite=None):
        QWidget.__init__(self)
        anr.Actionneur.__init__(self, nom, min_val, max_val, step, unite)
        self.parent_robot = parent_robot
        self.backend = self.parent_robot.backend
        self.updated_outside = False
        self.ping = 0

        # Création des widgets de l'équipement
        self.gridlayout_eqp = QGridLayout(self)
        self.spaceritem_equipement = QSpacerItem(1, 15)
        self.label_name_equipement = QLabel()
        self.label_message_equipement = QLabel("Dernière MAJ (s)")
        self.lcdnumber_ping_eqp = QLCDNumber()

        self.layout_discret = QHBoxLayout()
        self.slider_equipement = QSlider(Qt.Horizontal)
        self.doublespinbox_eqp = QDoubleSpinBox()
        self.label_command = QLineEdit()
        self.label_last_command = QLabel()

        # Configuration des widgets de l'équipement
        self.ui_setup_equipement()

    #calcul et mise à jour du ping
    def update_ping(self):
        """Mise à jour du ping de l'équipement"""
        self.ping = round(abs(time.time() - self.last_updt), 1)
        self.lcdnumber_ping_eqp.display(format(self.ping))

    def ui_setup_equipement(self):
        """ Configure l'ensemble des widgets de l'équipement"""

        self.gridlayout_eqp.setAlignment(QT_TOP)

        if self.unite == "None" or self.unite is None:
            self.label_name_equipement.setText(self.nom)
        else:
            self.label_name_equipement.setText('{0} ({1})'.format(self.nom, self.unite))
        self.gridlayout_eqp.addWidget(self.label_name_equipement, 0, 0, 1, 1, QT_LEFT)

        self.label_message_equipement.setText("Dernière MAJ (s)")
        self.gridlayout_eqp.addWidget(self.label_message_equipement, 2, 0, 1, 2, QT_LEFT)
        self.lcdnumber_ping_eqp.setMaximumSize(QSize(75, 25))
        self.lcdnumber_ping_eqp.setFixedSize(QLCD_SIZE2)
        self.gridlayout_eqp.addWidget(self.lcdnumber_ping_eqp, 2, 1, 1, 1, QT_RIGHT)

        self.slider_equipement.setFixedSize(100, 30)
        self.slider_equipement.setMinimum(self.min_val)
        self.slider_equipement.setMaximum(self.max_val)
        self.slider_equipement.setSingleStep(self.step)
        self.slider_equipement.valueChanged.connect(self.onvaluechanged_slider)
        self.layout_discret.addWidget(self.slider_equipement)
        self.doublespinbox_eqp.setFixedSize(75, 30)
        self.doublespinbox_eqp.setMaximum(self.max_val)
        self.doublespinbox_eqp.setMinimum(self.min_val)
        self.doublespinbox_eqp.setSingleStep(self.step)
        self.doublespinbox_eqp.setAlignment(QT_CENTER)
        self.doublespinbox_eqp.valueChanged.connect(self.onvaluechanged)
        self.layout_discret.addWidget(self.doublespinbox_eqp)
        self.gridlayout_eqp.addLayout(self.layout_discret, 0, 1, 1, 1, QT_RIGHT)

        self.label_command.setText("None")
        self.label_command.setFixedSize(75, 30)
        self.label_command.setReadOnly(True)
        self.label_command.setAlignment(QT_CENTER)
        self.gridlayout_eqp.addWidget(self.label_command, 1, 1, 1, 1, QT_RIGHT)
        self.label_last_command.setText("Dern. Cmd:")
        self.gridlayout_eqp.addWidget(self.label_last_command, 1, 0, 1, 1, QT_LEFT)

    def set_state(self, valeur):
        """Change la valeur

        Entrée:
        - valeur (float)"""
        anr.Binaire.set_state(self, valeur)
        self.updated_outside = True
        self.slider_equipement.setValue(int(valeur))
        self.doublespinbox_eqp.setValue(valeur)
        self.updated_outside = False

    def updt_cmd(self, state):
        """Met à jour le timestamp de dernière commande
        et la dernière commande"""
        anr.Binaire.updt_cmd(self, state)
        self.label_command.setText(str(state))

    @pyqtSlot()
    def onvaluechanged(self):
        """ Affiche et envoie vers backend la dernière commande d'un actionneur discret"""
        if not self.updated_outside:
            self.backend.sendeqpcmd(self.parent_robot.rid, self.nom, self.doublespinbox_eqp.value())
            self.label_command.setText(str(self.doublespinbox_eqp.value()))
            self.slider_equipement.setValue(int(self.doublespinbox_eqp.value()))
            self.updt_cmd(self.doublespinbox_eqp.value())

    @pyqtSlot()
    def onvaluechanged_slider(self):
        """ Affiche et envoie vers backend la dernière commande d'un actionneur discret"""
        if not self.updated_outside:
            self.backend.sendeqpcmd(self.parent_robot.rid, self.nom, self.doublespinbox_eqp.value())
            self.label_command.setText(str(self.slider_equipement.value()))
            self.doublespinbox_eqp.setValue(self.slider_equipement.value())
            self.updt_cmd(self.slider_equipement.value())
