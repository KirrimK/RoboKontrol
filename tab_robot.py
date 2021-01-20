""" tab_robot.py - Définit l'affichage d'un onglet robot"""

import time
import annuaire
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QGroupBox, QHBoxLayout, QVBoxLayout,QLineEdit, QLCDNumber, \
     QScrollArea, QFrame
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QSize
from equipement import Equipement

# Customisation
QLCD_STYLE = "QLCDNumber{background-color: grey;border: 2px solid rgb(113, 113, 113);border-width: 2px; " \
             "border-radius: 10px;  color: rgb(255, 255, 255)} "
QPUSHBUTTON = ""
QEMERGENCYBUTTON = "QPushButton{background-color : rgb(255, 0, 0)}"
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
        self.timestamp = time.time()
        self.backend = self.window.backend

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
        self.label_name = QLabel()
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
        self.last_update_pos = time.time ()

        # Liste des équipements attachés au robot
        self.current_equipement_list = []
        self.current_equipement_dic = {}
        self.current_actuators_list = []

        self.current_sensors_list = []

        # Configuration des widgets de la boite robot
        self.ui_setup_tab_robot()

        self.QLineEdit_position_command = None

        # Connexion du signal de mise à jours des équipements avec le slot de mise à jour de l'ensemble des équipements
        #self.list_equipement_changed_signal.connect(self.update_equipements)

    def ui_setup_tab_robot(self):
        """ Configure l'ensemble de l'onglet robot"""

        # Configuration de l'affichage du nom robot et du bouton oublier
        self.label_name.setMinimumSize(0, 30)
        # self.label_name.setMaximumSize(100, 30)
        self.label_name.setText(self.rid)
        self.layout_name_delete.addWidget(self.label_name)
        self.button_delete.setMaximumSize(150, 25)
        self.button_delete.setStyleSheet(QPUSHBUTTON)
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
        self.lcdNumber_last_message.setStyleSheet(QLCD_STYLE)
        self.layout_last_message.addWidget(self.lcdNumber_last_message)
        self.layout_box_robot.addLayout(self.layout_last_message)

        # Confiuration de l'envoyeur de commandes de postion
        self.label_positionCommand.setText("Dern. PosCmd:")
        self.layout_last_command.addWidget(self.label_positionCommand)
        self.QLineEdit_positionCommand = QLineEdit()
        self.QLineEdit_positionCommand.setText("1500 : 1000: 000")
        self.QLineEdit_positionCommand.setInputMask("0000 : 0000 : 000")
        self.QLineEdit_positionCommand.setFixedSize(95, 25)
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
        self.lcdNumber_coord.setStyleSheet(QLCD_STYLE)
        self.layout_coord.addWidget(self.lcdNumber_coord)
        return self.lcdNumber_coord

    def update_position(self, position = None, new = False):
        """ Met à jour la position de la boite robot """
        
        if new:
            # Récupération du timestamp de dernière mise à jour de la position
            self.last_update_pos = time.time ()
            # Mise à jour des valeurs affichées par les QLCDNUmber
            self.lcdNumber_x.display(self.position[0])
            self.lcdNumber_y.display(self.position[1])
            self.lcdNumber_theta.display(self.position[2])

        # Calcul du ping
        self.timestamp = time.time()
        self.ping = abs(self.last_update_pos - self.timestamp)

        
        self.lcdNumber_last_message.display(str(round(self.ping, 1)))

    def newEquipment (self, eid, minV, maxV, step, droits, unit):
        self.current_equipement_list.append [eid]
        if droits == "RW" :
            self.current_actuators_list.append (eid)
            if float (minv) + float (step) >= float (maxv) :
                kind  = "BINAIRE"
            else :
                kind = "DISCRET"
        elif droits == "READ":
            self.current_sensors_list.append (eid)
            if None in (minV, maxV, step):
                kind = "VALEUR"
            else :
                kind = "BAR"
        self.self.current_equipement_dic [eid] = Equipement (eid, None, minV, maxV, step, unit, droits,
                                                             kind, parent_layout, self.rid, self.window)
    @pyqtSlot()
    def update_tab_robot(self):
        """ Mise à jour des pings """

        # Initialise la mise à jours de la position du robot
        self.update_position()
        for eqp in self.current_equipement_dic.values ():
            eqp.update_ping ()
        
        """# Récupération de la liste des équipements du robot
        new_equipements = self.backend.getdata_robot(self.rid)[1]
        # Emission du signal de mise à jour des équipements du robot
        self.list_equipement_changed_signal.emit(new_equipements)"""

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

"""    def get_equipements(self):
        Charge la liste des des équipements du robot et les informations de chaque équipement présent.
            Renvoie le dictionnaire des équipements (clé= nom de l'équipement, valeur= objet de la class Equipement)

        # Mise à jour de la liste de l'équipement du robot
        self.equipement_list = self.backend.getdata_robot(self.rid)[1]
        equipements = {}

        for eqp_name in self.equipement_list:
            eqp = self.backend.getdata_eqp(self.rid, eqp_name)
            eqp_type = eqp[0]
            eqp_value = eqp[1]
            last_update = eqp[2]
            # eqp_last_cmd = eqp[3]
            unit = eqp[4]
            value, min_val, max_val, step = eqp_value

            if eqp_type == annuaire.Actionneur:
                equipements[eqp_name] = Equipement(eqp_name, value, min_val, max_val, step, unit, last_update, "R&W",
                                                   "DISCRET", self.layout_box_actuators, self.rid, self.window)

            if eqp_type == annuaire.Binaire:
                equipements[eqp_name] = Equipement(eqp_name, value, 0, 1, 1, None, last_update, "R&W", "BINAIRE",
                                                   self.layout_box_actuators, self.rid, self.window)

            if eqp_type == annuaire.Capteur:

                if min_val is None or max_val is None or step is None:
                    kind = "VALEUR"
                else:
                    kind = "BAR"
                equipements[eqp_name] = Equipement(eqp_name, value, min_val, max_val, step, unit, last_update,
                                                   "R", kind, self.layout_box_sensors, self.rid, self.window)

        return equipements

    @pyqtSlot()
    def update_equipements(self):
         Met à jour l'ensemble des équipements accrochés au robots et initialise la mise à jour de chaque
        équipement 
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
            if eqpment.variety == "R&W":
                self.current_actuators_list.append(name)
                eqpment.add_equipement ()
                self.current_sensors_list.pop(self.current_sensors_list.index(name))
                sensor = self.current_equipement_dic[name]
                sensor.remove_equipement ()

        # Met à jour la liste et le dictionnaire des capteurs présents
        self.current_equipement_list = equipements_list
        self.current_equipement_dic = equipements

        # Emission pour chaque équipement de la nouvelle valeur et du nouveau ping
        for equipement in self.current_equipement_dic.values():
            # Récupération de la nouvelle valeur
            value = equipement.value
            # Calcul du ping
            last_update = equipement.last_update
            ping = abs(time.time() - last_update)
            if equipement.value is not None:
                # Emission de la nouvelle valeur de l'équipement
                equipement.value_changed_signal.emit(value)
            # Emission du nouveau ping de l'équipement
            equipement.ping_changed_signal.emit(ping)

            # Ajoute le nom de l'actionneur dans la liste des actionneurs si l'équipement est un actionneur
            if equipement.variety == "R&W":
                self.current_actuators_list.append(equipement.name)
            # Ajoute le nom du capteur dans la liste des capteurs si l'équipement est un capteur
            if equipement.variety == "R":
                self.current_sensors_list.append(equipement.name)

            # print(equipement.name, value, ping)

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

        # Force le changement d'affichage des boites d'actionneurs et de capteurs.
        self.groupBox_actuators.repaint()
        self.groupBox_sensors.repaint()
"""
