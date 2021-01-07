""" boite_robot.py - Gère l'affichage d'une boite robot dans le layout parent situé dans le layout widget et effectue les mise à jours liées a ce robot"""

from PyQt5 import QtWidgets, QtCore
import annuaire
import time

#TODO: ajouter min max step aux capteurs
# Définition des mins et maxs de tension pour la batterie (en V)
MIN_BATTERIE = 9
MAX_BATTERIE = 12

# Customisation
QPROGRESSBAR = "QProgressBar{background-color : grey;border : 1px; border: 2px solid grey; border-radius: 5px}"
QLCD_STYLE = "QLCDNumber{background-color: grey;border: 2px solid rgb(113, 113, 113);border-width: 2px; " \
             "border-radius: 10px;  color: rgb(255, 255, 255)} "
QPUSHBUTTON = "QPushButton{background-color: grey; border 2px solid rgb(113, 113, 113);border-width: 2px; " \
              "border-radius: 10px;  color: rgb(0,0,0)} "

# Alignment
QT_CENTER = QtCore.Qt.AlignCenter
QT_TOP = QtCore.Qt.AlignTop


class BoiteRobot:
    """Définit un objet boite robot qui hérite des infomations du robot auquel il est associé et instancie
    l'affichage dans l'inspecteur sous forme QGroupBox """

    def __init__(self, parent_widget, parent_layout, rid, inspector):
        """Crée la boite robot dans le parent_layout situé dans un parent_widget et lui associe le numéro
        robot_number """

        self.rid = rid
        self.inspecteur = inspector
        self.parent_widget = parent_widget
        self.parent_layout = parent_layout
        self.position = ()
        self.timestamp = time.time()

        self.groupBox_robot = QtWidgets.QGroupBox(self.parent_widget)
        self.layout_box_robot = QtWidgets.QVBoxLayout(self.groupBox_robot)
        self.parent_layout.addWidget(self.groupBox_robot, 0, QT_TOP)

        # Liste des équipements attachés au robot
        self.current_equipement_list = []
        self.current_equipement_dic = {}
        self.current_actuators_list = []
        self.current_actionneurs_dic = {}
        self.current_sensors_list = []
        self.current_capteurs_dic = {}

        # Création de l'entête position
        self.create_position()
        self.create_box_actuators()
        self.create_box_sensors()
        self.QLineEdit_position_command = None

    def create_position(self):
        """Crée l'entête de la boite robot où l'on retrouve son nom, le bouton supprimer et ses coordonnées)"""

        self.layout_name_delete = QtWidgets.QHBoxLayout()
        # self.layout_name_delete.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)

        self.label_name = QtWidgets.QLabel(self.groupBox_robot)
        self.label_name.setMinimumSize(0, 30)
        self.label_name.setMaximumSize(100, 30)
        self.label_name.setText(self.rid)
        self.layout_name_delete.addWidget(self.label_name)

        self.button_delete = QtWidgets.QPushButton(self.groupBox_robot)
        self.button_delete.setMaximumSize(150, 30)
        self.button_delete.setStyleSheet(QPUSHBUTTON)
        self.button_delete.setText("Oublier")
        self.button_delete.clicked.connect(lambda: self.remove_box_robot())
        self.layout_name_delete.addWidget(self.button_delete)

        self.layout_box_robot.addLayout(self.layout_name_delete)

        # Création de l'affichage des coordonnées"
        self.lcdNumber_x = self.create_coord("X", "mm")
        self.lcdNumber_y = self.create_coord("Y", "mm")
        self.lcdNumber_theta = self.create_coord("Orientation", "degré")
        self.lcdNumber_ping_pos = self.create_coord("Dernier message", "s")

        #Création de l'envoyeur de commandes
        self.layoutCommand = QtWidgets.QHBoxLayout ()
        self.layoutCommand.setContentsMargins (0, 0, 0, 0)
        
        self.label_positionCommand = QtWidgets.QLabel (self.groupBox_robot)
        self.label_positionCommand.setText ("Dernière commande envoyée : ")
        
        self.QLineEdit_positionCommand = QtWidgets.QLineEdit (self.groupBox_robot)
        self.QLineEdit_positionCommand.setInputMask("0000 : 0000 : 000")
        self.QLineEdit_positionCommand.setText ("1500 : 0000 : 000")
        self.QLineEdit_positionCommand.editingFinished.connect (lambda : self.onEditingFinished ())

        self.layoutCommand.addWidget (self.label_positionCommand)
        self.layoutCommand.addWidget (self.QLineEdit_positionCommand)
        self.layout_box_robot.addLayout(self.layoutCommand)
        
    def onEditingFinished (self):
        """"Appelée après la fin de l'édition de self.QLineEdit_positionCommand"""
        self.inspecteur.backend.sendposcmd_robot (self.rid, list (int (i) for i in self.QLineEdit_positionCommand.text ().split (' : ')))

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

    def create_box_actuators(self):
        """ Crée la boite actionneurs (QGroupBox) et l'ajoute dans la boite robot"""

        self.groupBox_actuator = QtWidgets.QGroupBox(self.groupBox_robot)
        self.groupBox_actuator.setAlignment(QT_CENTER)
        self.groupBox_actuator.setTitle("Actionneurs")
        self.layout_box_actuators = QtWidgets.QVBoxLayout(self.groupBox_actuator)
        self.layout_box_robot.addWidget(self.groupBox_actuator, 0, QT_TOP)

    def create_box_sensors(self):
        """ Crée la boite capteurs (QGroupBox) et l'ajoute dans la boite robot"""

        self.groupBox_sensors = QtWidgets.QGroupBox(self.groupBox_robot)
        self.groupBox_sensors.setAlignment(QT_CENTER)
        self.groupBox_sensors.setTitle("Capteurs:")
        self.layout_box_capteurs = QtWidgets.QVBoxLayout(self.groupBox_sensors)
        self.layout_box_robot.addWidget(self.groupBox_sensors, 0, QT_TOP)

    @QtCore.pyqtSlot()
    def remove_box_robot(self):
        """Permet la suppression de la boite robot dont le numéro est placé en paramètre"""

        self.groupBox_robot.hide()
        self.inspecteur.backend.stopandforget_robot(self.rid)

    def update_position(self):
        """Met à jour la position de la boite robot"""

        # Mise à jour du vecteur position du robot
        self.position = self.inspecteur.backend.getdata_robot(self.rid)[0]
        # Récupération du timestamp de dernière mise à jour de la position
        self.last_updt_pos = self.inspecteur.backend.getdata_robot(self.rid)[2]  # todo:pb de remise à 0?

        # Calcul du ping
        self.timestamp = time.time()
        self.ping = abs(self.last_updt_pos-self.timestamp)

        # Mise à jour des valeurs affichés par les QLCDNUmber
        self.lcdNumber_x.display(self.position[0])
        self.lcdNumber_y.display(self.position[1])
        self.lcdNumber_theta.display(self.position[2])
        self.lcdNumber_ping_pos.display(self.ping)

    def load_equipement(self):
        """ Charge la liste des des équipements du robot et charge les informations de chaque équipement présent"""

        # Mise à jour de la liste de l'équipement du robot
        self.equipement_list = self.inspecteur.backend.getdata_robot(self.rid)[1]
        equipements = {}

        for eqp_name in self.equipement_list:
            eqp = self.inspecteur.backend.getdata_eqp(self.rid, eqp_name)
            eqp_type = eqp[0]
            eqp_value = eqp[1]
            eqp_last_updt = eqp[2]
            eqp_last_cmd = eqp[3]
            eqp_unit = eqp[4]

            if eqp_type == annuaire.Actionneur:
                valeur, min_val, max_val, step = eqp_value
                equipements[eqp_name] = Actuator(eqp_name, valeur, min_val, max_val, step, eqp_unit, "DISCRET",
                                                 self.groupBox_actuator, self.layout_box_actuators, self.inspecteur.backend, self.rid,  eqp_last_updt)
            if eqp_type == annuaire.Binaire:
                equipements[eqp_name] = Actuator(eqp_name, eqp_value, 0, 1, 1, None, "BINAIRE", self.groupBox_actuator,
                                                 self.layout_box_actuators, self.inspecteur.backend, self.rid, eqp_last_updt)

            if eqp_type == annuaire.Capteur:
                valeur, minV, maxV, step = eqp_value
                sensor = Sensor(eqp_name, valeur, minV, maxV, step, eqp_unit, self.groupBox_sensors,
                                self.layout_box_capteurs, eqp_last_updt)
                equipements[eqp_name] = sensor

        return equipements

    def update_equipements(self):
        """ Met à jour l'ensemble des équipements accrochés au robots et initialise la mise à jour de chaque
        équipement """

        # Mets à jour le dictionnaire des équipements
        equipements = self.load_equipement()
        # Crée une liste des équipemnts présents sur le robot
        equipements_list = [key for key in equipements.keys()]

        # Ajoute les nouveaux équipements
        for name in set(equipements_list) - set(self.current_equipement_list):
            self.current_equipement_dic[name] = equipements[name]
            equipement = equipements[name]
            if type(equipement) == Actuator:
                actuator = equipements[name]
                self.current_actuators_list.append (name)
                actuator.add_actuator()
            if type(equipement) == Sensor:
                self.current_sensors_list.append (name)
                sensor = equipements[name]
                sensor.add_capteur()

        # Supprime les équipements qui ne sont plus présents
        for name in set(self.current_equipement_list) - set(equipements_list):
            equipement = self.current_equipement_dic.pop(name)
            if type(equipement) == Actuator:
                actuator = equipements[name]
                self.current_actuators_list.pop (self.current_actuators_list.index (name))
                actuator.remove_actionneur()
            if type(equipement) == Sensor:
                sensor = equipements[name]
                self.current_sensors_list.pop ( self.current_sensors_list.index (name))
                sensor.remove_capteur()

        #Change les capteurs en actionneurs si neccessaire.
        for name in self.current_sensors_list :
            if type (equipements [name]) == Actuator :
                actuator = equipements [name]
                self.current_actuators_list.append (name)
                self.current_sensors_list.pop ( self.current_sensors_list.index (name))
                actuator.add_actuator()
                sensor = self.current_equipement_dic [name]
                sensor.remove_capteur ()

        # Met à jour la liste et le dictionnaire des capteurs présents
        self.current_equipement_list = equipements_list
        self.current_equipement_dic = equipements

        # Initialise la mise à jours des capteurs
        for equipement in self.current_equipement_dic.values():
            if type(equipement) == Sensor:
                equipement.update_capteur()
            if type(equipement) == Actuator:
                equipement.update_actuator()
        self.layout_box_actuators.update ()

    @QtCore.pyqtSlot()
    def update_boite_robot(self):
        """ Initialise la mise à jour de la position et des équipements du robot de la boite robot """

        self.update_position()
        self.update_equipements()


class Actuator:
    """ Définit l'affichage d'un actionneur (QGridLayout) situé dans la boite actionneur """

    def __init__(self, nom: str, valeur: int or tuple, min_val, max_val, step: float, unite: str or None, type: str,
                 boite_actionneurs, layout_boite_actionneurs, backend, rid,
                 last_update):
        """ Crée l'affichage de l'actionneur (hérité de la classe Actionneur d'annuaire) et l'ajoute dans la
        boite actionneurs """
        self.nom = nom
        self.rid = rid
        self.backend = backend
        self.min_val = min_val
        self.max_val = max_val
        self.groupBox_actuator = boite_actionneurs
        self.layout_box_actuators = layout_boite_actionneurs
        self.unite = unite
        self.value = valeur
        self.type_actionneur = type
        self.step = step
        self.info_actionneur = ["état1", "état2", "état3", "état4", "état5"]
        # TODO : ajouter les actionneurs types multiples
        self.last_commande = ""
        self.last_update = last_update
        self.timestamp = time.time()

        self.gridLayout_actuator = QtWidgets.QGridLayout()
        self.label_name_actuator = QtWidgets.QLabel(self.groupBox_actuator)
        self.label_actuator_tps = QtWidgets.QLabel(self.groupBox_actuator)
        self.label_actuator_command = QtWidgets.QLabel(self.groupBox_actuator)
        self.lcdNumber_ping_actuator = QtWidgets.QLCDNumber(self.groupBox_actuator)
        if self.type_actionneur == "BINAIRE":
            self.checkBox_actuator = QtWidgets.QCheckBox(self.groupBox_actuator)

        if self.type_actionneur == "DISCRET":
            self.doubleSpinBox_actuator = QtWidgets.QDoubleSpinBox(self.groupBox_actuator)

        if self.type_actionneur == "MULTIPLE":
            self.comboBox_actuator = QtWidgets.QComboBox(self.groupBox_actuator)

        if self.type_actionneur == "COMPLEXE":
            self.pushButton_actuator = QtWidgets.QPushButton(self.groupBox_actuator)

    def add_actuator(self):
        """Ajoute un actionneur (QGridLayout) dans la boite actionneurs (QGroupBox)"""

        # spacerItem_actionneur = create_space()
        # self.layout_box_actuators.addItem(spacerItem_actionneur)

        if self.unite is None:
            self.label_name_actuator.setText(self.nom)
        else:
            self.label_name_actuator.setText("{0} ({1})".format(self.nom, self.unite))

        self.gridLayout_actuator.addWidget(self.label_name_actuator, 0, 0, 1, 1)

        self.label_actuator_tps.setText("Dernier message (s)")
        self.label_actuator_tps.setMinimumSize(120, 30)

        self.label_actuator_command.setText ("Dernière commande : ")
        
        self.gridLayout_actuator.addWidget(self.label_actuator_tps, 1, 0, 1, 1)
        self.gridLayout_actuator.addWidget(self.label_actuator_command, 2, 0, 1, 1)
        self.lcdNumber_ping_actuator.setMaximumSize(QtCore.QSize(16777215, 25))
        self.gridLayout_actuator.addWidget(self.lcdNumber_ping_actuator, 1, 1, 1, 1)
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

        self.checkBox_actuator.setText("")
        self.gridLayout_actuator.addWidget(self.checkBox_actuator, 0, 1, 1, 1, QT_CENTER)

    def create_actuator_discret(self):
        """Crée et ajoute un actionneur de type discret (QDoubleSpinBox)"""

        self.doubleSpinBox_actuator.setMinimumSize(0, 30)
        self.doubleSpinBox_actuator.setMaximum(self.max_val)
        self.doubleSpinBox_actuator.setMinimum(self.min_val)
        self.doubleSpinBox_actuator.setSingleStep(self.step)
        self.doubleSpinBox_actuator.valueChanged.connect (lambda : self.onValueChanged())
        try:
            self.doubleSpinBox_actuator.setValue(self.value)
        except TypeError:
            pass
        self.gridLayout_actuator.addWidget(self.doubleSpinBox_actuator, 0, 1, 1, 1)

    def onValueChanged (self):
        self.backend.sendeqpcmd (self.rid,self.nom,self.doubleSpinBox_actuator.value())
        self.label_actuator_command.setText ("Dernière commande : {}".format (self.doubleSpinBox_actuator.value()))

    def create_actuator_multiple(self):
        """Crée et ajoute un actionneur de type multiple (QComboBox)"""
        list_options = self.info_actionneur
        
        self.comboBox_actuator.addItem(list_options[self.value].strip('"'))
        for i in range(len(list_options)):
            if i != self.value:
                self.comboBox_actuator.addItem(list_options[i].strip('"'))

        self.gridLayout_actuator.addWidget(self.comboBox_actuator, 0, 1, 1, 1)

    def create_actuator_led(self):
        """ Création d'un actionneur complexe spéciale : la LED """
        self.pushButton_led = QtWidgets.QPushButton(self.groupBox_actuator)
        self.pushButton_led.setText("Choisir la couleur")
        self.pushButton_led.clicked.connect(lambda: self.open_LED_menu())
        self.gridLayout_actuator.addWidget(self.pushButton_led, 0, 1, 1, 1)

    def create_actuator_complexe(self):
        """Crée et ajoute un actionneur de type complexe (QPushButton) : il s'agit d'un bouton qui peut ouvrir un
        menu plus détaillée de l'actionneur (QDialog par exemple) """
        self.pushButton_actuator.setText(self.info_actionneur[0])
        self.pushButton_actuator.clicked.connect(lambda: self.open_actionneur_complexe())
        self.gridLayout_actuator.addWidget(self.pushButton_actuator, 0, 1, 1, 1)

    @QtCore.pyqtSlot()
    def open_LED_menu(self):
        """Ouvre une fenêtre de sélection de couleur (QColorDialog) et modifie la valeur de l'actionneur la couleur
        choisie """

        self.value = QtWidgets.QColorDialog.getColor().name()
        self.pushButton_led.setStyleSheet("background-color : {0};".format(self.value))

    @QtCore.pyqtSlot()
    def open_actionneur_complexe(self):  # TODO: idée d'autres actionneurs complexes?
        """Ouvre un QDilaog à définir qui change la valeur de l'actionneur"""

        self.value = QtWidgets.QDialog()

    def remove_actionneur(self):
        """Supprime l'affiche de l'actionneur (QGroupBox)"""

        self.groupBox_actuator.hide()

    def update_actuator(self):
        """ Met à jour l'actionneur """

        # Calcul du ping
        self.timestamp = time.time()
        self.ping_actuator = abs(self.timestamp - self.last_update)
        self.lcdNumber_ping_actuator.display(self.ping_actuator)

        # Mise à jour des informations de l'actionneur suivant son type
        if self.type_actionneur == "DISCRET":
            try:
                self.doubleSpinBox_actuator.setValue(self.value)
                print (self.doubleSpinBox_actuator.value())
            except TypeError:
                pass
        if self.type_actionneur == "BINAIRE":
            if self.value == 0:
                self.checkBox_actuator.setChecked(False)
            if self.value == 1:
                self.checkBox_actuator.setChecked(True)

        if self.type_actionneur == "LED":
            self.pushButton_led.setStyleSheet("background-color : {0};".format(self.value))


class Sensor:#TODO : Rendre la classe compatible avec le backend (ajout de min, max et step)
    """ Crée l'affichage d'un capteur (hérité de la classe Capteur d'annuaire) et l'ajoute dans la boite capteurs """

    def __init__(self, nom, valeur, minV, maxV, step, unite, boite_capteurs, layout_boite_capteurs, last_update):
        """ Héritagede la classe Capteur de annuaire et création de l'affichage du capteur puis ajout dans boite
        capteurs """

        self.nom = nom
        self.valeur = valeur
        self.minV, self.maxV, self.step = minV, maxV, step
        self.unite = unite
        self.layout_box_capteurs = layout_boite_capteurs
        self.groupBox_sensors = boite_capteurs
        self.last_update = last_update
        self.timestamp = time.time()

        self.gridLayout_capteur = QtWidgets.QGridLayout()

        self.label_nom_capteur = QtWidgets.QLabel(self.groupBox_sensors)
        self.label_nom_capteur.setMinimumSize(0, 30)
        self.label_nom_capteur.setMaximumSize(100, 30)
        self.label_nom_capteur.setText('{0} ({1}):'.format(self.nom, self.unite))
        self.gridLayout_capteur.addWidget(self.label_nom_capteur, 0, 0, 1, 1)

        self.label_message_capteur = QtWidgets.QLabel(self.groupBox_sensors)
        self.label_message_capteur.setText("Dernier message (ms)")
        self.gridLayout_capteur.addWidget(self.label_message_capteur, 1, 0, 1, 1)

        self.lcdNumber_ping_capteur = QtWidgets.QLCDNumber(self.groupBox_sensors)
        self.lcdNumber_ping_capteur.setMaximumSize(QtCore.QSize(16777215, 25))
        self.gridLayout_capteur.addWidget(self.lcdNumber_ping_capteur, 1, 1, 1, 1)
        self.lcdNumber_capteur = QtWidgets.QLCDNumber(self.groupBox_sensors)

    def add_capteur(self):
        """ Ajoute un capteur (QGridLayout) dans la boite capteur (QGroupBox) """
        
        if self.nom == "Batterie":
            n = 100  # n permet d'afficher les décimales de la tension
            self.progressBar = QtWidgets.QProgressBar(self.groupBox_sensors)
            self.progressBar.setRange(MIN_BATTERIE * n, MAX_BATTERIE * n)
            if not self.valeur is None :
                self.progressBar.setValue(self.valeur * n)
            self.progressBar.setFormat(str(self.valeur))
            self.progressBar.setStyleSheet(QPROGRESSBAR)
            self.progressBar.setAlignment(QT_CENTER)
            self.gridLayout_capteur.addWidget(self.progressBar, 0, 1, 1, 1)
            self.progressBar.setMaximumSize(160, 25)

        else:
            self.lcdNumber_capteur.setMinimumSize(160, 25)
            self.gridLayout_capteur.addWidget(self.lcdNumber_capteur, 0, 1, 1, 1)
            self.lcdNumber_capteur.display(self.valeur)

        self.layout_box_capteurs.addLayout(self.gridLayout_capteur)

    def remove_capteur(self):
        """ Supprime l'affiche du capteur (QGroupBox) """

        self.groupBox_sensors.hide()

    def update_capteur(self):
        """ Met à jour le capteur """

        # Calcul du ping
        self.timestamp = time.time()
        self.ping = abs(self.timestamp - self.last_update)
        self.lcdNumber_ping_capteur.display(self.ping)

        # Met à jour à jour les informations du capteur
        if self.valeur is not None :
            self.lcdNumber_capteur.display(self.valeur)
