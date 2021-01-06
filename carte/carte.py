import math
import lxml.etree as ET

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPen, QBrush, QColor

#brosses
ROBOT_COLOR= 'yellow'
ROBOT_BRUSH=QBrush(QColor(ROBOT_COLOR))

class MapView(QtWidgets.QWidget):

    """Un widget permettant de visualiser la carte et les robots dessus"""
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.map_data = []

        # show the window
        self.show()
    
    def paintEvent(self, event):
        """Evt appellé à chaque fois que l'on veut redessiner la map"""
        self.paint()
    
    def paint(self):
        """Dessin de la map"""
        for elt in self.map_data:
            pass
        #dessine robot

    def updt_map_data(self, config_path):
        """Mise à jour des objets à dessiner sur la map
        
        Entrée:
            - config_path (str): le chemin du fichier xml de config map"""
        pass
        


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
        width = 5
        self.setRect(-width, -width, width * 2, width * 2)
        #todo # add tooltip
        tooltip = r.type.name + ' ' + f.call_sign + ' ' + f.qfu
        self.setToolTip(tooltip)

    def controlerobot(self, event):
        """controle du robot en cliquant sur la carte et avec le clavier"""
        
        # Do nothing for the moment...
            #shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(text), self)
            #shortcut.activated.connect(slot)

        #add_shortcut('b_up', lambda: ))
        #add_shortcut('b_down', lambda:)
        #add_shortcut('b_left', lambda )
        #add_shortcut('b_right', lambda )
        #return toolbar
        event.accept()

    def update_position(self):
        """moves the robot in the scene"""
        position = self.robot.get_position(#)
        self.setBrush(ROBOT-BRUSH)
        self.setPos(position.x, position.y)
