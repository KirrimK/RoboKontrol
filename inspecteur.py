"""Ajoute une boite robot dans le layout parent situé dans le layout widget"""

from PyQt5 import QtWidgets, QtCore
import json

ACTIONNEURS_CAPTEURS_FILES = "actionneurs_capteurs.json"


class BoiteRobot:
    def __init__(self, parent_widget, parent_layout, robot_number):
        """Crée la boite robot dans le parent_layout situé dans un parent_widget et lui associe le numéro robot_number"""
        self.parent_widget = parent_widget
        self.parent_layout = parent_layout
        self.robot_number = robot_number

        self.groupBox_robot = QtWidgets.QGroupBox(self.parent_widget)
        self.groupBox_robot.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.groupBox_robot.setAutoFillBackground(True)
        self.groupBox_robot.setTitle("")
        self.groupBox_robot.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.groupBox_robot.setFlat(False)
        self.groupBox_robot.setCheckable(False)
        self.groupBox_robot.setChecked(False)

        self.layout_box_robot = QtWidgets.QVBoxLayout(self.groupBox_robot)





        self.parent_layout.addWidget(self.groupBox_robot, 0, QtCore.Qt.AlignTop)

        self.boites = {}

    def create_position(self):
        """Crée l'entête de la boite robot où l'on retrouve son nom, le bouton supprimer et ses coordonnées)"""

        self.layout_name_delete = QtWidgets.QHBoxLayout()
        self.layout_name_delete.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)

        self.label_name = QtWidgets.QLabel(self.groupBox_robot)

        self.label_name.setMinimumSize(QtCore.QSize(0, 30))
        self.label_name.setMaximumSize(QtCore.QSize(100, 30))
        self.label_name.setText("Nom du robot 1")
        self.layout_name_delete.addWidget(self.label_name)

        self.button_delete = QtWidgets.QPushButton(self.groupBox_robot)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_delete.sizePolicy().hasHeightForWidth())
        self.button_delete.setSizePolicy(sizePolicy)
        self.button_delete.setMaximumSize(QtCore.QSize(150, 30))
        self.button_delete.setText("Supprimer")
        self.layout_name_delete.addWidget(self.button_delete)

        self.layout_box_robot.addLayout(self.layout_name_delete)

        self.create_coordonnees("X", "mm")
        self.create_coordonnees("Y", "mm")
        self.create_coordonnees("Orientation", "degré")

    def create_coordonnees(self, coord: str, unite: str):
        """Crée une ligne coordonnée"""
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.label = QtWidgets.QLabel(self.groupBox_robot)
        self.label.setMaximumSize(QtCore.QSize(100, 30))
        self.label.setText('{0} ({1}):'.format(coord, unite))
        self.label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.layout.addWidget(self.label)
        self.lcdNumber = QtWidgets.QLCDNumber(self.groupBox_robot)
        self.lcdNumber.setMaximumSize(QtCore.QSize(50, 25))
        self.layout.addWidget(self.lcdNumber)
        self.layout_box_robot.addLayout(self.layout)

    def create_grid_actionneurs(self):
        self.groupBox_actuator = QtWidgets.QGroupBox(self.groupBox_robot)
        self.groupBox_actuator.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_actuator.setTitle("Actionneurs")

        self.layout_box_actuators = QtWidgets.QVBoxLayout(self.groupBox_actuator)

    def create_grid_capteurs(self):
        self.groupBox_sensors = QtWidgets.QGroupBox(self.groupBox_robot)
        self.groupBox_sensors.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_sensors.setTitle("Capteurs:")

        self.layout_box_capteurs = QtWidgets.QVBoxLayout(self.groupBox_sensors)



    def add_actuators(self, actionneurs):
        "Initialise l'ajout des actionneurs à la boite robot sous forme d'un QGridLayout dans une QGroupBox"

        data = actionneurs.copy()
        n = 0
        for dic in data:

            actuator_name = dic['nom']
            actuator_type = dic['type']
            actuator_value = dic['valeur']
            actuator_min = dic['min_value']
            actuator_max = dic['max_value']
            actuator_info = dic["info"].strip('][').split(', ')
            # list_robot = dic['robot'].strip('][').split(', ')

            if n != 0:
                spacerItem_actuators = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                             QtWidgets.QSizePolicy.Fixed)
                self.layout_box_actuators.addItem(spacerItem_actuators)
            n+=1

            self.gridLayout_actuator = QtWidgets.QGridLayout()

            self.label_name_actuator = QtWidgets.QLabel(self.groupBox_actuator)
            self.label_name_actuator.setText(actuator_name)
            self.gridLayout_actuator.addWidget(self.label_name_actuator, 0, 0, 1, 1)

            self.label_command_actuator = QtWidgets.QLabel(self.groupBox_actuator)
            self.label_command_actuator.setText("Dernière commande")
            self.gridLayout_actuator.addWidget(self.label_command_actuator, 1, 0, 1, 1)
            self.textBrowser_actuator = QtWidgets.QTextBrowser(self.groupBox_actuator)
            self.textBrowser_actuator.setMaximumSize(QtCore.QSize(16777215, 25))
            self.gridLayout_actuator.addWidget(self.textBrowser_actuator, 1, 1, 1, 1)
            self.layout_box_actuators.addLayout(self.gridLayout_actuator)
            self.layout_box_robot.addWidget(self.groupBox_actuator, 0, QtCore.Qt.AlignTop)

            if actuator_type == "BINAIRE":
                self.add_actuator_binaire()

            if actuator_type == "DISCRET":
                self.add_actuator_discret(actuator_value, actuator_min, actuator_max)

            if actuator_type == "MULTIPLE":
                self.add_actuator_multiple(actuator_info, actuator_value)

            if actuator_type == "COMPLEXE":
                self.add_actuator_complexe(actuator_info)

    def add_actuator_binaire(self):
        "Ajoute les actionneurs types binaires"

        self.checkBox_actuator = QtWidgets.QCheckBox(self.groupBox_actuator)
        self.checkBox_actuator.setText("")
        self.gridLayout_actuator.addWidget(self.checkBox_actuator, 0, 1, 1, 1,
                                           QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

    def add_actuator_discret(self, value: int, min_value, max_value):
        "Ajoute les actionneurs types discrets"

        self.doubleSpinBox_actuator = QtWidgets.QDoubleSpinBox(self.groupBox_actuator)
        self.doubleSpinBox_actuator.setMinimumSize(QtCore.QSize(0, 30))
        self.doubleSpinBox_actuator.setMaximum(max_value)
        self.doubleSpinBox_actuator.setMinimum(min_value)
        self.doubleSpinBox_actuator.setValue(value)
        self.gridLayout_actuator.addWidget(self.doubleSpinBox_actuator, 0, 1, 1, 1)

    def add_actuator_multiple(self, list_options, value):
        "Ajoute les actionneurs types multiples"

        self.comboBox_actuator = QtWidgets.QComboBox(self.groupBox_actuator)

        self.comboBox_actuator.addItem(list_options[value].strip('"'))
        for i in range(len(list_options)):
            if i != value:
                self.comboBox_actuator.addItem(list_options[i].strip('"'))

        self.gridLayout_actuator.addWidget(self.comboBox_actuator, 0, 1, 1, 1)

    def add_actuator_complexe(self, info):
        """Ajoute les actionneurs types complexes : il s'agit d'un bouton qui peut ouvrir un menu plus détaillée de l'actionneur"""

        self.pushButton_actuator = QtWidgets.QPushButton(self.groupBox_actuator)
        self.pushButton_actuator.setText(info[0])
        self.gridLayout_actuator.addWidget(self.pushButton_actuator, 0, 1, 1, 1)


    def add_capteurs(self,capteurs):

        data = capteurs.copy()
        n=0
        for dic in data:

            nom = dic['nom']
            valeur = dic['valeur']
            unite = dic['unite']
            if n!=0:
                spacerItem_actuators = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                             QtWidgets.QSizePolicy.Fixed)
                self.layout_box_capteurs.addItem(spacerItem_actuators)
            n+=1

            self.gridLayout_capteur = QtWidgets.QGridLayout()

            self.label_nom_capteur = QtWidgets.QLabel(self.groupBox_sensors)
            self.label_nom_capteur.setMinimumSize(QtCore.QSize(0, 30))
            self.label_nom_capteur.setMaximumSize(QtCore.QSize(100, 30))
            self.label_nom_capteur.setText('{0} ({1}):'.format(nom, unite))
            self.gridLayout_capteur.addWidget(self.label_nom_capteur, 0, 0, 1, 1)

            self.label_message_capteur = QtWidgets.QLabel(self.groupBox_sensors)
            self.label_message_capteur.setText("Dernier message (ms)")
            self.gridLayout_capteur.addWidget(self.label_message_capteur, 1, 0, 1, 1)

            self.lcdNumber_message_capteur = QtWidgets.QLCDNumber(self.groupBox_sensors)
            self.lcdNumber_message_capteur.setMaximumSize(QtCore.QSize(50, 25))
            self.gridLayout_capteur.addWidget(self.lcdNumber_message_capteur,1,1,1,1)

            if nom == "Batterie":

                self.progressBar = QtWidgets.QProgressBar(self.groupBox_sensors)
                self.progressBar.setProperty(str(valeur), 24)
                self.gridLayout_capteur.addWidget(self.progressBar, 0, 1, 1, 1)

            else:
                self.lcdNumber_capteur = QtWidgets.QLCDNumber(self.groupBox_sensors)
                self.lcdNumber_capteur.setMinimumSize(QtCore.QSize(160, 25))
                self.gridLayout_capteur.addWidget(self.lcdNumber_capteur, 0, 1, 1, 1)
            self.layout_box_capteurs.addLayout(self.gridLayout_capteur)

    def add_box_robot(self):
        """Permet l'ajout d'une boite robot"""

        self.create_position()

        self.create_grid_actionneurs()

        self.add_actuators(actionneurs)

        self.create_grid_capteurs()

        self.add_capteurs(capteurs)

        self.layout_box_robot.addWidget(self.groupBox_sensors, 0, QtCore.Qt.AlignTop)

        n = self.robot_number
        self.boites[n] = [self.groupBox_robot, self.button_delete]
        self.boites[n][1].clicked.connect(lambda: self.remove_box_robot(n))

    def remove_box_robot(self, number_delete):
        """Permet la suppression de la boite robot dont le numéro est placé en paramètre"""
        self.boites[number_delete][0].hide()




def load_fichier(fichier):
    """Retourne les actionneurs placés dans un fichier .json de la forme:
            - type : binaire, discret, multiple ou plus complexe
            - nom
            -  valeur : valeur initiale
            - min_value : valeur minimale prise par l'actionneur
            - max_value : valeur maximale prse par l'actionneur
            - info : information supplémentaire sur lactionneur comme la liste des états possible ou le nom d'un fichier à lancer"
            - robot : liste des robots concernées par l'actionneur
        sous la forme d'une liste de dictionnaires"""

    actionneurs, capteurs = [], []
    with open(fichier) as f:
        data = json.load(f)
    for dic in data["Actionneur"]:
        actionneurs.append(dic)
    for dic in data["Capteur"]:
        capteurs.append(dic)
    return actionneurs, capteurs


actionneurs, capteurs = load_fichier(ACTIONNEURS_CAPTEURS_FILES)
