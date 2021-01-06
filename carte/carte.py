import math

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPen, QBrush, QColor

#brosses
ROBOT-COLOR= 'yellow'
robot_brush=QBrush(QColor(ROBOT-COLOR))

class MapView(QtWidgets.QWidget):


    def __init__(self, simu):
        super().__init__()
        self.simulation = simu
        self.time_increment = 1

        # Settings
        
        self.resize(WIDTH, HEIGHT)

        # create components
        root_layout = QtWidgets.QVBoxLayout(self)
        self.scene = QtWidgets.QGraphicsScene()
        self.view = PanZoomView(self.scene)
        self.time_entry = QtWidgets.QLineEdit()
        

        # add the robot elements to the graphic scene and then fit it in the view
        self.add_robots_items()
        self.fit_scene_in_view()

        # maintain a scene graph so as to _update_ plots
        # instead of clearing and recreating them at each update
      #  self.moving_aircraft = radarmotion.AircraftItemsMotionManager(self)

        #todo # add components to the root_layout  
        root_layout.addWidget(self.view)
        root_layout.addLayout(toolbar)

        # create and setup the timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.advance)

        # show the window
        self.show()
        



class RobotItem(QGraphicsEllipseItem):
    """The view of a robot in the GraphicsScene"""

    def __init__(self, simu, f):
        """RobotItem constructor, creates the ellipse and adds to the scene"""
        super().__init__(None)
        self.setZValue(mapview.PLOT_Z_VALUE)

        # instance variables
        self.robot = r
        self.simulation = simu
        # build the ellipse
        width = #5
        self.setRect(-width, -width, width * 2, width * 2)
        # add tooltip
        tooltip = r.type.name + ' ' + f.call_sign + ' ' + f.qfu
        self.setToolTip(tooltip)

    def mousePressEvent(self, event):
        """control du robot en cliquant sur la carte"""
        # Do nothing for the moment...
        event.accept()

    def update_position(self):
        """moves the robot in the scene"""
        position = self.robot.get_position(#)
        self.setBrush(#robot_brush)
        self.setPos(position.x, position.y)