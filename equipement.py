""" equipement.py - Définit l'affichage d'un équipement"""

import time
from PyQt5.QtWidgets import QLabel, QWidget, QSlider, QPushButton, QGridLayout, QHBoxLayout,\
    QLineEdit, QDialog, QColorDialog, QCheckBox, QDoubleSpinBox, QProgressBar, QSpacerItem, QLCDNumber, QComboBox
from PyQt5.QtCore import pyqtSlot, Qt, QSize, QTimer #pyqtSignal


# Customisation
QPROGRESSBAR = "QProgressBar{background-color : grey;border : 1px; border: 2px solid grey; border-radius: 5px} "
# QtWidgets size
QLCD_SIZE1, QLCD_SIZE2 = QSize(60, 20), QSize(80, 20)
# Alignment
QT_CENTER, QT_RIGHT, QT_LEFT, QT_TOP = Qt.AlignCenter, Qt.AlignRight, Qt.AlignLeft, Qt.AlignTop


class Equipement(QWidget):
    """ Définit l'affichage d'un équipement attaché à un robot
        Arguments:
            - cf annuaire.py
            - permission (str): actionneur(envoie des commandes et reçoit des messages: "RW") ou capteur (reçoit des messages: "R")
            - parent_layout (QLayout): layout dans lequel sera ajouté l'affichage de l'équipement
            - window (QWidget): fenêtre principale de l'application
            """

    def __init__(self, name, value, min_val, max_val, step, unite, last_update, permission, parent_layout, rid: str,
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
        self.permission = permission
        self.parent_layout = parent_layout
        self.rid = rid
        self.window = window
        self.timestamp = time.time()
        self.ping = abs(self.timestamp - self.last_update)
        self.backend = self.window.backend
        self.updated_from_outside = False

        if self.permission == "RW":
            if self.min_val == 0 and self.max_val == 1 and self.step ==1:
                self.type_widget = "BINAIRE"
            elif self.name == "LED":
                self.type_widget = "LED"
            else:
                self.type_widget = "DISCRET"

        if self.permission == "R":
            if self.min_val is None or self.max_val is None or self.step is None:
                self.type_widget = "VALEUR"
            else:
                self.type_widget = "BAR"

        # Création des widgets de l'équipement
        self.gridLayout_equipement = QGridLayout()
        self.spacerItem_equipement = QSpacerItem(1, 15)
        self.label_name_equipement = QLabel()
        self.label_message_equipement = QLabel()
        self.lcdNumber_ping_equipement = QLCDNumber()

        if self.type_widget == "BINAIRE":
            self.layout_binaire = QHBoxLayout()
            self.checkBox_equipement = QCheckBox()
            self.label_command = QLineEdit()
            self.label_last_command = QLabel()
            self.label_binaire = QLabel()

        if self.type_widget == "DISCRET":
            self.layout_discret = QHBoxLayout()
            self.slider_equipement = QSlider(Qt.Horizontal)
            self.doubleSpinBox_equipement = QDoubleSpinBox()
            self.label_command = QLineEdit()
            self.label_last_command = QLabel()

        if self.type_widget == "MULTIPLE":
            self.comboBox_equipement = QComboBox()
            self.label_command = QLineEdit()
            self.label_last_command = QLabel()

        if self.type_widget == "COMPLEXE":
            self.pushButton_equipement = QPushButton()
            self.label_command = QLineEdit()
            self.label_last_command = QLabel()

        if self.type_widget == "LED":
            self.pushButton_led = QPushButton()
            self.label_command = QLineEdit()
            self.label_last_command = QLabel()

        if self.type_widget == "VALEUR":
            self.lcdNumber_equipement = QLCDNumber()

        if self.type_widget == "BAR":
            self.progressBar_equipement = QProgressBar()

        # Configuration des widgets de l'équipement
        self.ui_setup_equipement()

        self.backend.widget.CaptRegSignal.connect(lambda current_state: self.update_equipement(current_state))

    #calcul et mise à jour du ping
    def update_ping(self, last_update: float):
        self.last_update = last_update
        self.ping = round(abs(time.time() - self.last_update), 1)
        self.lcdNumber_ping_equipement.display(format(self.ping))

    def update_last_message(self, last_message: list):
        if last_message[0] == self.rid and last_message[1] == self.name:
            self.update_ping(last_message[2])

    def ui_setup_equipement(self):
        """ Configure l'ensemble des widgets de l'équipement"""

        self.gridLayout_equipement.setAlignment(QT_TOP)

        if self.unite == "None" or self.unite is None:
            self.label_name_equipement.setText(self.name)
        else:
            self.label_name_equipement.setText('{0} ({1})'.format(self.name, self.unite))
        self.gridLayout_equipement.addWidget(self.label_name_equipement, 0, 0, 1, 1, QT_LEFT)

        self.label_message_equipement.setText("Dernière MAJ (s)")
        self.gridLayout_equipement.addWidget(self.label_message_equipement, 2, 0, 1, 2, QT_LEFT)
        self.lcdNumber_ping_equipement.setMaximumSize(QSize(75, 25))
        self.lcdNumber_ping_equipement.setFixedSize(QLCD_SIZE2)
        self.gridLayout_equipement.addWidget(self.lcdNumber_ping_equipement, 2, 1, 1, 1, QT_RIGHT)

        if self.type_widget == "BINAIRE":
            self.label_binaire.setFixedSize(100, 20)
            self.checkBox_equipement.stateChanged.connect(lambda: self.oncheckbox_toggled())
            self.layout_binaire.addWidget(self.label_binaire)
            self.layout_binaire.addWidget(self.checkBox_equipement)
            self.gridLayout_equipement.addLayout(self.layout_binaire, 0, 1, 1, 1, QT_CENTER)

        if self.type_widget == "DISCRET":
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

        if self.type_widget == "MULTIPLE":
            self.gridLayout_equipement.addWidget(self.comboBox_equipement, 0, 1, 1, 1, QT_RIGHT)

        if self.type_widget == "COMPLEXE":
            self.pushButton_equipement.clicked.connect(lambda: self.open_actionneur_complexe())
            self.gridLayout_equipement.addWidget(self.pushButton_equipement, 0, 1, 1, 1, QT_RIGHT)

        if self.type_widget == "LED":
            self.pushButton_led.setText('Choisir la couleur')
            self.pushButton_led.clicked.connect(lambda: self.open_led_menu())
            self.gridLayout_equipement.addWidget(self.pushButton_led, 0, 1, 1, 1, QT_RIGHT)

        if self.type_widget == "VALEUR":
            self.lcdNumber_equipement.setMinimumSize(150, 30)
            self.gridLayout_equipement.addWidget(self.lcdNumber_equipement, 0, 1, 1, 1, QT_RIGHT)

        if self.type_widget == "BAR":
            self.progressBar_equipement = QProgressBar()
            self.progressBar_equipement.setRange(int(self.min_val), int(self.max_val))
            self.progressBar_equipement.setStyleSheet(QPROGRESSBAR)
            self.progressBar_equipement.setAlignment(QT_CENTER)
            self.progressBar_equipement.setFormat("%v")
            self.progressBar_equipement.setFixedSize(150, 30)
            self.gridLayout_equipement.addWidget(self.progressBar_equipement, 0, 1, 1, 1, QT_RIGHT)

    def add_equipement(self):
        """ Ajoute l'équipement dans la bon layout parent selon qu'il est actionneur ou capteur"""

        if self.permission == "RW":
            self.parent_layout.addItem(self.spacerItem_equipement)
            self.label_command.setText("None")
            self.label_command.setFixedSize(75, 30)
            self.label_command.setReadOnly(True)
            self.label_command.setAlignment(QT_CENTER)
            self.gridLayout_equipement.addWidget(self.label_command, 1, 1, 1, 1, QT_RIGHT)
            self.label_last_command.setText("Dern. Cmd:")
            self.gridLayout_equipement.addWidget(self.label_last_command, 1, 0, 1, 1, QT_LEFT)

        if self.permission == "R":
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
        """Ouvre un QDialog (à compléter) qui change la valeur de l'actionneur"""

        self.value = QDialog()

    @pyqtSlot()
    def onvaluechanged(self):
        """ Affiche et envoie vers backend la dernière commande d'un actionneur discret"""
        if not self.updated_from_outside:
            self.backend.sendeqpcmd(self.rid, self.name, self.doubleSpinBox_equipement.value())
            self.label_command.setText(str(self.doubleSpinBox_equipement.value()))
            self.slider_equipement.setValue(int(self.doubleSpinBox_equipement.value()))

    @pyqtSlot()
    def onvaluechanged_slider(self):
        """ Affiche et envoie vers backend la dernière commande d'un actionneur discret"""
        if not self.updated_from_outside:
            self.backend.sendeqpcmd(self.rid, self.name, self.doubleSpinBox_equipement.value())
            self.label_command.setText(str(self.slider_equipement.value()))
            self.doubleSpinBox_equipement.setValue(self.slider_equipement.value())

    @pyqtSlot()
    def oncheckbox_toggled(self):
        """ Affiche et renvoie vers backend la dernière commande d'un actionneur binaire"""
        if not self.updated_from_outside:
            if self.checkBox_equipement.isChecked():
                self.backend.sendeqpcmd(self.rid, self.name, 1)
                self.label_command.setText(str(1))
            else:
                self.backend.sendeqpcmd(self.rid, self.name, 0)
                self.label_command.setText(str(0))

    @pyqtSlot()
    def update_equipement(self, current_state: list):
        """ Met à jour l'équipement suivant son type"""

        if current_state[0] == self.rid and current_state[1] == self.name:

            self.value = float(current_state[2])
            self.last_update = float(current_state[3])
            self.label_message_equipement.setText("Dernière MAJ (s)")

            if self.type_widget == "BINAIRE":
                self.updated_from_outside = True
                if self.value == 0:
                    self.checkBox_equipement.setChecked(False)
                if self.value == 1:
                    self.checkBox_equipement.setChecked(True)
                self.updated_from_outside = False

            if self.type_widget == "DISCRET" and self.value is not None:
                self.updated_from_outside = True
                self.doubleSpinBox_equipement.setValue(self.value)
                self.slider_equipement.setValue(self.value)
                self.updated_from_outside = False

            if self.type_widget == "MULTIPLE":
                pass

            if self.type_widget == "COMPLEXE":
                pass

            if self.type_widget == "LED":
                self.pushButton_led.setStyleSheet("background: {}".format(self.value))

            if self.type_widget == "VALEUR":
                self.updated_from_outside = True
                if self.value is not None:
                    # Emission de signal de màj de la valeur de l'équipement
                    self.lcdNumber_equipement.display(self.value)
                self.updated_from_outside = False

            if self.type_widget == "BAR" and self.value is not None:

                self.updated_from_outside = True
                self.progressBar_equipement.setValue(int(self.value))
                self.updated_from_outside = False

            self.update_ping(self.last_update)
