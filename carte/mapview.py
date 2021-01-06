import math

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPen, QBrush, QColor

class MapView(QtWidgets.QWidget):


    def __init__(self, simu):
        super().__init__()
        self.simulation = simu
        self.time_increment = 1

        # Settings
        self.setWindowTitle('interface de controle du robot')
        self.resize(WIDTH, HEIGHT)

        # create components
        root_layout = QtWidgets.QVBoxLayout(self)
        self.scene = QtWidgets.QGraphicsScene()
        self.view = PanZoomView(self.scene)
        self.time_entry = QtWidgets.QLineEdit()
        toolbar = self.create_toolbar()

        

        # add the robot elements to the graphic scene and then fit it in the view
        self.add_robots_items()
        self.fit_scene_in_view()

        # maintain a scene graph so as to _update_ plots
        # instead of clearing and recreating them at each update
      #  self.moving_aircraft = radarmotion.AircraftItemsMotionManager(self)

        # add components to the root_layout
        root_layout.addWidget(self.view)
        root_layout.addLayout(toolbar)

        # create and setup the timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.advance)

        # show the window
        self.show()
    
    