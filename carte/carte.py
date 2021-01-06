"""Module carte.py - gestion de l'affichage sur la carte"""

import sys
import lxml.etree as ET

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication #, QMainWindow, QWidget
from PyQt5.QtGui import QBrush, QColor, QPainter #,Qpen

#brosses
ROBOT_COLOR= 'yellow'
ROBOT_BRUSH=QBrush(QColor(ROBOT_COLOR))

class MapView(QtWidgets.QWidget):

    """Un widget permettant de visualiser la carte et les robots dessus"""
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.map_data = []
        self.map_width = None
        self.map_height = None
        self.map_margin = None
        self.updt_map_data("map_sail_the_world.xml")

        # show the window
        self.show()

    def paintEvent(self, event):
        """Evt appellé à chaque fois que l'on veut redessiner la map"""
        self.paint()

    def paint(self):
        """Dessin de la map"""
        painter = QPainter(self)
        for rect in self.map_data:
            painter.setBrush(QBrush(QColor(rect[1]), Qt.SolidPattern))
            painter.drawRect(rect[4][0], rect[4][1], rect[3][0], rect[3][1])
            #TODO: modifier en fonction de la taille de la map
        #dessine robot

    def updt_map_data(self, config_path):
        """Mise à jour des objets à dessiner sur la map
        
        Entrée:
            - config_path (str): le chemin du fichier xml de config map
        """
        self.map_data = []
        root = ET.parse(config_path).getroot()
        self.map_width = float(root.attrib.get('width'))
        self.map_height = float(root.attrib.get('height'))
        self.map_margin = float(root.attrib.get('margin'))
        for rect in root.findall('rect'):
            nom = rect.attrib.get('nom')
            color = rect.find("color").text
            order = float(rect.find("order").text)
            size = rect.find("size").text.strip().split("x")
            size[0] = int(size[0])//5
            size[1] = int(size[1])//5
            pos = rect.find("pos").text.strip().split("x")
            pos[0] = int(pos[0])//5
            pos[1] = int(pos[1])//5
            rect_data = (nom, color, order, size, pos)
            self.map_data.append(rect_data)
        
#class RobotItem(QGraphicsEllipseItem):
#    """The view of a robot in the GraphicsScene"""
#
#    def __init__(self, simu, f):
#        """RobotItem constructor, creates the ellipse and adds to the scene"""
#        super().__init__(None)
#        self.setZValue(mapview.PLOT_Z_VALUE)

        # instance variables
#        self.robot = r
#        self.simulation = simu
        # build the ellipse
#        width = #5
#        self.setRect(-width, -width, width * 2, width * 2)

        #todo # add tooltip
#        tooltip = r.type.name + ' ' + f.call_sign + ' ' + f.qfu
#        self.setToolTip(tooltip)

#    def controlerobot(self, event):
        """controle du robot en cliquant sur la carte et avec le clavier"""
        # Do nothing for the moment...
#            shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(text), self)
#            shortcut.activated.connect(slot)

        #add_shortcut('b_up', lambda: ))
        #add_shortcut('b_down', lambda:)
        #add_shortcut('b_left', lambda )
        #add_shortcut('b_right', lambda )
        #return toolbar
#        event.accept()

App = QApplication(sys.argv)
map_view = MapView(None)
sys.exit(App.exec())
