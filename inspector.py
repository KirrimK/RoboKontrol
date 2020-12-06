from PyQt5 import QtWidgets
import json

ACTUATORS_FILES = "actuator.json"


class Box_robot:
    def __init__(self, parent_widget, robot_number: int):
        """Création d'une boite robot avec:
        -nom du robot
        -Position (x,y,angle)
        -Actioneurs
        -Bouton supprimer
        """
        self.robot_number = robot_number
        self.box_robot = QtWidgets.QGroupBox()
        self.layout_box = QtWidgets.QVBoxLayout(self.box_robot)

        self.parent_widget = parent_widget
        self.parent_widget.addWidget(self.box_robot)

        self.layout_name_button = QtWidgets.QHBoxLayout()
        self.label_name_robot = QtWidgets.QLabel(self.box_robot)
        self.button_delete = QtWidgets.QPushButton(self.box_robot)
        self.label_location = QtWidgets.QLabel(self.box_robot)

        self.layout_x = QtWidgets.QHBoxLayout()
        self.label_x = QtWidgets.QLabel(self.box_robot)
        self.label_x.setText("X:")
        self.lcdNumber_x = QtWidgets.QLCDNumber(self.box_robot)

        self.layout_y = QtWidgets.QHBoxLayout()
        self.label_y = QtWidgets.QLabel(self.box_robot)
        self.label_y.setText("Y:")
        self.lcdNumber_y = QtWidgets.QLCDNumber(self.box_robot)

        self.layout_angle = QtWidgets.QHBoxLayout()
        self.label_angle = QtWidgets.QLabel(self.box_robot)
        self.label_angle.setText("Angle:")
        self.lcdNumber_angle = QtWidgets.QLCDNumber(self.box_robot)

        self.label_actuators = QtWidgets.QLabel(self.box_robot)

        self.boxes = {}

    def layout_name_button_delete(self):
        """Créer le layout contenant le nom et le bouton supprimer du robot"""

        self.label_name_robot.setText("Robot [{}]".format(self.robot_number))
        self.layout_name_button.addWidget((self.label_name_robot))
        self.button_delete.setText("Supprimer")
        self.layout_name_button.addWidget(self.button_delete)
        self.layout_box.addLayout(self.layout_name_button)

    def layout_location(self):
        """Créer le layout poisition de la boite robot"""
        self.label_location.setText("Position:")
        self.layout_box.addWidget(self.label_location)
        self.layout_x.addWidget(self.label_x)
        self.layout_x.addWidget(self.lcdNumber_x)
        self.layout_box.addLayout(self.layout_x)
        self.layout_y.addWidget(self.label_y)
        self.layout_y.addWidget(self.lcdNumber_y)
        self.layout_box.addLayout(self.layout_y)
        self.layout_angle.addWidget(self.label_angle)
        self.layout_angle.addWidget(self.lcdNumber_angle)
        self.layout_box.addLayout(self.layout_angle)

    def label_actuator(self):
        self.label_actuators.setText("Actionneurs")
        self.layout_box.addWidget(self.label_actuators)

    def add_actuator(self, list_of_dic):

        data = list_of_dic.copy()

        for dic in data:

            actuator_name  = dic['nom']
            default_choice = int(dic['choix_initial'])
            list_options = dic['choix'].strip('][').split(', ')    #conversion str to list
            list_robot = dic['robot'].strip('][').split(', ')      #conversion str to list

            if int_in_list(self.robot_number, list_robot):

                self.layout_add_actuator = QtWidgets.QHBoxLayout()
                self.label_add_actuator = QtWidgets.QLabel(self.box_robot)
                self.comboBox_add_actuator = QtWidgets.QComboBox(self.box_robot)
                self.comboBox_add_actuator.addItem(list_options[default_choice].strip('"'))
                for i in range(len(list_options)):
                    if i != default_choice:
                        self.comboBox_add_actuator.addItem(list_options[i].strip('"'))

                self.label_add_actuator.setText(actuator_name)

                self.layout_add_actuator.addWidget(self.label_add_actuator)
                self.layout_add_actuator.addWidget(self.comboBox_add_actuator)

                self.layout_box.addLayout(self.layout_add_actuator)

    def add_box_robot(self):
        """Permet l'ajout d'une boite robot"""
        self.layout_name_button_delete()
        self.layout_location()
        self.label_actuator()
        self.add_actuator(list_dic_actuators)
        n = self.robot_number
        self.boxes[n] = [self.box_robot, self.button_delete]
        self.boxes[n][1].clicked.connect(lambda: self.remove_box_robot(n))

    def remove_box_robot(self, number_delete):
        """Permet la suppression de la boite robot dont le numéro est placé en paramètre"""
        self.boxes[number_delete][0].hide()


def int_in_list(n, l):
    """Teste si l'entier n (type str) est compris dans la liste"""
    for i in l:
        if int(i) == n:
            return True
        else:
            pass


def load_actuators(fichier):
    """Retourne les actionneurs placés dans un fichier .json de la forme:
            - nom
            - liste des choix (type string)
            - indince du choix par défauts
            - liste des robots qui ont cet actionneur (type string)
        sous la forme d'une liste de dictionnaires"""

    l = []
    with open(fichier) as f:
        data = json.load(f)
    for dic in data["Actionneur"]:
        l.append(dic)
    return l


list_dic_actuators = load_actuators(ACTUATORS_FILES)
