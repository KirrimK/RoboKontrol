"""Ajoute une boite robot dans le layout parent situé dans le layout widget"""

from PyQt5 import QtWidgets, QtCore
import json
import annuaire
from backend import Backend
import inspecteur

ACTIONNEURS_CAPTEURS_FILES = "actionneurs_capteurs.json"
MIN_BATTERIE = 9
MAX_BATTERIE = 12


class BoiteRobot(annuaire.Robot):
    """Définit un objet boite robot qui hérite des infomations du robot auquel il est associé et instancie l'affichage dans l'inspecteur sous forme QGroupBox"""

    def __init__(self, parent_widget, parent_layout, rid, inspector):
        """Crée la boite robot dans le parent_layout situé dans un parent_widget et lui associe le numéro robot_number"""
        super().__init__(rid)
        self.position = (self.x, self.y, self.theta)
        self.inspecteur = inspector
        self.parent_widget = parent_widget
        self.parent_layout = parent_layout
        self.nom_robot = rid

        self.groupBox_robot = QtWidgets.QGroupBox(self.parent_widget)
        self.layout_box_robot = QtWidgets.QVBoxLayout(self.groupBox_robot)
        self.parent_layout.addWidget(self.groupBox_robot, 0, QtCore.Qt.AlignTop)

        #self.equipement = self.inspecteur.backend.getdata_robot(self.nom_robot)[1]
        # Création d'un dictionnaire (clé = nom du robot; valeur = (boite robot, bouton supprimer)
        self.actionneurs = {}
        self.capteur = {}

        # Connexion du signal de nouveau message de blackend avec la mise à jour de la boite robot
        #self.inspecteur.backend.new_message_signal.connect(self.update_boite_robot)
        #self.inspecteur.robot_list_updated_signal.connect()


    def create_position(self):
        """Crée l'entête de la boite robot où l'on retrouve son nom, le bouton supprimer et ses coordonnées)"""

        self.layout_name_delete = QtWidgets.QHBoxLayout()
        self.layout_name_delete.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)

        self.label_name = QtWidgets.QLabel(self.groupBox_robot)
        self.label_name.setMinimumSize(QtCore.QSize(0, 30))
        self.label_name.setMaximumSize(QtCore.QSize(100, 30))
        self.label_name.setText(self.nom_robot)
        self.layout_name_delete.addWidget(self.label_name)

        self.button_delete = QtWidgets.QPushButton(self.groupBox_robot)
        self.button_delete.setMaximumSize(QtCore.QSize(150, 30))
        self.button_delete.setText("Supprimer")
        self.button_delete.clicked.connect(lambda: self.remove_box_robot())
        self.layout_name_delete.addWidget(self.button_delete)

        self.layout_box_robot.addLayout(self.layout_name_delete)

        # Création de l'affichage des coordonnées"
        self.lcdNumber_x = self.create_coord("X", "mm")
        self.lcdNumber_y = self.create_coord("Y", "mm")
        self.lcdNumber_theta = self.create_coord("Orientation", "degré")
        self.lcdNumber_last_updt_pos = self.create_coord("Dernier message", "ms")

    def create_coord(self, coord: str, unite: str):
        """Crée une ligne coordonnée (QLabel et QLCDNumber dans un QLayout) et renvoie le QLCDNumber"""
        self.layout_coord = QtWidgets.QHBoxLayout()
        self.layout_coord.setContentsMargins(0, 0, 0, 0)
        self.label_coord = QtWidgets.QLabel(self.groupBox_robot)
        self.label_coord.setMaximumSize(QtCore.QSize(150, 30))
        self.label_coord.setText('{0} ({1}):'.format(coord, unite))
        self.layout_coord.addWidget(self.label_coord)
        self.lcdNumber_coord = QtWidgets.QLCDNumber(self.groupBox_robot)
        self.lcdNumber_coord.setMaximumSize(QtCore.QSize(75, 30))
        self.layout_coord.addWidget(self.lcdNumber_coord)
        self.layout_box_robot.addLayout(self.layout_coord)
        return self.lcdNumber_coord

    def create_boite_actionneurs(self):
        self.groupBox_actuator = QtWidgets.QGroupBox(self.groupBox_robot)
        # self.groupBox_actuator.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_actuator.setTitle("Actionneurs")
        self.layout_box_actuators = QtWidgets.QVBoxLayout(self.groupBox_actuator)
        self.layout_box_robot.addWidget(self.groupBox_actuator, 0, QtCore.Qt.AlignTop)

    def create_boite_capteurs(self):
        self.groupBox_sensors = QtWidgets.QGroupBox(self.groupBox_robot)
        # self.groupBox_sensors.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_sensors.setTitle("Capteurs:")
        self.layout_box_capteurs = QtWidgets.QVBoxLayout(self.groupBox_sensors)
        self.layout_box_robot.addWidget(self.groupBox_sensors, 0, QtCore.Qt.AlignTop)

    @QtCore.pyqtSlot()
    def create_boite_robot(self):
        """Permet l'ajout d'une boite robot"""

        self.create_position()
        self.create_boite_actionneurs()
        self.create_boite_capteurs()

        self.add_actuators(actionneurs)
        self.add_capteurs(capteurs)

        self.layout_box_robot.addWidget(self.groupBox_sensors, 0, QtCore.Qt.AlignTop)

    @QtCore.pyqtSlot()
    def remove_box_robot(self):
        """Permet la suppression de la boite robot dont le numéro est placé en paramètre"""
        self.groupBox_robot.hide()


    def add_actuators(self, actionneurs: list):
        for i in range(len(actionneurs)):
            act = actionneurs[i]
            actionneur = Actionneur(act.nom, act.min_val, act.max_val,act.unite,  self.groupBox_actuator, self.layout_box_actuators)
            actionneur.add_actuator()

    def add_capteurs(self, capteurs: list):
        for i in range(len(capteurs)):
            capt = capteurs[i]
            capteur = Capteur(capt.nom, capt.valeur, capt.unite, self.groupBox_sensors, self.layout_box_capteurs)
            capteur.add_capteur()


    @QtCore.pyqtSlot()
    def update_position(self):
        """Met à jour la position de la boite robot"""

        self.position = self.inspecteur.backend.getdata_robot(self.nom_robot)[1]
        self.last_updt_pos = self.inspecteur.backend.getdata_robot(self.nom_robot)[2]

        self.lcdNumber_x.display(self.position[0])
        self.lcdNumber_y.display(self.position[1])
        self.lcdNumber_theta.display(self.position[2])
        self.lcdNumber_last_updt_pos.display(self.last_updt_pos)

    def update_actionneurs(self):                                                               #TODO: besoin de get_actionneur dans backend
        """Met à jour les actionneurs de la boite robot"""
        #doit également émettre un signal lorsque l'actionneur a changé de valeur
        pass

    def update_capteurs(self):                                                                  #TODO: besoin de get_capteur dans backend
        """Met à jour les capteurs de la boite robot"""
        pass

    @QtCore.pyqtSlot()
    def update_boite_robot(self):
        """Initialise la mise à jours de la position, des actionneurs, et des capteurs du robot"""
        self.update_position()
        self.update_actionneurs()
        self.update_capteurs()


class Actionneur(annuaire.Actionneur):
    """Définit l'affichage d'un actionneur (QGridLayout) situé dans la boite actionneur"""
    def __init__(self, nom, min_val, max_val, unite,boite_actionneurs, layout_boite_actionneurs):
        super().__init__(nom, min_val, max_val)
        self.groupBox_actuator = boite_actionneurs
        self.layout_box_actuators = layout_boite_actionneurs

        self.unite = unite
        self.value = 0
        self.actuator_type = "COMPLEXE"                                       #TODO : ajouter attribut type dans annuaire
        self.actuator_info = ["état1", "état2", "état3", "état4", "état5"]    #TODO : ajouter les états possibles des actionnaires types MULTIPLE
        self.last_commande = ""                                               #TODO : ajouter un attribut coorespondant à la dernière commande envoyée/reçue à l'actionneur

        self.gridLayout_actuator = QtWidgets.QGridLayout()
        self.label_name_actuator = QtWidgets.QLabel(self.groupBox_actuator)
        self.label_command_actuator = QtWidgets.QLabel(self.groupBox_actuator)
        self.textBrowser_actuator = QtWidgets.QTextBrowser(self.groupBox_actuator)

    def add_actuator(self):
        """Ajoute un actionneur (QGridLayout) dans la boite actionneurs (QGroupBox)"""


        #actuator_type = dic['type']
        #actuator_info = dic["info"].strip('][').split(', ')
        #list_robot = dic['robot'].strip('][').split(', ')

        spacerItem_actuators = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                     QtWidgets.QSizePolicy.Fixed)
        self.layout_box_actuators.addItem(spacerItem_actuators)

        if self.unite is None:
            self.label_name_actuator.setText(self.nom)
        else:
            self.label_name_actuator.setText("{0} ({1})".format(self.nom, self.unite))

        self.gridLayout_actuator.addWidget(self.label_name_actuator, 0, 0, 1, 1)

        self.label_command_actuator.setText("Dernière commande")
        self.label_command_actuator.setMinimumSize(120,30)
        self.gridLayout_actuator.addWidget(self.label_command_actuator, 1, 0, 1, 1)
        self.textBrowser_actuator.setMaximumSize(QtCore.QSize(16777215, 25))
        self.gridLayout_actuator.addWidget(self.textBrowser_actuator, 1, 1, 1, 1)
        self.layout_box_actuators.addLayout(self.gridLayout_actuator)

        if self.actuator_type == "BINAIRE":
            self.add_actuator_binaire()

        if self.actuator_type == "DISCRET":
            self.add_actuator_discret()

        if self.actuator_type == "MULTIPLE":
            self.add_actuator_multiple()

        if self.actuator_type == "COMPLEXE":
            self.add_actuator_complexe()

    def remove_actionneur(self):
        """Supprime l'affiche de l'actionneur (QGroupBox)"""
        self.groupBox_actuator.hide()

    def add_actuator_binaire(self):
        "Crée et ajoute les actionneurs types binaires"

        self.checkBox_actuator = QtWidgets.QCheckBox(self.groupBox_actuator)
        self.checkBox_actuator.setText("")
        self.gridLayout_actuator.addWidget(self.checkBox_actuator, 0, 1, 1, 1,
                                           QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

    def add_actuator_discret(self):
        "Crée et ajoute les actionneurs types discrets"

        self.doubleSpinBox_actuator = QtWidgets.QDoubleSpinBox(self.groupBox_actuator)
        self.doubleSpinBox_actuator.setMinimumSize(QtCore.QSize(0, 30))
        self.doubleSpinBox_actuator.setMaximum(self.max_val)
        self.doubleSpinBox_actuator.setMinimum(self.min_val)
        self.doubleSpinBox_actuator.setValue(self.value)
        self.gridLayout_actuator.addWidget(self.doubleSpinBox_actuator, 0, 1, 1, 1)

    def add_actuator_multiple(self):
        "Crée et ajoute les actionneurs types multiples"
        list_options = self.actuator_info
        self.comboBox_actuator = QtWidgets.QComboBox(self.groupBox_actuator)

        self.comboBox_actuator.addItem(list_options[self.value].strip('"'))
        for i in range(len(list_options)):
            if i != self.value:
                self.comboBox_actuator.addItem(list_options[i].strip('"'))

        self.gridLayout_actuator.addWidget(self.comboBox_actuator, 0, 1, 1, 1)

    def add_actuator_complexe(self):
        """Crée et ajoute les actionneurs types complexes : il s'agit d'un bouton qui peut ouvrir un menu plus détaillée de l'actionneur (QDialog par exemple)"""
        self.pushButton_actuator = QtWidgets.QPushButton(self.groupBox_actuator)
        if self.nom == "LED":
            self.pushButton_actuator.setText("Choisir la couleur")
            self.pushButton_actuator.clicked.connect(lambda: self.open_LED_menu())
        else:
            self.pushButton_actuator.setText(self.actuator_info[0])
            self.pushButton_actuator.clicked.connect(lambda: self.open_actionneur_complexe())
        self.gridLayout_actuator.addWidget(self.pushButton_actuator, 0, 1, 1, 1)

    @QtCore.pyqtSlot()
    def open_LED_menu(self):
        """Ouvre une fenêtre de sélection de couleur (QColorDialog) et modifie la valeur de l'actionneur la couleur choisie"""
        self.valeur = QtWidgets.QColorDialog.getColor().name()
        self.pushButton_actuator.setStyleSheet("background-color : {0};".format(self.valeur))

    @QtCore.pyqtSlot()
    def open_actionneur_complexe(self):                                        # TODO: idée d'autres actionneurs complexes?
        """Ouvre un QDilaog à définir qui change la valeur de l'actionneur"""
        self.valeur = QtWidgets.QDialog()



class Capteur(annuaire.Actionneur):
    """Définit l'affichage d'un capteur (QGridLayout) situé dans la boite capteur"""
    def __init__(self, nom, valeur, unite, boite_capteurs, layout_boite_capteurs):
        super().__init__(nom, valeur, unite)
        self.valeur = valeur
        self.unite = unite
        self.layout_box_capteurs = layout_boite_capteurs
        self.groupBox_sensors = boite_capteurs


        self.gridLayout_capteur = QtWidgets.QGridLayout()

        self.label_nom_capteur = QtWidgets.QLabel(self.groupBox_sensors)
        self.label_nom_capteur.setMinimumSize(QtCore.QSize(0, 30))
        self.label_nom_capteur.setMaximumSize(QtCore.QSize(100, 30))
        self.label_nom_capteur.setText('{0} ({1}):'.format(self.nom, self.unite))
        self.gridLayout_capteur.addWidget(self.label_nom_capteur, 0, 0, 1, 1)

        self.label_message_capteur = QtWidgets.QLabel(self.groupBox_sensors)
        self.label_message_capteur.setText("Dernier message (ms)")
        self.gridLayout_capteur.addWidget(self.label_message_capteur, 1, 0, 1, 1)

        self.lcdNumber_message_capteur = QtWidgets.QLCDNumber(self.groupBox_sensors)
        self.lcdNumber_message_capteur.setMaximumSize(QtCore.QSize(50, 25))
        self.gridLayout_capteur.addWidget(self.lcdNumber_message_capteur, 1, 1, 1, 1)

    def add_capteur(self):
        """Ajoute un capteur (QGridLayout) dans la boite capteur (QGroupBox)"""

        spacerItem_actuators = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                     QtWidgets.QSizePolicy.Fixed)
        self.layout_box_capteurs.addItem(spacerItem_actuators)

        if self.nom == "Batterie":
            n = 100   #permet d'afficher les décimales de la tension
            self.progressBar = QtWidgets.QProgressBar(self.groupBox_sensors)
            self.progressBar.setRange(MIN_BATTERIE*n, MAX_BATTERIE*n)
            self.progressBar.setValue(self.valeur*n)
            self.progressBar.setFormat(str(self.valeur))
            self.progressBar.setStyleSheet("QProgressBar"
                          "{"
                          "background-color : grey;"
                          "border : 1px"
                          "}")
            self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
            self.gridLayout_capteur.addWidget(self.progressBar, 0, 1, 1, 1)

        else:
            self.lcdNumber_capteur = QtWidgets.QLCDNumber(self.groupBox_sensors)
            self.lcdNumber_capteur.setMinimumSize(QtCore.QSize(160, 25))
            self.gridLayout_capteur.addWidget(self.lcdNumber_capteur, 0, 1, 1, 1)

        self.layout_box_capteurs.addLayout(self.gridLayout_capteur)

    def remove_capteur(self):
        """Supprime l'affiche de lu capteur (QGroupBox)"""
        self.groupBox_sensors.hide()



def load_actionneurs(fichier):
    """Retourne les actionneurs placés dans un fichier .json de la forme:
            - type : binaire, discret, multiple ou plus complexe
            - nom
            -  valeur : valeur initiale
            - min_value : valeur minimale prise par l'actionneur
            - max_value : valeur maximale prse par l'actionneur
            - info : information supplémentaire sur lactionneur comme la liste des états possible ou le nom d'un fichier à lancer"
            - robot : liste des robots concernées par l'actionneur
        sous la forme d'une liste de dictionnaires"""

    actionneurs = []
    with open(fichier, encoding='utf-8') as f:
        data = json.load(f)
        data = data["Actionneurs"].copy()
        #print(data)
        for dic in data:
            actionneur = annuaire.Actionneur(dic['nom'], dic['min_value'], dic['max_value'], unite=dic['unite'])
            actionneurs.append(actionneur)
    return actionneurs

def load_capteurs(fichier):
    """Retourne les actionneurs placés dans un fichier .json de la forme:
            - type : binaire, discret, multiple ou plus complexe
            - nom
            -  valeur : valeur initiale
            - min_value : valeur minimale prise par l'actionneur
            - max_value : valeur maximale prse par l'actionneur
            - info : information supplémentaire sur lactionneur comme la liste des états possible ou le nom d'un fichier à lancer"
            - robot : liste des robots concernées par l'actionneur
        sous la forme d'une liste de dictionnaires"""

    capteurs = []
    with open(fichier, encoding='utf-8') as f:
        data = json.load(f)
        data = data["Capteurs"].copy()
        for d in data:
            capteur = annuaire.Capteur(d['nom'], d['valeur'], d['unite'])
            capteurs.append(capteur)
    return capteurs


actionneurs = load_actionneurs(ACTIONNEURS_CAPTEURS_FILES)
capteurs = load_capteurs(ACTIONNEURS_CAPTEURS_FILES)

