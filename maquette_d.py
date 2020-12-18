from PyQt5 import QtCore, QtGui, QtWidgets
import inspecteur

class Ui_base_window(object):
    def __init__(self, base_window, number_robots = 0):
        base_window.setObjectName("base_window")
        base_window.resize(1091, 782)
        base_window.setWindowTitle("Form")
        self.number_robots = number_robots

        self.layout_window = QtWidgets.QVBoxLayout(base_window)

        self.menu_area = QtWidgets.QGroupBox(base_window)
        self.menu_area.setTitle("")
        self.menu_area.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)

        self.layout_menu = QtWidgets.QHBoxLayout(self.menu_area)

        self.button_map = QtWidgets.QPushButton(self.menu_area)
        self.button_map.setMaximumSize(QtCore.QSize(200, 16777215))
        self.button_map.setText("Configurer la carte")
        self.layout_menu.addWidget(self.button_map)

        self.button_connect_robot = QtWidgets.QPushButton(self.menu_area)
        self.button_connect_robot.setText("Connecter un robot")
        self.layout_menu.addWidget(self.button_connect_robot)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layout_menu.addItem(spacerItem)

        self.button_help = QtWidgets.QPushButton(self.menu_area)
        self.button_help.setText("Aide")
        self.layout_menu.addWidget(self.button_help)

        self.layout_window.addWidget(self.menu_area)


        self.layout_map_inspector = QtWidgets.QHBoxLayout()
        self.map_view = QtWidgets.QGraphicsView(base_window)
        self.map_view.setMinimumSize(QtCore.QSize(0, 250))
        self.layout_map_inspector.addWidget(self.map_view)



        self.create_inspecteur_scrollbar()

        """Ajoute les boites robots"""

        self.add_robot()

        self.inspector_scroll_area.setWidget(self.scrollAreaWidgetContents)
        self.layout_map_inspector.addWidget(self.inspector_scroll_area)
        self.layout_window.addLayout(self.layout_map_inspector)




        self.message_area = QtWidgets.QGroupBox(base_window)
        self.message_area.setMaximumSize(QtCore.QSize(16777215, 40))
        self.message_area.setTitle("")
        self.layout_message_menu = QtWidgets.QHBoxLayout(self.message_area)
        self.message_robot1 = QtWidgets.QLabel(self.message_area)
        self.message_robot1.setMaximumSize(QtCore.QSize(16777215, 30))
        self.message_robot1.setText("dernier message robot 1: __ms")
        self.layout_message_menu.addWidget(self.message_robot1)
        self.message_robot2 = QtWidgets.QLabel(self.message_area)
        self.message_robot2.setMaximumSize(QtCore.QSize(16777215, 30))
        self.message_robot2.setText("dernier message robot 2: __ms")
        self.layout_message_menu.addWidget(self.message_robot2)
        self.message_robot3 = QtWidgets.QLabel(self.message_area)
        self.message_robot3.setMaximumSize(QtCore.QSize(16777215, 30))
        self.message_robot3.setText("dernier message robot 3: __ms")
        self.layout_message_menu.addWidget(self.message_robot3)


        self.layout_window.addWidget(self.message_area)

        QtCore.QMetaObject.connectSlotsByName(base_window)

    def add_robot(self):
        self.boite_robot = inspecteur.BoiteRobot(self.scrollAreaWidgetContents, self.layout_inspector, self.number_robots)
        self.boite_robot.add_box_robot()
        self.number_robots += 1

    def create_inspecteur_scrollbar(self):
        self.inspector_scroll_area = QtWidgets.QScrollArea(base_window)
        #self.inspector_scroll_area.setStyleSheet("background-color: deepskyblue")  #customisation de la boite robot(couleur fond)
        self.inspector_scroll_area.setMinimumSize(QtCore.QSize(350, 0))
        self.inspector_scroll_area.setMaximumSize(QtCore.QSize(350, 16777215))
        self.inspector_scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.inspector_scroll_area.setWidgetResizable(True)

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 333, 882))
        self.layout_inspector = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)

        self.button_add_robot = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.button_add_robot.setMinimumSize(QtCore.QSize(0, 30))
        self.button_add_robot.setText("Ajouter un robot")
        self.button_add_robot.clicked.connect(lambda: self.add_robot())
        self.layout_inspector.addWidget(self.button_add_robot)



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    base_window = QtWidgets.QWidget()
    ui = Ui_base_window(base_window)
    base_window.show()
    #base_window.setStyleSheet("QGroupBox { border: 1px solid deepskyblue;}" + "QGroupBox { background-color: white;}")
    sys.exit(app.exec_())
