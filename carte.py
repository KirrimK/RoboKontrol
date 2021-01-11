"""Module carte.py - gestion de l'affichage sur la carte"""

import sys
import lxml.etree as ET

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication #, QMainWindow, QWidget,
from PyQt5.QtGui import QBrush, QColor, QPainter #, QPen

#brosses
ROBOT_COLOR= 'gold'
ROBOT_BRUSH=QBrush(QColor(ROBOT_COLOR))

class MapView(QtWidgets.QWidget):

    """Un widget permettant de visualiser la carte et les robots dessus"""
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.map_data = []
        self.map_width = 10
        self.map_height = 10
        self.map_margin = 0

        self.mouse_pos = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.repaint)
        self.timer.start(100)

        self.show()

    def paintEvent(self, event):
        """Evt appellé à chaque fois que le widget est resize ou caché"""
        self.paint()

    def paint(self):
        """Dessin de la map et des robots"""
        painter = QPainter(self)
        for rect in self.map_data:
            size = rect[3]
            pos = rect[4]
            size, pos = self.calc_pos_size(size, pos)
            painter.setBrush(QBrush(QColor(rect[2]), Qt.SolidPattern))
            painter.drawRect(pos[0], pos[1], size[0], size[1])
        #dessine robot

    def updt_map_data(self, config_path):
        """Mise à jour des objets à dessiner sur la map

        Entrée:
            - config_path (str): le chemin du fichier xml de config map
        """
        self.map_data = []
        try:
            root = ET.parse(config_path).getroot()
            self.map_width = int(root.attrib.get('width'))
            self.map_height = int(root.attrib.get('height'))
            self.map_margin = int(root.attrib.get('margin'))
            for rect in root.findall('rect'):
                nom = rect.attrib.get('nom')
                color = rect.find("color").text
                order = float(rect.find("order").text)
                size = rect.find("size").text.strip().split("x")
                pos = rect.find("pos").text.strip().split("x")
                rect_data = (order, nom, color, size, pos)
                self.map_data.append(rect_data)
            self.map_data.sort()
        except Exception as e:
            print(e)

    def calc_pos_size(self, size, pos):
        """Calcule les positions et tailles en fonction de la taille du widget"""
        new_pos = [0, 0]
        new_size = [0, 0]
        new_pos[0] = int(pos[0])
        new_pos[1] = int(pos[1])
        new_size[0] = int(size[0])
        new_size[1] = int(size[1])
        width = self.geometry().width()
        height = self.geometry().height()
        map_ttl_height = self.map_width + 2 * self.map_margin
        map_ttl_width = self.map_height + 2 * self.map_margin
        if map_ttl_width/width >= map_ttl_height/height:
            resize_factor = map_ttl_width/width
            new_pos[0] = (int(new_pos[0])//resize_factor + self.map_margin//resize_factor)
            new_pos[1] = height - (int(new_pos[1])//resize_factor + self.map_margin//resize_factor + height/2 - map_ttl_height//resize_factor/2)
            new_size[0] = (int(new_size[0])//resize_factor)
            new_size[1] = -(int(new_size[1])//resize_factor)
        else:
            resize_factor = map_ttl_height/height
            new_pos[0] = (int(new_pos[0])//resize_factor + self.map_margin//resize_factor + width/2 - map_ttl_width//resize_factor/2)
            new_pos[1] = height -(int(new_pos[1])//resize_factor + self.map_margin//resize_factor)
            new_size[0] = (int(new_size[0])//resize_factor)
            new_size[1] = -(int(new_size[1])//resize_factor)
        return new_size, new_pos

    def mousePressEvent(self, QMouseEvent):
        """La souris est cliquée"""
        self.mouse_pos = QMouseEvent.localPos()
        self.reverse_mouse_pos(self.mouse_pos)
        if QMouseEvent.button() == Qt.LeftButton:
            pass
        elif QMouseEvent.button() == Qt.RightButton:
            #do what you want here
            pass

    def mouseMoveEvent(self, event):
        """Quand la souris est bougée sur la fenêtre"""
        self.mouse_pos = event.localPos()
        self.reverse_mouse_pos(self.mouse_pos)

    def reverse_mouse_pos(self, qpoint):
        """Calcule la position de la souris relative à la carte"""
        qpoint_x = qpoint.x()
        qpoint_y = qpoint.y()
        new_pos = [qpoint_x, qpoint_y]
        width = self.geometry().width()
        height = self.geometry().height()
        map_ttl_height = self.map_width + 2 * self.map_margin
        map_ttl_width = self.map_height + 2 * self.map_margin
        if map_ttl_width/width >= map_ttl_height/height:
            resize_factor = map_ttl_width/width
            new_pos[0] = (int(new_pos[0]) - self.map_margin//resize_factor)*resize_factor
            new_pos[1] = (int(-new_pos[1] + height) - self.map_margin//resize_factor - height/2 + map_ttl_height//resize_factor/2)*resize_factor
        else:
            resize_factor = map_ttl_height/height
            new_pos[0] = (int(new_pos[0]) - self.map_margin//resize_factor - width/2 + map_ttl_width//resize_factor/2)*resize_factor
            new_pos[1] = (int(-new_pos[1] + height) - self.map_margin//resize_factor)*resize_factor
        print(new_pos)


class RobotItem(): #QGraphicsEllipseItem):
    """The view of a robot in the GraphicsScene"""

    def __init__(self, simu, f):
        """RobotItem constructor, creates the ellipse and adds to the scene"""
        super().__init__(None)
        #self.setZValue(mapview.PLOT_Z_VALUE)

        # instance variables
        #self.robot = r
        # build the ellipse
        width = 5
        #self.setRect(-width, -width, width * 2, width * 2)

        #todo # add tooltip
        #tooltip = r.type.name
        #self.setToolTip(tooltip)


    def controleclicevent(self, event):
        self.controlclic()

    def controlclic(self):
        """controle du robot en cliquant sur la carte """
        destination = []
        #destination=self.buttonDownPos
        #if destination!=robot.getposition:
        #    parent.backend.sendposcmd_robot(self,robot_name,destination)

    def controledragndropevent(self, event):
        self.controldragndrop()

    def controldragndrop(self):
        """controle avec drag and drop"""

    def controleclavierevent(self,event):
        self.controleclavier()

    def controleclavier(self):
        pass
        #shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(text), self)
        #shortcut.activated.connect(slot)
        #add_shortcut('b_up', lambda: ))
        #add_shortcut('b_down', lambda:)
        #add_shortcut('b_left', lambda: )
        #add_shortcut('b_right', lambda: )
        #return toolbar
        #event.accept()

#App = QApplication(sys.argv)
#map_view = MapView(None)
#sys.exit(App.exec())
