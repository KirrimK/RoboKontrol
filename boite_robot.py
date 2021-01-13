""" boite_robot.py - Définit l'affichage d'une boite robot et de ses équipements """

import annuaire
import time
from PyQt5.QtWidgets import QLabel, QWidget, QSlider, QPushButton, QGridLayout, QGroupBox, QHBoxLayout, QVBoxLayout, \
    QLineEdit, QDialog, QColorDialog, QCheckBox, QDoubleSpinBox, QProgressBar, QSpacerItem, QLCDNumber, QComboBox
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QSize

# Customisation
QPROGRESSBAR = "QProgressBar{background-color : grey;border : 1px; border: 2px solid grey; border-radius: 5px}"
QLCD_STYLE = "QLCDNumber{background-color: grey;border: 2px solid rgb(113, 113, 113);border-width: 2px; " \
             "border-radius: 10px;  color: rgb(255, 255, 255)} "
QPUSHBUTTON = ""
# QtWidgets size
QLCD_SIZE1, QLCD_SIZE2 = QSize(60, 20), QSize(80, 20)
# Alignment
QT_CENTER, QT_RIGHT, QT_LEFT, QT_TOP = Qt.AlignCenter, Qt.AlignRight, Qt.AlignLeft, Qt.AlignTop


# TODO: régler le problème de mise à jour des capteurs

class Equipement(QWidget):
    """ Définit l'affichage d'un équipement attaché à un robot
        Arguments (cf annuaire.py):
            - variety (str): actionneur(envoie des commandes et reçoit des messages) ou capteur (reçoit des messages)
            - kind (str): définit le type d'affichage (QtWidget) de l'équipement (discret, binaire,
                        multiple,complexe, led, valeur, bar)
            - parent_layout (QLayout): layout dans lequel sera ajouté l'affichage de l'équipement
            - window (QWidget): fenêtre principale de l'application
            """

    # Création du signal de mise à jour de la valeur de l'équipement
    value_changed_signal = pyqtSignal(float)
    # Création du signal de mise à jour de la valeur de dernier message reçu
    ping_changed_signal = pyqtSignal(float)

    def __init__(self, name, value, min_val, max_val, step, unite, last_update, variety, kind, parent_layout, rid: str,
                 window):
        super(Equipement, self).__init__()
        # Instanciation des attributs de l'équipement
        self.name = name
        self.value = value
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.unite = unite
        self.last_update = last_update
        self.variety = variety
        self.kind = kind
        self.parent_layout = parent_layout
        self.rid = rid
        self.window = window
        self.timestamp = time.time()
        self.ping = abs(self.timestamp - self.last_update)
        self.backend = self.window.backend

        # Création des widgets de l'équipement
        self.gridLayout_equipement = QGridLayout()
        self.spacerItem_equipement = QSpacerItem(1, 10)

        self.label_name_equipement = QLabel()
        self.label_message_equipement = QLabel()
        self.lcdNumber_ping_equipement = QLCDNumber()

        if self.kind == "BINAIRE":
            self.checkBox_equipement = QCheckBox()
            self.label_command = QLabel()
            self.label_last_command = QLabel()

        if self.kind == "DISCRET":
            self.layout_discret = QHBoxLayout()
            self.slider_equipement = QSlider(Qt.Horizontal)
            self.doubleSpinBox_equipement = QDoubleSpinBox()
            self.label_command = QLabel()
            self.label_last_command = QLabel()

        if self.kind == "MULTIPLE":
            self.comboBox_equipement = QComboBox()
            self.label_command = QLabel()
            self.label_last_command = QLabel()

        if self.kind == "COMPLEXE":
            self.pushButton_equipement = QPushButton()
            self.label_command = QLabel()
            self.label_last_command = QLabel()

        if self.kind == "LED":
            self.pushButton_led = QPushButton()
            self.label_command = QLabel()
            self.label_last_command = QLabel()

        if self.kind == "VALEUR":
            self.lcdNumber_equipement = QLCDNumber()

        if self.kind == "BAR":
            self.progressBar_equipement = QProgressBar()

        # Configuration des widgets de l'équipement
        self.ui_setup_equipement()

        # Connexion du signal de pin du dernier message reçu màj avec le slot d'affichage du ping du dernier message
        self.ping_changed_signal.connect(self.onPingChangedSignal )

    def onPingChangedSignal (self,ping):
        self.lcdNumber_ping_equipement.display(str(round(ping, 1)))
#        print (self.lcdNumber_ping_equipement.value ())
        self.window.repaint ()

        self.value_changed_signal.connect(lambda val: self.update_equipement(val))

    def ui_setup_equipement(self):
        """ Configure l'ensemble des widgets de l'équipement"""

        self.gridLayout_equipement.setAlignment(QT_TOP)

        self.label_name_equipement.setMaximumSize(100, 25)
        if self.unite == "None" or self.unite is None:
            self.label_name_equipement.setText(self.name)
        else:
            self.label_name_equipement.setText('{0} ({1}):'.format(self.name, self.unite))
        self.gridLayout_equipement.addWidget(self.label_name_equipement, 0, 0, 1, 1, QT_LEFT)

        self.label_message_equipement.setText("Dern. Msg (ms) : {}".format (round (self.ping,1)))
        self.gridLayout_equipement.addWidget(self.label_message_equipement, 1, 0, 1, 1, QT_LEFT)
        self.lcdNumber_ping_equipement.setMaximumSize(QSize(75, 25))
        self.lcdNumber_ping_equipement.setStyleSheet(QLCD_STYLE)
        self.lcdNumber_ping_equipement.setFixedSize(QLCD_SIZE2)
        self.gridLayout_equipement.addWidget(self.lcdNumber_ping_equipement, 1, 1, 1, 1, QT_RIGHT)

        if self.kind == "BINAIRE":
            self.checkBox_equipement.setText("")
            self.checkBox_equipement.stateChanged.connect(lambda: self.oncheckbox_toggled())
            self.gridLayout_equipement.addWidget(self.checkBox_equipement, 0, 1, 1, 1, QT_CENTER)

        if self.kind == "DISCRET":
            self.slider_equipement.setFixedSize(100, 30)
            self.slider_equipement.setMinimum(self.min_val)
            self.slider_equipement.setMaximum(self.max_val)
            self.slider_equipement.setSingleStep(self.step)
            self.slider_equipement.valueChanged.connect(lambda: self.onvaluechanged_slider())
            self.layout_discret.addWidget(self.slider_equipement)
            self.doubleSpinBox_equipement.setFixedSize(50, 30)
            self.doubleSpinBox_equipement.setMaximum(self.max_val)
            self.doubleSpinBox_equipement.setMinimum(self.min_val)
            self.doubleSpinBox_equipement.setSingleStep(self.step)
            self.doubleSpinBox_equipement.valueChanged.connect(lambda: self.onvaluechanged())
            self.layout_discret.addWidget(self.doubleSpinBox_equipement)
            self.gridLayout_equipement.addLayout(self.layout_discret, 0, 1, 1, 1, QT_RIGHT)

        if self.kind == "MULTIPLE":
            self.gridLayout_equipement.addWidget(self.comboBox_equipement, 0, 1, 1, 1, QT_RIGHT)

        if self.kind == "COMPLEXE":
            self.pushButton_equipement.setText(self.info_actionneur[0])
            self.pushButton_equipement.clicked.connect(lambda: self.open_actionneur_complexe())
            self.gridLayout_equipement.addWidget(self.pushButton_equipement, 0, 1, 1, 1, QT_RIGHT)

        if self.kind == "LED":
            self.pushButton_led.setText('Choisir la couleur')
            self.pushButton_led.clicked.connect(lambda: self.open_led_menu())
            self.gridLayout_equipement.addWidget(self.pushButton_led, 0, 1, 1, 1, QT_RIGHT)

        if self.kind == "VALEUR":
            self.lcdNumber_equipement.setMinimumSize(150, 30)
            self.lcdNumber_equipement.setStyleSheet(QLCD_STYLE)
            self.gridLayout_equipement.addWidget(self.lcdNumber_equipement, 0, 1, 1, 1, QT_RIGHT)

            # Connexion du signal de màj de la valeur avec la slot d'affichage de la valeur'
            # self.value_changed_signal.connect(lambda val: self.lcdNumber_equipement.display(int(val)))

        if self.kind == "BAR":
            self.progressBar_equipement = QProgressBar()
            self.progressBar_equipement.setRange(int(self.min_val), int(self.max_val))
            self.progressBar_equipement.setStyleSheet(QPROGRESSBAR)
            self.progressBar_equipement.setAlignment(QT_CENTER)
            self.progressBar_equipement.setFixedSize(150, 30)
            self.gridLayout_equipement.addWidget(self.progressBar_equipement, 0, 1, 1, 1, QT_RIGHT)

            # Connexion du signal de màj de la bar de progression avec la slot d'affichage de la valeur'
            # self.value_changed_signal.connect(lambda val: self.progressBar_equipement.setValue(int(val)))

    def add_equipement(self):
        """ Ajoute l'équipement dans la bon layout parent selon qu'il est actionneur ou capteur"""

        if self.variety == "ACTIONNEUR":
            self.parent_layout.addItem(self.spacerItem_equipement)
            self.label_command.setText("None")
            self.gridLayout_equipement.addWidget(self.label_command, 2, 1, 1, 1, QT_RIGHT)
            self.label_last_command.setText("Dern. Cmd:")
            self.gridLayout_equipement.addWidget(self.label_last_command, 2, 0, 1, 1, QT_LEFT)

        if self.variety == "CAPTEUR":
            self.parent_layout.addItem(self.spacerItem_equipement)

        # Ajoute l'affichage de l'équipement dans le parent layout
        self.parent_layout.addLayout(self.gridLayout_equipement)

    def remove_equipement(self):
        """ Retire l'affichage de l'équipement"""

        self.gridLayout_equipement.hide()

    @pyqtSlot()
    def open_led_menu(self):
        """Ouvre une fenêtre de sélection de couleur (QColorDialog) et modifie la valeur de l'actionneur la couleur
        choisie """

        self.value = QColorDialog.getColor().name()
        self.pushButton_led.setStyleSheet("background-color : {0};".format(self.value))

    @pyqtSlot()
    def open_actionneur_complexe(self):
        """Ouvre un QDilaog (à compléter) qui change la valeur de l'actionneur"""

        self.value = QDialog()

    @pyqtSlot()
    def onvaluechanged(self):
        """ Affiche et envoie vers backend la dernière commande d'un actionneur discret"""
        self.backend.sendeqpcmd(self.rid, self.name, self.doubleSpinBox_equipement.value())
        self.label_command.setText(str(self.doubleSpinBox_equipement.value()))
        self.slider_equipement.setValue(int(self.doubleSpinBox_equipement.value()))

    @pyqtSlot()
    def onvaluechanged_slider(self):
        """ Affiche et envoie vers backend la dernière commande d'un actionneur discret"""
        self.backend.sendeqpcmd(self.rid, self.name, self.doubleSpinBox_equipement.value())
        self.label_command.setText(str(self.slider_equipement.value()))
        self.doubleSpinBox_equipement.setValue((self.slider_equipement.value()))

    @pyqtSlot()
    def oncheckbox_toggled(self):
        """ Affiche et renvoie vers backend la dernière commande d'un actionneur binaire"""
        if self.checkBox_equipement.isChecked():
            self.backend.sendeqpcmd(self.rid, self.name, 1)
            self.label_command.setText(str(1))
        else:
            self.backend.sendeqpcmd(self.rid, self.name, 0)
            self.label_command.setText(str(0))

    @pyqtSlot()
    def update_ping(self, ping):
        # Calcul et mise à jour du denier message reçu

        self.lcdNumber_ping_equipement.display(str(round(ping, 1)))

    @pyqtSlot()
    def update_equipement(self, value):
        """ Met à jour l'équipement suivant son type"""

        # self.ping_changed_signal.emit(self.ping)

        if self.kind == "BINAIRE":
            if self.value == 0:
                self.checkBox_equipement.setChecked(False)
            if self.value == 1:
                self.checkBox_equipement.setChecked(True)

        if self.kind == "DISCRET" and self.value is not None:
            self.doubleSpinBox_equipement.setValue(self.value)
            self.slider_equipement.setValue(self.value)
            # print ('Updated to {}'.format(self.slider_equipement.value()))

        if self.kind == "MULTIPLE":
            pass

        if self.kind == "COMPLEXE":
            pass

        if self.kind == "LED":
            self.pushButton_led.setStyleSheet("background: {}".format(self.value))

        if self.kind == "VALEUR":
            if self.value is not None:
                # Emission de signal de màj de la valeur de l'équipement
                self.lcdNumber_equipement.display(value)

        if self.kind == "BAR" and self.value is not None:
            self.progressBar_equipement.setValue(int(value))


class BoiteRobot(QWidget):
    """Définit l'affiche d'un robot sous forme d'un QGroupBox """

    # Création de signal de mise jour de la liste des équipements associés au robot
    list_equipement_changed_signal = pyqtSignal(list)

    def __init__(self, rid: str, main_window):

        super().__init__()
        self.rid = rid
        self.main_window = main_window

        self.position = ()
        self.timestamp = time.time()
        self.backend = self.main_window.backend

        # Création de la boite robot (QGroupBox)
        self.groupBox_robot = QGroupBox()
        self.groupBox_robot.setMaximumSize(400, 16777215)
        #self.groupBox_robot.setStyleSheet("QGroupBox { background-color: rgb(255, 255, 255); border: 1px solid grey; }")
        self.layout_box_robot = QVBoxLayout(self.groupBox_robot)

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

        # Liste des équipements attachés au robot
        self.current_equipement_list = []
        self.current_equipement_dic = {}
        self.current_actuators_list = []
        self.current_actionneurs_dic = {}
        self.current_sensors_list = []
        self.current_capteurs_dic = {}

        # Configuration des widgets de la boite robot
        self.ui_setup_boite_robot()

        self.QLineEdit_position_command = None

        # self.main_window.timer.timeout.connect(lambda: self.update_boite_robot())
        # Connexion du signal de mise à jours des équipements avec le slot de mise à jour de l'ensemble des équipements
        self.list_equipement_changed_signal.connect(lambda: self.update_equipements())

    def ui_setup_boite_robot(self):
        """ Configure l'ensemble de la boite robot"""

        # Configuration de l'affichage du nom robot et du bouton oublier
        self.label_name.setMinimumSize(0, 30)
        # self.label_name.setMaximumSize(100, 30)
        self.label_name.setText(self.rid)
        self.layout_name_delete.addWidget(self.label_name)
        self.button_delete.setMaximumSize(150, 25)
        self.button_delete.setStyleSheet(QPUSHBUTTON)
        self.button_delete.setText("Oublier")
        self.button_delete.clicked.connect(lambda: self.remove_box_robot())
        self.layout_name_delete.addWidget(self.button_delete)
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
        self.QLineEdit_positionCommand.setInputMask("0000 : 0000 : 000")
        self.QLineEdit_positionCommand.setText("1500 : 1000 : 000")
        self.QLineEdit_positionCommand.setFixedSize(130, 30)
        self.QLineEdit_positionCommand.editingFinished.connect(lambda: self.onEditingFinished())
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

    def update_position(self):
        """ Met à jour la position de la boite robot """

        # Mise à jour du vecteur position du robot
        self.position = self.backend.getdata_robot(self.rid)[0]
        # Récupération du timestamp de dernière mise à jour de la position
        self.last_update_pos = self.backend.getdata_robot(self.rid)[2]

        # Calcul du ping
        self.timestamp = time.time()
        self.ping = abs(self.last_update_pos - self.timestamp)

        # Mise à jour des valeurs affichées par les QLCDNUmber
        self.lcdNumber_x.display(self.position[0])
        self.lcdNumber_y.display(self.position[1])
        self.lcdNumber_theta.display(self.position[2])
        self.lcdNumber_last_message.display(str(round(self.ping, 1)))

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
            # eqp_last_cmd = eqp[3]
            unit = eqp[4]
            value, min_val, max_val, step = eqp_value

            if eqp_type == annuaire.Actionneur:
                equipements[eqp_name] = Equipement(eqp_name, value, min_val, max_val, step, unit, last_update,
                                                   "ACTIONNEUR",
                                                   "DISCRET", self.layout_box_actuators, self.rid, self.main_window)

            if eqp_type == annuaire.Binaire:
                equipements[eqp_name] = Equipement(eqp_name, value, 0, 1, 1, None, last_update, "ACTIONNEUR", "BINAIRE",
                                                   self.layout_box_actuators, self.rid, self.main_window)

            if eqp_type == annuaire.Capteur:

                if min_val is None or max_val is None or step is None:
                    kind = "VALEUR"
                else:
                    kind = "BAR"
                equipements[eqp_name] = Equipement(eqp_name, value, min_val, max_val, step, unit, last_update,
                                                   "CAPTEUR", kind, self.layout_box_sensors, self.rid, self.main_window)


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
            equipement = equipements[name]
            if equipement.variety == "Actionneur":
                self.current_actuators_list.append(name)
                self.current_sensors_list.pop(self.current_sensors_list.index(name))
                sensor = self.current_equipement_dic[name]

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

        # self.layout_box_actuators.update()

        #Force le changement d'affichage des boites d'actionneurs et de capteurs.
        self.groupBox_actuators.repaint ()
        self.groupBox_sensors.repaint ()

    @pyqtSlot()
    def update_boite_robot(self):
        """ Initialise la mise à jour de la position et des équipements du robot de la boite robot """

        # Initialise la mise à jours de la position du robot
        self.update_position()
        # Récupération de la liste des équipements du robot
        new_equipements = self.backend.getdata_robot(self.rid)[1]
        # Emission du signal de mise à jour des équipements du robot
        self.list_equipement_changed_signal.emit(new_equipements)

    @pyqtSlot()
    def remove_box_robot(self):
        """ Supprime  la boite robot dont le numéro est placé en paramètre et envoie l'information à backend """

        self.groupBox_robot.hide()
        self.backend.stopandforget_robot(self.rid)

    @pyqtSlot()
    def onEditingFinished(self):
        """"Appelée après la fin de l'édition de self.QLineEdit_positionCommand"""
        self.backend.sendposcmd_robot(self.rid, [int(i) for i in self.QLineEdit_positionCommand.text().split(' : ')])

    @pyqtSlot()
    def emergencyButtonPressed (self):
        """Appelée si le bouton d'arrêt d'urgence d'un robot est pressé"""
        self.backend.emergency_stop_robot (self.rid)
