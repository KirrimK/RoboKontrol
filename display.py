""" Module display.py - widgets associés à l'affichage des informations """

import time, sys
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QGroupBox, QHBoxLayout, QVBoxLayout,QLineEdit, QLCDNumber, \
     QScrollArea, QFrame, QProgressBar, QTabWidget, QApplication
from PyQt5.QtWidgets import QLabel, QWidget, QSlider, QPushButton, QGridLayout, QHBoxLayout,\
    QLineEdit, QDialog, QColorDialog, QCheckBox, QDoubleSpinBox, QProgressBar, QSpacerItem, QLCDNumber, QComboBox
from PyQt5.QtCore import pyqtSlot, Qt, QSize, QTimer #pyqtSignal
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QSize, QTimer
import annuaire as anr

# Customisation
QPROGRESSBAR = "QProgressBar{background-color : grey;border : 1px; border: 2px solid grey; border-radius: 5px} "
QEMERGENCYBUTTON = "QPushButton{background-color : rgb(255, 0,0); border : 1px; border: 2px solid rgb(170,0,0)}"
QPROGRESSBAR_FULL = "QProgressBar{background-color : grey; border : 1px; border: 2px solid grey; border-radius: 5px} QProgressBar::chunk{background-color: green; border-radius: 5px;}"
QPROGRESSBAR_MEDIUM = "QProgressBar{background-color : grey; border : 1px; border: 2px solid grey; border-radius: 5px} QProgressBar::chunk{background-color: orange; border-radius: 5px;}"
QPROGRESSBAR_LOW = "QProgressBar{background-color : grey; border : 1px; border: 2px solid grey; border-radius: 5px} QProgressBar::chunk{background-color: red; border-radius: 5px;}"

# QtWidgets size
QLCD_SIZE1, QLCD_SIZE2 = QSize(60, 20), QSize(80, 20)
# Alignment
QT_CENTER, QT_RIGHT, QT_LEFT, QT_TOP = Qt.AlignCenter, Qt.AlignRight, Qt.AlignLeft, Qt.AlignTop


class DisplayAnnu(anr.Annuaire, QTabWidget):
    """Une combinaison de l'objet annuaire et d'un tabwidget"""
    def __init__(self, window):
        anr.Annuaire.__init__(self)
        QTabWidget.__init__(self)
        self.window = window
        #self.window.map_view.selected_robot_signal.connect(lambda rid: self.setCurrentWidget(self.window.current_robots_dic[rid]))
        self.ui_setup_tab()

    def update_selected_robot(self, rid):
        """Met à jour le robot selectionné sur la carte"""
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
        robot.parent = self
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

    def update(self):
        """Mise à jour du widget et des widgets contenus"""
        # Emission du signal de l'onglet sélectionné
        if self.robots:
            self.window.map_view.selected_robot_signal.emit(self.currentWidget().rid)

class DisplayRobot(anr.Robot, QWidget):
    """Une combinaison de l'objet Robot et d'un QWidget"""
    def __init__(self, rid):
        self.parent = None
        anr.Robot.__init__(self, rid)
        QWidget.__init__(self)

        self.ping = 0

        # Création de la boite robot (QGroupBox)
        self.layout_tab_robot = QVBoxLayout(self)
        self.groupBox_robots = QWidget()
        self.layout_box_robot = QVBoxLayout(self.groupBox_robots)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.scroll_area.setWidget(self.groupBox_robots)
        self.layout_tab_robot.addWidget(self.scroll_area)

        # Création des widgets de la boite robot
        self.layout_name_delete = QHBoxLayout()
        self.button_delete = QPushButton()
        self.layout_coord = QHBoxLayout()
        self.layout_last_message = QHBoxLayout()
        self.groupBox_actuators = QGroupBox()
        self.groupBox_sensors = QGroupBox()
        self.layout_box_actuators = QVBoxLayout(self.groupBox_actuators)
        self.layout_box_sensors = QVBoxLayout(self.groupBox_sensors)
        self.label_last_message = QLabel()
        self.lcdNumber_last_message = QLCDNumber()
        self.layout_last_command = QHBoxLayout()
        self.label_positionCommand = QLabel()
        self.QLineEdit_positionCommand = QLineEdit()
        self.emergencyButton = QPushButton()
        self.progressbar_battery = QProgressBar()

        # Configuration des widgets de la boite robot
        self.ui_setup_tab_robot()

        # Connexion du signal de mise à jours des équipements avec le slot de mise à jour de l'ensemble des équipements
        #self.list_equipement_changed_signal.connect(self.update_equipements)

        # Connexion du signal de mise à jour de la position
        #self.backend.widget.position_updated.connect(lambda new_position: self.set_pos(new_position))

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ping)
        self.timer.start(100)

    def ui_setup_tab_robot(self):
        """ Configure l'ensemble de l'onglet robot"""

        self.progressbar_battery.setStyleSheet(QPROGRESSBAR_FULL)
        self.progressbar_battery.setFixedSize(150, 30)

        self.button_delete.setMaximumSize(150, 25)
        self.button_delete.setText("Eteindre")
        self.button_delete.clicked.connect(lambda: self.parent.remove_robot(self.rid))

        self.emergencyButton.setText("Arrêt d'urgence")
        self.emergencyButton.setStyleSheet(QEMERGENCYBUTTON)
        self.emergencyButton.setMaximumSize(250, 25)
        self.emergencyButton.clicked.connect(lambda: self.parent.window.backend.emergency_stop_robot(self.rid))
        self.layout_name_delete.addWidget(self.button_delete)
        self.layout_name_delete.addWidget(self.emergencyButton)
        self.layout_box_robot.addLayout(self.layout_name_delete)

        # Configuration de l'affichage des coordonnées"
        self.lcdNumber_x = self.ui_setup_coord("X", "mm")
        self.lcdNumber_y = self.ui_setup_coord("Y", "mm")
        self.lcdNumber_theta = self.ui_setup_coord("θ", "°")
        self.layout_box_robot.addLayout(self.layout_coord)

        # Configuration de l'affichage du dernier message reçu
        self.label_last_message.setText("Dernière MAJ (s)")
        self.layout_last_message.addWidget(self.label_last_message)
        self.lcdNumber_last_message.setFixedSize(QLCD_SIZE2)
        self.layout_last_message.addWidget(self.lcdNumber_last_message)
        self.layout_box_robot.addLayout(self.layout_last_message)

        # Confiuration de l'envoyeur de commandes de postion
        self.label_positionCommand.setText("Dern. PosCmd:")
        self.layout_last_command.addWidget(self.label_positionCommand)
        self.QLineEdit_positionCommand = QLineEdit()
        self.QLineEdit_positionCommand.setText("1500 : 1000: 000")
        self.QLineEdit_positionCommand.setInputMask("0000 : 0000 : 000")
        self.QLineEdit_positionCommand.setFixedSize(220, 25)
        self.QLineEdit_positionCommand.editingFinished.connect(self.onEditingFinished)
        self.QLineEdit_positionCommand.setAlignment(QT_CENTER)
        self.layout_last_command.addWidget(self.QLineEdit_positionCommand)
        self.layout_box_robot.addLayout(self.layout_last_command)

        # Configuration de la Configure la boite actionneurs
        self.groupBox_actuators.setAlignment(QT_CENTER)
        self.groupBox_actuators.setTitle("Actionneurs")
        self.layout_box_robot.addWidget(self.groupBox_actuators, 0, QT_TOP)

        # Configuration de la boite capteurs
        self.groupBox_sensors.setAlignment(QT_CENTER)
        self.groupBox_sensors.setTitle("Capteurs:")
        self.layout_box_robot.addWidget(self.groupBox_sensors, 0, QT_TOP)

    def ui_setup_coord(self, coord: str, unite: str):
        """Configure un duo de widget (QLabel et QLCDNumber dans un QLayout)
        et renvoie le QLCDNumber"""

        self.label_coord = QLabel()
        self.label_coord.setText('{0} ({1})'.format(coord, unite))
        self.layout_coord.addWidget(self.label_coord)
        self.lcdNumber_coord = QLCDNumber()
        self.lcdNumber_coord.setFixedSize(QLCD_SIZE1)
        self.layout_coord.addWidget(self.lcdNumber_coord)
        return self.lcdNumber_coord

    def set_pos(self, pos_x, pos_y, theta):
        """Met à jour la position du robot

        Entrée:
        - pos_x (float)
        - pos_y (float)
        - theta (float)
        """
        anr.Robot.set_pos(self, pos_x, pos_y, theta)
        # Mise à jour des valeurs affichées par les QLCDNUmber
        self.lcdNumber_x.display(self.x)
        self.lcdNumber_y.display(self.y)
        self.lcdNumber_theta.display(self.theta)

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
        eqp = None
        if eqp_type == "Actionneur":
            min_v = args[0]
            max_v = args[1]
            step = args[2]
            if len(args) == 4:
                unit = args[3]
            else:
                unit = None
            eqp = DisplayActionneur(self.window, eqp_name, min_v, max_v, step, unit)
        elif eqp_type == "Binaire":
            eqp = DisplayBinaire(self.window, eqp_name)
        elif eqp_type == "Capteur":
            min_v = args[0]
            max_v = args[1]
            step = args[2]
            if len(args) == 4:
                unit = args[3]
            else:
                unit = None
            eqp = DisplayCapteur(self.window, eqp_name, min_v, max_v, step, unit)

        if eqp is not None:
            self.updt_eqp(eqp)

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
        for eqp in self.equipements.values():
            if isinstance(eqp, DisplayCapteur):
                has_capt = True
            if isinstance(eqp, DisplayBinaire):
                has_act = True
        if not has_capt:
            self.groupBox_sensors.hide()
        else:
            self.groupBox_sensors.show()
        if not has_act:
            self.groupBox_actuators.hide()
        else:
            self.groupBox_actuators.show()

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
        self.lcdNumber_last_message.display(format(self.ping))
        for eqp in self.equipements.values():
            eqp.update_ping()

    @pyqtSlot()
    def onEditingFinished(self):
        """"Appelée après la fin de l'édition de self.QLineEdit_positionCommand"""
        self.backend.sendposcmd_robot(self.rid, [int(i) for i in self.QLineEdit_positionCommand.text().split(' : ')])

    @pyqtSlot()
    def emergencyButtonPressed (self):
        """Appelée si le bouton d'arrêt d'urgence d'un robot est pressé"""
        self.backend.emergency_stop_robot (self.rid)

class DisplayBinaire(anr.Binaire, QWidget):
    """Une combinaison de l'objet Equipement et d'un QWidget"""
    def __init__(self, parent_window, nom):
        QWidget.__init__(self)
        anr.Binaire.__init__(self, nom)
        self.parent = parent_window
        self.updated_outside = False
        self.ping = 0

        # Création des widgets de l'équipement
        self.gridLayout_equipement = QGridLayout(self)
        self.spacerItem_equipement = QSpacerItem(1, 15)
        self.label_name_equipement = QLabel()
        self.label_message_equipement = QLabel("Dernière MAJ (s)")
        self.lcdNumber_ping_equipement = QLCDNumber()

        self.layout_binaire = QHBoxLayout()
        self.checkBox_equipement = QCheckBox()
        self.label_command = QLineEdit()
        self.label_last_command = QLabel()
        self.label_binaire = QLabel()

        # Configuration des widgets de l'équipement
        self.ui_setup_equipement()

    def ui_setup_equipement(self):
        """ Configure l'ensemble des widgets de l'équipement"""

        self.gridLayout_equipement.setAlignment(QT_TOP)

        if self.unite == "None" or self.unite is None:
            self.label_name_equipement.setText(self.nom)
        else:
            self.label_name_equipement.setText('{0} ({1})'.format(self.nom, self.unite))
        self.gridLayout_equipement.addWidget(self.label_name_equipement, 0, 0, 1, 1, QT_LEFT)

        self.gridLayout_equipement.addWidget(self.label_message_equipement, 2, 0, 1, 2, QT_LEFT)
        self.lcdNumber_ping_equipement.setMaximumSize(QSize(75, 25))
        self.lcdNumber_ping_equipement.setFixedSize(QLCD_SIZE2)
        self.gridLayout_equipement.addWidget(self.lcdNumber_ping_equipement, 2, 1, 1, 1, QT_RIGHT)

        self.label_binaire.setFixedSize(100, 20)
        self.checkBox_equipement.stateChanged.connect(lambda: self.oncheckbox_toggled())
        self.layout_binaire.addWidget(self.label_binaire)
        self.layout_binaire.addWidget(self.checkBox_equipement)
        self.gridLayout_equipement.addLayout(self.layout_binaire, 0, 1, 1, 1, QT_CENTER)

        self.label_command.setText("None")
        self.label_command.setFixedSize(75, 30)
        self.label_command.setReadOnly(True)
        self.label_command.setAlignment(QT_CENTER)
        self.gridLayout_equipement.addWidget(self.label_command, 1, 1, 1, 1, QT_RIGHT)
        self.label_last_command.setText("Dern. Cmd:")
        self.gridLayout_equipement.addWidget(self.label_last_command, 1, 0, 1, 1, QT_LEFT)

    def updt_cmd(self, state):
        """Met à jour le timestamp de dernière commande
        et la dernière commande"""
        anr.Binaire.updt_cmd(self)
        self.label_command.setText(str(state))

    def set_state(self, valeur):
        """Change la valeur

        Entrée:
        - valeur (float)"""
        anr.Binaire.set_state(self, valeur)
        self.updated_outside = True
        self.checkBox_equipement.setChecked(int(valeur))
        self.updated_outside = False

    #calcul et mise à jour du ping
    def update_ping(self):
        self.ping = round(abs(time.time() - self.last_updt), 1)
        self.lcdNumber_ping_equipement.display(format(self.ping))

    @pyqtSlot()
    def oncheckbox_toggled(self):
        """ Affiche et renvoie vers backend la dernière commande d'un actionneur binaire"""
        if not self.updated_outside:
            state = 1 if self.checkBox_equipement.isChecked() else 0
            self.backend.sendeqpcmd(self.rid, self.name, state)
            self.updt_cmd(state)

class DisplayCapteur(anr.Capteur, QWidget):
    """Une combinaison de Capteur et d'un QWidget"""
    def __init__(self, parent_window, nom, min_val, max_val, step=1, unite=None):
        QWidget.__init__(self)
        anr.Capteur.__init__(self, nom, min_val, max_val, step, unite)
        self.parent = parent_window
        self.updated_outside = False
        self.ping = 0

        # Création des widgets de l'équipement
        self.gridLayout_equipement = QGridLayout(self)
        self.spacerItem_equipement = QSpacerItem(1, 15)
        self.label_name_equipement = QLabel()
        self.label_message_equipement = QLabel("Dernière MAJ (s)")
        self.lcdNumber_ping_equipement = QLCDNumber()

        self.lcdNumber_equipement = QLCDNumber()
        self.progressBar_equipement = QProgressBar()

        # Configuration des widgets de l'équipement
        self.ui_setup_equipement()

    def ui_setup_equipement(self):
        """ Configure l'ensemble des widgets de l'équipement"""

        self.gridLayout_equipement.setAlignment(QT_TOP)

        if self.unite == "None" or self.unite is None:
            self.label_name_equipement.setText(self.nom)
        else:
            self.label_name_equipement.setText('{0} ({1})'.format(self.nom, self.unite))
        self.gridLayout_equipement.addWidget(self.label_name_equipement, 0, 0, 1, 1, QT_LEFT)

        self.label_message_equipement.setText("Dernière MAJ (s)")
        self.gridLayout_equipement.addWidget(self.label_message_equipement, 2, 0, 1, 2, QT_LEFT)
        self.lcdNumber_ping_equipement.setMaximumSize(QSize(75, 25))
        self.lcdNumber_ping_equipement.setFixedSize(QLCD_SIZE2)
        self.gridLayout_equipement.addWidget(self.lcdNumber_ping_equipement, 2, 1, 1, 1, QT_RIGHT)

        self.lcdNumber_equipement.setMinimumSize(150, 30)
        self.gridLayout_equipement.addWidget(self.lcdNumber_equipement, 0, 1, 1, 1, QT_RIGHT)

        self.progressBar_equipement = QProgressBar()
        self.progressBar_equipement.setRange(int(self.min_val), int(self.max_val))
        self.progressBar_equipement.setStyleSheet(QPROGRESSBAR)
        self.progressBar_equipement.setAlignment(QT_CENTER)
        self.progressBar_equipement.setFormat("%v")
        self.progressBar_equipement.setFixedSize(150, 30)
        self.gridLayout_equipement.addWidget(self.progressBar_equipement, 0, 1, 1, 1, QT_RIGHT)

        if self.min_val is None or self.max_val is None or self.step is None:
            self.progressBar_equipement.hide()
        else:
            self.lcdNumber_equipement.hide()

    #calcul et mise à jour du ping
    def update_ping(self):
        self.ping = round(abs(time.time() - self.last_updt), 1)
        self.lcdNumber_ping_equipement.display(format(self.ping))

    def set_state(self, valeur):
        """Change la valeur

        Entrée:
        - valeur (float)"""
        anr.Binaire.set_state(self, valeur)
        self.updated_outside = True
        self.lcdNumber_equipement.display(self.valeur)
        self.progressBar_equipement.setValue(int(self.valeur))
        self.updated_outside = False

class DisplayActionneur(anr.Actionneur, QWidget):
    """Combinaise d'un objet Actionneur et d'un QWidget"""
    def __init__(self, parent_window, nom, min_val, max_val, step=1, unite=None):
        QWidget.__init__(self)
        anr.Actionneur.__init__(self, nom, min_val, max_val, step, unite)
        self.parent = parent_window
        self.updated_outside = False
        self.ping = 0

        # Création des widgets de l'équipement
        self.gridLayout_equipement = QGridLayout(self)
        self.spacerItem_equipement = QSpacerItem(1, 15)
        self.label_name_equipement = QLabel()
        self.label_message_equipement = QLabel("Dernière MAJ (s)")
        self.lcdNumber_ping_equipement = QLCDNumber()

        self.layout_discret = QHBoxLayout()
        self.slider_equipement = QSlider(Qt.Horizontal)
        self.doubleSpinBox_equipement = QDoubleSpinBox()
        self.label_command = QLineEdit()
        self.label_last_command = QLabel()

        # Configuration des widgets de l'équipement
        self.ui_setup_equipement()
    
    #calcul et mise à jour du ping
    def update_ping(self):
        self.ping = round(abs(time.time() - self.last_updt), 1)
        self.lcdNumber_ping_equipement.display(format(self.ping))

    def ui_setup_equipement(self):
        """ Configure l'ensemble des widgets de l'équipement"""

        self.gridLayout_equipement.setAlignment(QT_TOP)

        if self.unite == "None" or self.unite is None:
            self.label_name_equipement.setText(self.nom)
        else:
            self.label_name_equipement.setText('{0} ({1})'.format(self.nom, self.unite))
        self.gridLayout_equipement.addWidget(self.label_name_equipement, 0, 0, 1, 1, QT_LEFT)

        self.label_message_equipement.setText("Dernière MAJ (s)")
        self.gridLayout_equipement.addWidget(self.label_message_equipement, 2, 0, 1, 2, QT_LEFT)
        self.lcdNumber_ping_equipement.setMaximumSize(QSize(75, 25))
        self.lcdNumber_ping_equipement.setFixedSize(QLCD_SIZE2)
        self.gridLayout_equipement.addWidget(self.lcdNumber_ping_equipement, 2, 1, 1, 1, QT_RIGHT)

        self.slider_equipement.setFixedSize(100, 30)
        self.slider_equipement.setMinimum(self.min_val)
        self.slider_equipement.setMaximum(self.max_val)
        self.slider_equipement.setSingleStep(self.step)
        self.slider_equipement.valueChanged.connect(lambda: self.onvaluechanged_slider())
        self.layout_discret.addWidget(self.slider_equipement)
        self.doubleSpinBox_equipement.setFixedSize(75, 30)
        self.doubleSpinBox_equipement.setMaximum(self.max_val)
        self.doubleSpinBox_equipement.setMinimum(self.min_val)
        self.doubleSpinBox_equipement.setSingleStep(self.step)
        self.doubleSpinBox_equipement.setAlignment(QT_CENTER)
        self.doubleSpinBox_equipement.valueChanged.connect(lambda: self.onvaluechanged())
        self.layout_discret.addWidget(self.doubleSpinBox_equipement)
        self.gridLayout_equipement.addLayout(self.layout_discret, 0, 1, 1, 1, QT_RIGHT)

    def set_state(self, valeur):
        """Change la valeur

        Entrée:
        - valeur (float)"""
        anr.Binaire.set_state(self, valeur)
        self.updated_outside = True
        self.label_command.setText(str(valeur))
        self.slider_equipement.setValue(int(valeur))
        self.doubleSpinBox_equipement.setValue(valeur)
        self.updated_outside = False

    def updt_cmd(self, state):
        """Met à jour le timestamp de dernière commande
        et la dernière commande"""
        anr.Binaire.updt_cmd(self)
        self.label_command.setText(str(state))

    @pyqtSlot()
    def onvaluechanged(self):
        """ Affiche et envoie vers backend la dernière commande d'un actionneur discret"""
        if not self.updated_outside:
            self.backend.sendeqpcmd(self.rid, self.name, self.doubleSpinBox_equipement.value())
            self.label_command.setText(str(self.doubleSpinBox_equipement.value()))
            self.slider_equipement.setValue(int(self.doubleSpinBox_equipement.value()))
            self.updt_cmd(self.doubleSpinBox_equipement.value())

    @pyqtSlot()
    def onvaluechanged_slider(self):
        """ Affiche et envoie vers backend la dernière commande d'un actionneur discret"""
        if not self.updated_outside:
            self.backend.sendeqpcmd(self.rid, self.name, self.doubleSpinBox_equipement.value())
            self.label_command.setText(str(self.slider_equipement.value()))
            self.doubleSpinBox_equipement.setValue(self.slider_equipement.value())
            self.updt_cmd(self.slider_equipement.value())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    annu = DisplayAnnu(None)
    robot = DisplayRobot("stonks")
    eqp = DisplayCapteur(None, "bruh", 0, 100)
    robot.updt_eqp(eqp)
    eqp2 = DisplayBinaire(None, "brrruhhhh")
    robot.updt_eqp(eqp2)
    eqp3 = DisplayActionneur(None, "actiobruh", 0, 100, 1, "bruh")
    robot.updt_eqp(eqp3)
    annu.add_robot(robot)
    annu.show()
    eqp.set_state(50)
    eqp3.set_state(75)
    sys.exit(app.exec_())
