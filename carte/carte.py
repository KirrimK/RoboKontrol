import math

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPen, QBrush, QColor

#brosses
robot_brush

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
        
class RobotMotion:
    def __init__(self, radar):
        self.MapView = map
        # list of the current robots
        self.current_robots = []
        # dictionary of the corresponding robots items in the scene
        self.robots_items_dict = {}

        # populate robots dictionary then create and update the corresponding robot items
        self.update_robots_items()
        
    def update_map_items(self):
        """ updates Plots views """
        new_robots = self.mapView.simulation.current_robots
        # add new robots who were added
        for r in set(new_robots) - set(self.current_robots):
            item = mapItem(self.mapView.simulation, r)  # create an item
            self.MapView.scene.addItem(item)  # add it to scene
            self.robots_items_dict[f] = item  # add it to item dict
        # remove robots items for who were deleted
        for r in set(self.current_robots) - set(new_robots):
            item = self.robots_items_dict.pop(f)  # get item  in the dictionary (and remove it)
            self.MapView.scene.removeItem(item)   # remove it also from scene
        # refresh current robots list
        self.current_robots = new_robots
        # get conflicting robots
        conf = self.mapView.simulation.conflicts
        # update positions of the current map items
        for robot in self.robots_items_dict.values():
            robot.update_position(robot. in conf)


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