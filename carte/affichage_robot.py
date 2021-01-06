from PyQt5 import Qwidget
import #todo
class Robotview:
    def __init__(self,Qwidget):
        self.ui = #todo
        self.ui.setupUi(self)
        
        
        
    def paintEvent(self, event):
    
        # calls super paintEvent method
        QPushButton.paintEvent(self, event)
        # adds custom drawing code
        qp = QPainter()
        qp.begin(self)
        qp.setPen(Qt.red)
        qp.drawEllipse(#position du robot) #todo
        qp.end()
        #change la position affichée(a faire)
        root_layout = QtWidgets.QVBoxLayout(self)
        self.scene = QtWidgets.QGraphicsScene()
class Robots:
    #liste des robots
    def __ init__(self):
                
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

    def update_position(self, is_conflict):
        """moves the robot in the scene"""
        position = self.robot.get_position(#)
        self.setBrush(#DEP_BRUSH if self.flight.type == traffic.Movement.DEP else ARR_BRUSH)
        self.setPos(position.x, position.y)