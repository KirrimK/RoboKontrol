import math

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPen, QBrush, QColor

#brosses
ROBOT-COLOR= 'yellow'
robot_brush=QBrush(QColor(ROBOT-COLOR))

class MapView(QtWidgets.QWidget):


    def __init__(self, simu):
        super().__init__()

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
