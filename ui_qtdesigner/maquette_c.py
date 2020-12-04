from PyQt5 import QtCore, QtWidgets
import inspector

ACTUATORS_FILE = "actuator.txt"


class Window(object):
    def __init__(self, base_window, number_of_robots=0):
        base_window.resize(1385, 1156)
        base_window.setWindowTitle("app")
        self.number_of_robots = number_of_robots
        self.layout_base_window = QtWidgets.QVBoxLayout(base_window)
        self.menu_area = QtWidgets.QGroupBox(base_window)
        self.menu_area.setTitle("")
        self.menu_area.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft)
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.menu_area)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.button_map = QtWidgets.QPushButton(self.menu_area)
        self.button_map.setMaximumSize(QtCore.QSize(200, 16777215))
        self.button_map.setText("Configurer la carte")
        self.horizontalLayout.addWidget(self.button_map)

        self.button_connect_robot = QtWidgets.QPushButton(self.menu_area)
        self.button_connect_robot.setText("Connecter un robot")
        self.horizontalLayout.addWidget(self.button_connect_robot)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.button_help = QtWidgets.QPushButton(self.menu_area)
        self.button_help.setText("Aide")
        self.horizontalLayout.addWidget(self.button_help)
        self.layout_base_window.addWidget(self.menu_area)

        self.layout_map_inspector = QtWidgets.QHBoxLayout()

        self.map_view = QtWidgets.QGraphicsView(base_window)
        self.map_view.setMinimumSize(QtCore.QSize(0, 250))
        self.layout_map_inspector.addWidget(self.map_view)

        self.inspector_scroll_area = QtWidgets.QScrollArea(base_window)
        self.inspector_scroll_area.setMaximumSize(QtCore.QSize(270, 16777215))
        self.inspector_scroll_area.setWidgetResizable(True)

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 268, 1046))

        self.layout_scroll_area = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)

        self.button_add_robot = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.button_add_robot.setText("Ajouter un Robot")
        self.layout_scroll_area.addWidget(self.button_add_robot)
        self.button_add_robot.clicked.connect(lambda: self.add_robot(self.number_of_robots))

        self.add_robot(self.number_of_robots)

        self.inspector_scroll_area.setWidget(self.scrollAreaWidgetContents)
        self.layout_map_inspector.addWidget(self.inspector_scroll_area)
        self.layout_base_window.addLayout(self.layout_map_inspector)

        self.message_area = QtWidgets.QGroupBox(base_window)
        self.message_area.setMaximumSize(QtCore.QSize(16777215, 40))
        self.message_area.setTitle("")
        self.message_area.setObjectName("message_area")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.message_area)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.message_robot1 = QtWidgets.QLabel(self.message_area)
        self.message_robot1.setMaximumSize(QtCore.QSize(16777215, 30))
        self.message_robot1.setObjectName("message_robot1")
        self.message_robot1.setText("dernier message robot 1: __ms")
        self.horizontalLayout_5.addWidget(self.message_robot1)
        self.message_robot2 = QtWidgets.QLabel(self.message_area)
        self.message_robot2.setMaximumSize(QtCore.QSize(16777215, 30))
        self.message_robot2.setObjectName("message_robot2")
        self.message_robot2.setText("dernier message robot 1: __ms")
        self.horizontalLayout_5.addWidget(self.message_robot2)
        self.message_robot3 = QtWidgets.QLabel(self.message_area)
        self.message_robot3.setMaximumSize(QtCore.QSize(16777215, 30))
        self.message_robot3.setObjectName("message_robot3")
        self.message_robot3.setText("dernier message robot 3: __ms")
        self.horizontalLayout_5.addWidget(self.message_robot3)
        self.layout_base_window.addWidget(self.message_area)
        QtCore.QMetaObject.connectSlotsByName(base_window)

    def add_robot(self, robot_number):
        self.box_robot = inspector.Box_robot(self.layout_scroll_area, robot_number)
        self.box_robot.add_box_robot()
        self.number_of_robots += 1


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    base_window = QtWidgets.QWidget()
    ui = Window(base_window)
    base_window.show()
    sys.exit(app.exec_())
