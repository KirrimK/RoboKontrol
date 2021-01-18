""" tab_robot.py - Définit l'affichage d'un onglet robot"""

import time
import annuaire
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QGroupBox, QHBoxLayout, QVBoxLayout,QLineEdit, QLCDNumber, \
     QScrollArea, QFrame, QProgressBar
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QSize, QTimer
from equipement import Equipement

# Customisation
QEMERGENCYBUTTON = "QPushButton{background-color : rgb(255, 0,0); border : 1px; border: 2px solid rgb(170,0,0)}"
QPROGRESSBAR_FULL = "QProgressBar{background-color : grey; border : 1px; border: 2px solid grey; border-radius: 5px} QProgressBar::chunk{background-color: green; border-radius: 5px;}"
QPROGRESSBAR_MEDIUM = "QProgressBar{background-color : grey; border : 1px; border: 2px solid grey; border-radius: 5px} QProgressBar::chunk{background-color: orange; border-radius: 5px;}"
QPROGRESSBAR_LOW = "QProgressBar{background-color : grey; border : 1px; border: 2px solid grey; border-radius: 5px} QProgressBar::chunk{background-color: red; border-radius: 5px;}"

# QtWidgets size
QLCD_SIZE1, QLCD_SIZE2 = QSize(60, 20), QSize(80, 20)
# Alignment
QT_CENTER, QT_RIGHT, QT_LEFT, QT_TOP = Qt.AlignCenter, Qt.AlignRight, Qt.AlignLeft, Qt.AlignTop


class TabRobot(QWidget):
    """Définit l'affiche d'un robot sous forme d'un onglet composé d'une scroll bar (QScrollBar) dans laquelle il y a
    une boite robot (QGroupBox) """

    # Création de signal de mise jour de la liste des équipements associés au robot
    list_equipement_changed_signal = pyqtSignal(list)

    def __init__(self, rid: str, window):

        super().__init__()
        self.rid = rid
        self.window = window

        self.position = ()
        self.last_update_pos = time.time()
        self.timestamp = time.time()
        self.backend = self.window.backend

        self.battery_value = None
        self.battery_min = None
        self.battery_max = None
        self.battery_step = None

        # Création de la boite robot (QGroupBox)
        self.layout_tab_robot = QVBoxLayout(self)
        self.groupBox_robots = QWidget()
        self.layout_box_robot = QVBoxLayout(self.groupBox_robots)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        #self.scroll_area.setMinimumSize(QSize(425, 0))
        #self.scroll_area.setMaximumSize(QSize(425, 16777215))
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

        # Liste des équipements attachés au robot
        self.current_equipement_list = []
        self.current_equipement_dic = {}
        self.current_actuators_list = []
        self.current_sensors_list = []

        # Configuration des widgets de la boite robot
        self.ui_setup_tab_robot()

        #calcul et mise à jour du temps de message
        def update_ping():
            # Calcul du ping
            self.timestamp = time.time()
            self.ping = abs(self.last_update_pos - self.timestamp)
            self.lcdNumber_last_message.display(self.ping)
        
        self.ping_timer = QTimer()
        self.ping_timer.timeout.connect(update_ping)
        self.ping_timer.start(50)


        # Connexion du signal de mise à jours des équipements avec le slot de mise à jour de l'ensemble des équipements
        self.list_equipement_changed_signal.connect(self.update_equipements)

        # Connexion du signal de mise à jour de la position
        self.backend.widget.PosRegSignal.connect(lambda new_position: self.update_position(new_position))

    def ui_setup_tab_robot(self):
        """ Configure l'ensemble de l'onglet robot"""

        self.progressbar_battery.setStyleSheet(QPROGRESSBAR_FULL)
        self.progressbar_battery.setFixedSize(150, 30)

        self.button_delete.setMaximumSize(150, 25)
        self.button_delete.setText("Eteindre")
        self.button_delete.clicked.connect(lambda: self.remove_box_robot())

        self.emergencyButton.setText("Arrêt d'urgence")
        self.emergencyButton.setStyleSheet(QEMERGENCYBUTTON)
        self.emergencyButton.setMaximumSize(250, 25)
        self.emergencyButton.clicked.connect(lambda: self.backend.emergency_stop_robot(self.rid))
        self.layout_name_delete.addWidget(self.button_delete)
        self.layout_name_delete.addWidget(self.emergencyButton)
        self.layout_box_robot.addLayout(self.layout_name_delete)

        # Configuration de l'affichage des coordonnées"
        self.lcdNumber_x = self.ui_setup_coord("X", "mm")
        self.lcdNumber_y = self.ui_setup_coord("Y", "mm")
        self.lcdNumber_theta = self.ui_setup_coord("θ", "°")
        self.layout_box_robot.addLayout(self.layout_coord)

        # Configuration de l'affichage du dernier message reçu
        self.label_last_message.setText("Dern. Msg (s):")
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
        """Configure un duo de widget (QLabel et QLCDNumber dans un QLayout) et renvoie le QLCDNumber"""

        self.label_coord = QLabel()
        self.label_coord.setText('{0} ({1})'.format(coord, unite))
        self.layout_coord.addWidget(self.label_coord)
        self.lcdNumber_coord = QLCDNumber()
        self.lcdNumber_coord.setFixedSize(QLCD_SIZE1)
        self.layout_coord.addWidget(self.lcdNumber_coord)
        return self.lcdNumber_coord

    def update_position(self, new_position):
        """ Met à jour la position de la boite robot """

        if new_position[0] == self.rid:
            # Mise à jour du vecteur position du robot
            self.x = float(new_position[1])
            self.y = float(new_position[2])
            self.theta = float(new_position[3])
            # Récupération du timestamp de dernière mise à jour de la position
            self.last_update_pos = float(new_position[4])

            # Mise à jour des valeurs affichées par les QLCDNUmber
            self.lcdNumber_x.display(self.x)
            self.lcdNumber_y.display(self.y)
            self.lcdNumber_theta.display(self.theta)

    def get_equipements(self):
        """ Charge la liste des des équipements du robot et les informations de chaque équipement présent.
            Renvoie le dictionnaire des équipements (clé= nom de l'équipement, valeur= objet de la class Equipement)"""

        # Mise à jour de la liste de l'équipement du robot
        self.equipement_list = self.backend.getdata_robot(self.rid)[1]
        equipements = {}

        for eqp_name in self.equipement_list:
            eqp = self.backend.getdata_eqp(self.rid, eqp_name)
            eqp_type = eqp[0]
            eqp_value = eqp[1]
            last_update = eqp[2]
            unit = eqp[4]
            value, min_val, max_val, step = eqp_value

            if eqp_name == "Batterie":
                self.battery_value = value
                self.battery_min = min_val
                self.battery_max = max_val
                self.battery_step = step

            elif eqp_type == annuaire.Actionneur or eqp_type == annuaire.Binaire:
                equipements[eqp_name] = Equipement(eqp_name, value, min_val, max_val, step, unit, last_update, "RW",
                                                   self.layout_box_actuators, self.rid, self.window)

            elif eqp_type == annuaire.Capteur:
                equipements[eqp_name] = Equipement(eqp_name, value, min_val, max_val, step, unit, last_update, "R",
                                                   self.layout_box_sensors, self.rid, self.window)

        return equipements

    @pyqtSlot()
    def update_equipements(self):
        """ Met à jour l'ensemble des équipements accrochés au robots et initialise la mise à jour de chaque
        équipement """
        # Met à jour le dictionnaire des équipements
        equipements = self.get_equipements()
        # Crée une liste des équipements présents sur le robot
        equipements_list = [key for key in equipements]

        # Ajoute les nouveaux équipements
        for name in set(equipements_list) - set(self.current_equipement_list):
            self.current_equipement_dic[name] = equipements[name]
            equipement = equipements[name]
            equipement.add_equipement()

        # Supprime les équipements qui ne sont plus présents
        for name in set(self.current_equipement_list) - set(equipements_list):
            equipement = self.current_equipement_dic.pop(name)
            equipement.remove_equipement()

        # Change les capteurs en actionneurs si néccessaire.
        for name in self.current_sensors_list:
            eqpment = equipements[name]
            if eqpment.permission == "RW":
                self.current_actuators_list.append(name)
                eqpment.add_equipement()
                self.current_sensors_list.pop(self.current_sensors_list.index(name))
                sensor = self.current_equipement_dic[name]
                sensor.remove_equipement()

        # Met à jour la liste et le dictionnaire des capteurs présents
        self.current_equipement_list = equipements_list
        self.current_equipement_dic = equipements

        # Emission pour chaque équipement de la nouvelle valeur et du nouveau ping
        for equipement in self.current_equipement_dic.values():

            # Ajoute le nom de l'actionneur dans la liste des actionneurs si l'équipement est un actionneur
            if equipement.permission == "RW":
                self.current_actuators_list.append(equipement.name)
            # Ajoute le nom du capteur dans la liste des capteurs si l'équipement est un capteur
            if equipement.permission == "R":
                self.current_sensors_list.append(equipement.name)

        # Cache la boite Capteurs si jamais aucun capteur n'est attaché au robot
        if not self.current_sensors_list:
            self.groupBox_sensors.hide()
        else:
            self.groupBox_sensors.show()

        # Cache la boite Actionneurs si jamais aucun actionneur n'est attaché au robot
        if not self.current_actuators_list:
            self.groupBox_actuators.hide()
        else:
            self.groupBox_actuators.show()

        # Mise à jour de la batterie si elle est déclarée
        self.update_battery()

        # Force le changement d'affichage des boites d'actionneurs et de capteurs.
        self.groupBox_actuators.repaint()
        self.groupBox_sensors.repaint()

    def update_battery(self):
        """ Met à jour l'affichage de la batterie si celle ci est déclarée """
        try:
            if self.battery_value is not None and self.battery_step != 0:
                self.layout_name_delete.addWidget(self.progressbar_battery)
                n = (float(self.battery_max)-float(self.battery_min))/float(self.battery_step)
                v = (float(self.battery_value)-float(self.battery_min))/float(self.battery_step)
                value = (v/n)*100
                self.progressbar_battery.setRange(0, 100)
                self.progressbar_battery.setValue(int(value))
                self.progressbar_battery.setFormat("%.01f %%" % value)
                self.progressbar_battery.setAlignment(QT_CENTER)
                if value < 10:
                    self.progressbar_battery.setStyleSheet(QPROGRESSBAR_LOW)
                elif value < 30:
                    self.progressbar_battery.setStyleSheet(QPROGRESSBAR_MEDIUM)
        except TypeError:
            print(self.battery_min, self.battery_max, self.battery_step)


    @pyqtSlot()
    def update_tab_robot(self):
        """ Initialise la mise à jour de la position et des équipements du robot de l'onglet' robot """

        # Récupération de la liste des équipements du robot
        new_equipements = self.backend.getdata_robot(self.rid)[1]
        # Emission du signal de mise à jour des équipements du robot
        self.list_equipement_changed_signal.emit(new_equipements)

    @pyqtSlot()
    def remove_box_robot(self):
        """ Initialise la suppression de l'onglet robot dont le numéro est placé en paramètre et envoie l'information
        à backend """
        self.window.inspecteur.remove_robot(self.rid)

    @pyqtSlot()
    def onEditingFinished(self):
        """"Appelée après la fin de l'édition de self.QLineEdit_positionCommand"""
        self.backend.sendposcmd_robot(self.rid, [int(i) for i in self.QLineEdit_positionCommand.text().split(' : ')])

    @pyqtSlot()
    def emergencyButtonPressed (self):
        """Appelée si le bouton d'arrêt d'urgence d'un robot est pressé"""
        self.backend.emergency_stop_robot (self.rid)

