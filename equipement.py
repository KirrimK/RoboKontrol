""" equipement.py - Définit l'affichage d'un équipement"""

import time
from PyQt5.QtWidgets import QLabel, QWidget, QSlider, QPushButton, QGridLayout, QHBoxLayout,\
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
            - variety (str): actionneur(envoie des commandes et reçoit des messages: "R&W") ou capteur (reçoit des messages: "R")
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
        self.spacerItem_equipement = QSpacerItem(1, 15)

        self.label_name_equipement = QLabel()
        self.label_message_equipement = QLabel()
        self.lcdNumber_ping_equipement = QLCDNumber()

        if self.kind == "BINAIRE":
            self.checkBox_equipement = QCheckBox()
            self.label_command = QLineEdit()
            self.label_last_command = QLabel()

        if self.kind == "DISCRET":
            self.layout_discret = QHBoxLayout()
            self.slider_equipement = QSlider(Qt.Horizontal)
            self.doubleSpinBox_equipement = QDoubleSpinBox()
            self.label_command = QLineEdit()
            self.label_last_command = QLabel()

        if self.kind == "MULTIPLE":
            self.comboBox_equipement = QComboBox()
            self.label_command = QLineEdit()
            self.label_last_command = QLabel()

        if self.kind == "COMPLEXE":
            self.pushButton_equipement = QPushButton()
            self.label_command = QLineEdit()
            self.label_last_command = QLabel()

        if self.kind == "LED":
            self.pushButton_led = QPushButton()
            self.label_command = QLineEdit()
            self.label_last_command = QLabel()

        if self.kind == "VALEUR":
            self.lcdNumber_equipement = QLCDNumber()

        if self.kind == "BAR":
            self.progressBar_equipement = QProgressBar()

        # Configuration des widgets de l'équipement
        self.ui_setup_equipement()

        # Connexion du signal de pin du dernier message reçu màj avec le slot d'affichage du ping du dernier message
        self.ping_changed_signal.connect(self.onPingChangedSignal)

    def onPingChangedSignal(self, ping):
        self.lcdNumber_ping_equipement.display(str(round(ping, 1)))
        # print (self.lcdNumber_ping_equipement.value ())
        self.window.repaint()

    def ui_setup_equipement(self):
        """ Configure l'ensemble des widgets de l'équipement"""

        self.gridLayout_equipement.setAlignment(QT_TOP)

        # self.label_name_equipement.setMaximumSize(100, 25)
        if self.unite == "None" or self.unite is None:
            self.label_name_equipement.setText(self.name)
        else:
            self.label_name_equipement.setText('{0} ({1})'.format(self.name, self.unite))
        self.gridLayout_equipement.addWidget(self.label_name_equipement, 0, 0, 1, 1, QT_LEFT)

        self.label_message_equipement.setText("Dern. Msg (ms) : {}".format(round(self.ping, 1)))
        self.gridLayout_equipement.addWidget(self.label_message_equipement, 2, 0, 1, 1, QT_LEFT)
        self.lcdNumber_ping_equipement.setMaximumSize(QSize(75, 25))
        self.lcdNumber_ping_equipement.setStyleSheet(QLCD_STYLE)
        self.lcdNumber_ping_equipement.setFixedSize(QLCD_SIZE2)
        self.gridLayout_equipement.addWidget(self.lcdNumber_ping_equipement, 2, 1, 1, 1, QT_RIGHT)

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
            self.doubleSpinBox_equipement.setFixedSize(75, 30)
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

        if self.variety == "R&W":
            self.parent_layout.addItem(self.spacerItem_equipement)
            self.label_command.setText("None")
            self.label_command.setFixedSize(75, 30)
            self.label_command.setReadOnly(True)
            self.gridLayout_equipement.addWidget(self.label_command, 1, 1, 1, 1, QT_RIGHT)
            self.label_last_command.setText("Dern. Cmd:")
            self.gridLayout_equipement.addWidget(self.label_last_command, 1, 0, 1, 1, QT_LEFT)

        if self.variety == "R":
            self.parent_layout.addItem(self.spacerItem_equipement)

        # Ajoute l'affichage de l'équipement dans le parent layout
        self.parent_layout.addLayout(self.gridLayout_equipement)

    def remove_equipement(self):  # todo: non testé
        """ Retire l'affichage de l'équipement"""
        try:
            for i in reversed(range(self.gridLayout_equipement.count())):
                self.gridLayout_equipement.itemAt(i).widget().setParent(None)
        except AttributeError:
            pass

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
        self.doubleSpinBox_equipement.setValue(self.slider_equipement.value())

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
    def update_ping(self, last_update):
        # Calcul et mise à jour du denier message reçu
        self.timestamp = time.time()
        self.ping = abs(self.timestamp - last_update)
        self.lcdNumber_ping_equipement.display(str(round(self.ping, 1)))

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