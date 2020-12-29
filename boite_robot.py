"""Ajoute une boite robot dans le layout parent situé dans le layout widget"""

from PyQt5 import QtWidgets, QtCore, QtGui
import json
import annuaire

# fichier .json des actionneurs et des capteurs
ACTIONNEURS_CAPTEURS_FILES = "actionneurs_capteurs.json"
# Définition des mins et maxs de tension pour la batterie (en V)
MIN_BATTERIE = 9
MAX_BATTERIE = 12
# Customisation
QPROGRESSBAR = "QProgressBar{background-color : grey;border : 1px; border: 2px solid grey; border-radius: 5px}"
QLCD_STYLE = "QLCDNumber{background-color: grey;border: 2px solid rgb(113, 113, 113);border-width: 2px; " \
             "border-radius: 10px;  color: rgb(255, 255, 255)} "
QPUSHBUTTON = "QPushButton{background-color: grey; border 2px solid rgb(113, 113, 113);border-width: 2px; " \
              "border-radius: 10px;  color: rgb(0,0,0)} "

# Alignement
QT_CENTER = QtCore.Qt.AlignCenter
QT_TOP = QtCore.Qt.AlignTop


# noinspection PyArgumentList
class BoiteRobot(annuaire.Robot):
    """Définit un objet boite robot qui hérite des infomations du robot auquel il est associé et instancie
    l'affichage dans l'inspecteur sous forme QGroupBox """

    def __init__(self, parent_widget, parent_layout, rid, inspector):
        """Crée la boite robot dans le parent_layout situé dans un parent_widget et lui associe le numéro
        robot_number """

        super().__init__(rid)

        self.inspecteur = inspector
        self.parent_widget = parent_widget
        self.parent_layout = parent_layout
        self.nom_robot = rid
        self.position = (self.x, self.y, self.theta)

        self.groupBox_robot = QtWidgets.QGroupBox(self.parent_widget)
        self.layout_box_robot = QtWidgets.QVBoxLayout(self.groupBox_robot)
        self.parent_layout.addWidget(self.groupBox_robot, 0, QT_TOP)

        # Récupère la liste des noms d'équipements attachés aux robots
        self.equipement_list = []
        self.actionneurs = {}
        self.capteurs = {}

        self.current_actionneurs_list = []
        self.current_actionneurs_dic = {}
        self.current_capteurs_list = []
        self.current_capteurs_dic = {}

    def create_position(self):
        """Crée l'entête de la boite robot où l'on retrouve son nom, le bouton supprimer et ses coordonnées)"""

        self.layout_name_delete = QtWidgets.QHBoxLayout()
        # self.layout_name_delete.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)

        self.label_name = QtWidgets.QLabel(self.groupBox_robot)
        self.label_name.setMinimumSize(0, 30)
        self.label_name.setMaximumSize(100, 30)
        self.label_name.setText(self.nom_robot)
        self.layout_name_delete.addWidget(self.label_name)

        self.button_delete = QtWidgets.QPushButton(self.groupBox_robot)
        self.button_delete.setMaximumSize(150, 30)
        self.button_delete.setStyleSheet(QPUSHBUTTON)
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
        self.label_coord.setMaximumSize(150, 30)
        self.label_coord.setText('{0} ({1}):'.format(coord, unite))
        self.layout_coord.addWidget(self.label_coord)
        self.lcdNumber_coord = QtWidgets.QLCDNumber(self.groupBox_robot)
        self.lcdNumber_coord.setMaximumSize(75, 30)
        self.lcdNumber_coord.setStyleSheet(QLCD_STYLE)
        self.layout_coord.addWidget(self.lcdNumber_coord)
        self.layout_box_robot.addLayout(self.layout_coord)
        return self.lcdNumber_coord

    def create_boite_actionneurs(self):
        """ Crée la boite actionneurs (QGroupBox) et l'ajoute dans la boite robot"""

        self.groupBox_actuator = QtWidgets.QGroupBox(self.groupBox_robot)
        self.groupBox_actuator.setAlignment(QT_CENTER)
        self.groupBox_actuator.setTitle("Actionneurs")
        self.layout_box_actuators = QtWidgets.QVBoxLayout(self.groupBox_actuator)
        self.layout_box_robot.addWidget(self.groupBox_actuator, 0, QT_TOP)

    def create_boite_capteurs(self):
        """ Crée la boite capteurs (QGroupBox) et l'ajoute dans la boite robot"""

        self.groupBox_sensors = QtWidgets.QGroupBox(self.groupBox_robot)
        self.groupBox_sensors.setAlignment(QT_CENTER)
        self.groupBox_sensors.setTitle("Capteurs:")
        self.layout_box_capteurs = QtWidgets.QVBoxLayout(self.groupBox_sensors)
        self.layout_box_robot.addWidget(self.groupBox_sensors, 0, QT_TOP)

    @QtCore.pyqtSlot()
    def create_boite_robot(self):
        """ Crée une nouvelle boite robot et l'ajoute dans la zone inspecteur"""

        self.create_position()
        self.create_boite_actionneurs()
        self.create_boite_capteurs()

        self.add_actuators(actionneurs)
        self.add_capteurs(capteurs)

    @QtCore.pyqtSlot()
    def remove_box_robot(self):
        """Permet la suppression de la boite robot dont le numéro est placé en paramètre"""

        self.groupBox_robot.hide()
        self.inspecteur.backend.stopandforget_robot(self.nom_robot)

    def add_actuators(self, actionneurs: list):
        """ Ajoute les actionneurs placés dans une liste tirée du fichier .sjon ---> permet d'initialiser des
        actionneurs """

        for i in range(len(actionneurs)):
            act = actionneurs[i]
            actionneur = Actionneur(act.nom, act.min_val, act.max_val, act.unite, self.groupBox_actuator,
                                    self.layout_box_actuators)
            actionneur.add_actuator()

    def add_capteurs(self, capteurs: list):
        """ Ajoute les capteurs placés dans une liste tirée du fichier .sjon ---> permet d'initialiser des
        capteurss """

        for i in range(len(capteurs)):
            capt = capteurs[i]
            capteur = Capteur(capt.nom, capt.valeur, capt.unite, self.groupBox_sensors, self.layout_box_capteurs)
            capteur.add_capteur()

    def update_position(self):
        """Met à jour la position de la boite robot"""

        # Mise à jour du vecteur position du robot
        self.position = self.inspecteur.backend.getdata_robot(self.nom_robot)[0]
        # Récupération du timestamp de dernière mise à jour de la position
        self.last_updt_pos = self.inspecteur.backend.getdata_robot(self.nom_robot)[2]  # todo:pb de remise à 0?
        # print(self.last_updt_pos)

        # Mise à jour des valeurs affichés par les QLCDNUmber
        self.lcdNumber_x.display(self.position[0])
        self.lcdNumber_y.display(self.position[1])
        self.lcdNumber_theta.display(self.position[2])
        self.lcdNumber_last_updt_pos.display(self.last_updt_pos)

    def load_equipement(self):
        """ Met à jour la liste des des équipements du robot et charge les informations de chaque équipement présent
        en les séparant suivant qu'ils sont actionneurs ou capteurs """

        # Mise à jour de la liste de l'équipement du robot
        self.equipement_list = self.inspecteur.backend.getdata_robot(self.nom_robot)[1]

        for eqp_name in self.equipement_list:

            eqp_type = self.inspecteur.backend.getdata_eqp(self.nom_robot, eqp_name)[0]
            if eqp_type == annuaire.Actionneur or eqp_type == annuaire.Binaire:
                eqp_type.__str__(eqp_type)
                # self.actionneurs[eqp_name] =

            if eqp_type == annuaire.Capteur:
                pass

    def update_actionneurs(self):  # TODO: besoin de get_actionneur dans backend
        """ Met à jour les actionneurs de la boite robot """
        # doit également émettre un signal lorsque l'actionneur a changé de valeur
        pass

    def update_capteurs(self):  # TODO: besoin de get_capteur dans backend
        """ Met à jour les capteurs de la boite robot """

        new_capteurs = self.inspecteur.backend.get_all_robots()

        # Ajoute les nouveaux capteurs
        for capteur in set(new_capteurs) - set(self.current_capteurs_list):
            #capteur =
           #self.add_capteurs()
            pass

        # Supprime les capteurs qui ne sont plus présents
        for capteur in set(self.current_capteurs_list) - set(new_capteurs):
            self.remove_capteur(robot)

        # Met à jour la liste des capteurs présents
        self.current_robots_list = new_capteurs

        # Initialise la mise à jours des capteurs
        for k, v in self.current_capteurs_dic.items():
            v.update_capteur()
        pass

    @QtCore.pyqtSlot()
    def update_boite_robot(self):
        """ Initialise la mise à jour de la position, des actionneurs, et des capteurs du robot de la boite robot """

        self.update_position()
        self.load_equipement()
        self.update_actionneurs()
        self.update_capteurs()


class Actionneur(annuaire.Actionneur):
    """ Définit l'affichage d'un actionneur (QGridLayout) situé dans la boite actionneur """

    def __init__(self, nom, min_val, max_val, unite, boite_actionneurs, layout_boite_actionneurs):
        """ Crée l'affichage de l'actionneur (hérité de la classe Actionneur d'annuaire) et l'ajoute dans la
        boite actionneurs """
        super().__init__(nom, min_val, max_val)
        # Récupération des informations de la boite actionneurs
        self.groupBox_actuator = boite_actionneurs
        self.layout_box_actuators = layout_boite_actionneurs

        self.unite = unite
        self.value = 0
        self.type_actionneur = "BINAIRE"
        self.info_actionneur = ["état1", "état2", "état3", "état4", "état5"]
        # TODO : ajouter les actionneurs types multiples
        self.last_commande = ""

        self.gridLayout_actuator = QtWidgets.QGridLayout()
        self.label_name_actuator = QtWidgets.QLabel(self.groupBox_actuator)
        self.label_command_actuator = QtWidgets.QLabel(self.groupBox_actuator)
        self.textBrowser_actuator = QtWidgets.QTextBrowser(self.groupBox_actuator)

    def add_actuator(self):
        """Ajoute un actionneur (QGridLayout) dans la boite actionneurs (QGroupBox)"""

        spacerItem_actionneur = create_space()
        self.layout_box_actuators.addItem(spacerItem_actionneur)

        if self.unite is None:
            self.label_name_actuator.setText(self.nom)
        else:
            self.label_name_actuator.setText("{0} ({1})".format(self.nom, self.unite))

        self.gridLayout_actuator.addWidget(self.label_name_actuator, 0, 0, 1, 1)

        self.label_command_actuator.setText("Dernière commande")
        self.label_command_actuator.setMinimumSize(120, 30)
        self.gridLayout_actuator.addWidget(self.label_command_actuator, 1, 0, 1, 1)
        self.textBrowser_actuator.setMaximumSize(QtCore.QSize(16777215, 25))
        self.gridLayout_actuator.addWidget(self.textBrowser_actuator, 1, 1, 1, 1)
        self.layout_box_actuators.addLayout(self.gridLayout_actuator)

        if self.type_actionneur == "BINAIRE":
            self.create_actuator_binaire()

        if self.type_actionneur == "DISCRET":
            self.create_actuator_discret()

        if self.type_actionneur == "MULTIPLE":
            self.create_actuator_multiple()

        if self.type_actionneur == "COMPLEXE":
            self.create_actuator_complexe()

    def create_actuator_binaire(self):
        """Crée et ajoute un actionneur de type binaire (QCheckBox)"""

        self.checkBox_actuator = QtWidgets.QCheckBox(self.groupBox_actuator)
        self.checkBox_actuator.setText("")
        self.gridLayout_actuator.addWidget(self.checkBox_actuator, 0, 1, 1, 1, QT_CENTER)

    def create_actuator_discret(self):
        """Crée et ajoute un actionneur de type discret (QDoubleSpinBox)"""

        self.doubleSpinBox_actuator = QtWidgets.QDoubleSpinBox(self.groupBox_actuator)
        self.doubleSpinBox_actuator.setMinimumSize(0, 30)
        self.doubleSpinBox_actuator.setMaximum(self.max_val)
        self.doubleSpinBox_actuator.setMinimum(self.min_val)
        self.doubleSpinBox_actuator.setValue(self.value)
        self.gridLayout_actuator.addWidget(self.doubleSpinBox_actuator, 0, 1, 1, 1)

    def create_actuator_multiple(self):
        """""Crée et ajoute un actionneur de type multiple (QComboBox)"""
        list_options = self.info_actionneur
        self.comboBox_actuator = QtWidgets.QComboBox(self.groupBox_actuator)

        self.comboBox_actuator.addItem(list_options[self.value].strip('"'))
        for i in range(len(list_options)):
            if i != self.value:
                self.comboBox_actuator.addItem(list_options[i].strip('"'))

        self.gridLayout_actuator.addWidget(self.comboBox_actuator, 0, 1, 1, 1)

    def create_actuator_complexe(self):
        """Crée et ajoute un actionneur de type complexe (QPushButton) : il s'agit d'un bouton qui peut ouvrir un
        menu plus détaillée de l'actionneur (QDialog par exemple) """
        self.pushButton_actuator = QtWidgets.QPushButton(self.groupBox_actuator)
        if self.nom == "LED":
            # Création d'un actionneur complexe spéciale : la LED
            self.pushButton_actuator.setText("Choisir la couleur")
            self.pushButton_actuator.clicked.connect(lambda: self.open_LED_menu())
        else:
            self.pushButton_actuator.setText(self.info_actionneur[0])
            self.pushButton_actuator.clicked.connect(lambda: self.open_actionneur_complexe())
        self.gridLayout_actuator.addWidget(self.pushButton_actuator, 0, 1, 1, 1)

    @QtCore.pyqtSlot()
    def open_LED_menu(self):
        """Ouvre une fenêtre de sélection de couleur (QColorDialog) et modifie la valeur de l'actionneur la couleur
        choisie """

        self.valeur = QtWidgets.QColorDialog.getColor().name()
        self.pushButton_actuator.setStyleSheet("background-color : {0};".format(self.valeur))

    @QtCore.pyqtSlot()
    def open_actionneur_complexe(self):  # TODO: idée d'autres actionneurs complexes?
        """Ouvre un QDilaog à définir qui change la valeur de l'actionneur"""

        self.valeur = QtWidgets.QDialog()

    def remove_actionneur(self):
        """Supprime l'affiche de l'actionneur (QGroupBox)"""

        self.groupBox_actuator.hide()

    def update_capteur(self):
        pass


class Capteur(annuaire.Actionneur):
    """ Crée l'affichage d'un capteur (hérité de la classe Capteur d'annuaire) et l'ajoute dans la boite capteurs """

    def __init__(self, nom, valeur, unite, boite_capteurs, layout_boite_capteurs):
        """ Héritagede la classe Capteur de annuaire et création de l'affichage du capteur puis ajout dans boite
        capteurs """

        super().__init__(nom, valeur, unite)

        self.valeur = valeur
        self.unite = unite
        self.layout_box_capteurs = layout_boite_capteurs
        self.groupBox_sensors = boite_capteurs

        self.gridLayout_capteur = QtWidgets.QGridLayout()

        self.label_nom_capteur = QtWidgets.QLabel(self.groupBox_sensors)
        self.label_nom_capteur.setMinimumSize(0, 30)
        self.label_nom_capteur.setMaximumSize(100, 30)
        self.label_nom_capteur.setText('{0} ({1}):'.format(self.nom, self.unite))
        self.gridLayout_capteur.addWidget(self.label_nom_capteur, 0, 0, 1, 1)

        self.label_message_capteur = QtWidgets.QLabel(self.groupBox_sensors)
        self.label_message_capteur.setText("Dernier message (ms)")
        self.gridLayout_capteur.addWidget(self.label_message_capteur, 1, 0, 1, 1)

        self.lcdNumber_message_capteur = QtWidgets.QLCDNumber(self.groupBox_sensors)
        self.lcdNumber_message_capteur.setMaximumSize(QtCore.QSize(50, 25))
        self.gridLayout_capteur.addWidget(self.lcdNumber_message_capteur, 1, 1, 1, 1)

    def add_capteur(self):
        """ Ajoute un capteur (QGridLayout) dans la boite capteur (QGroupBox) """

        # Ajoute d'un espace sauf si c'est le premier actionneur placé dans la boite capteur
        if True:                                                        # TODO: modifierr cette condition
            spacerItem_actuators = create_space()
            self.layout_box_capteurs.addItem(spacerItem_actuators)

        if self.nom == "Batterie":
            n = 100                              # n permet d'afficher les décimales de la tension
            self.progressBar = QtWidgets.QProgressBar(self.groupBox_sensors)
            self.progressBar.setRange(MIN_BATTERIE * n, MAX_BATTERIE * n)
            self.progressBar.setValue(self.valeur * n)
            self.progressBar.setFormat(str(self.valeur))
            self.progressBar.setStyleSheet(QPROGRESSBAR)
            self.progressBar.setAlignment(QT_CENTER)
            self.gridLayout_capteur.addWidget(self.progressBar, 0, 1, 1, 1)

        else:
            self.lcdNumber_capteur = QtWidgets.QLCDNumber(self.groupBox_sensors)
            self.lcdNumber_capteur.setMinimumSize(160, 25)
            self.gridLayout_capteur.addWidget(self.lcdNumber_capteur, 0, 1, 1, 1)

        self.layout_box_capteurs.addLayout(self.gridLayout_capteur)

    def remove_capteur(self):
        """ Supprime l'affiche du capteur (QGroupBox) """

        self.groupBox_sensors.hide()

    def update_capteur(self):
        #self.valeur =
        pass

def load_actionneurs(fichier):
    """ Retourne les actionneurs placés dans un fichier .json de la forme:
            - type : binaire, discret, multiple ou plus complexe
            - nom
            -  valeur : valeur initiale
            - min_value : valeur minimale prise par l'actionneur
            - max_value : valeur maximale prse par l'actionneur
            - info : information supplémentaire sur lactionneur comme la liste des états possible ou le nom d'un fichier à lancer"
            - robot : liste des robots concernées par l'actionneur
        sous la forme d'une liste de dictionnaires """

    actionneurs = []
    with open(fichier, encoding='utf-8') as f:
        data = json.load(f)
        data = data["Actionneurs"].copy()
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


def create_space(w=20, h=40) -> QtWidgets.QSpacerItem:
    """ Crée un espace avec la largeur (w) et la longeur (h) passé en paramètre"""
    return QtWidgets.QSpacerItem(w, h, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)


actionneurs = load_actionneurs(ACTIONNEURS_CAPTEURS_FILES)
capteurs = load_capteurs(ACTIONNEURS_CAPTEURS_FILES)
