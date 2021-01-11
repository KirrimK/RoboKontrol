"""Module carte.py - gestion de l'affichage sur la carte"""

from math import sqrt
import lxml.etree as ET

from PyQt5 import QtWidgets #, QtGui
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint
from PyQt5.QtGui import QBrush, QColor, QPainter#, QPen

ROBOT_COLOR = 'green'
SELECT_COLOR = 'red'
ROBOT_BRUSH = QBrush(QColor(ROBOT_COLOR), Qt.SolidPattern)
SELECTED_RB_BRUSH = QBrush(QColor(SELECT_COLOR), Qt.SolidPattern)
ROBOT_SIZE = 200

class MapView(QtWidgets.QWidget):

    """Un widget permettant de visualiser la carte et les robots dessus"""
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.map_data = []
        self.map_width = 10
        self.map_height = 10
        self.map_margin = 0

        self.mouse_pos = QPoint(0, 0)
        self.relative_mspos = [0, 0]
        self.selected_robot = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.repaint)
        self.timer.start(50)

        self.setMouseTracking(True)

        self.show()

    def paintEvent(self, event):
        """Evt appellé à chaque fois que le widget est resize ou caché"""
        self.paint()

    def paint(self):
        """Dessin de la map et des robots"""
        painter = QPainter(self)
        #paint map
        for rect in self.map_data:
            size = rect[3]
            pos = rect[4]
            size, pos = self.calc_pos_size(size, pos)
            painter.setBrush(QBrush(QColor(rect[2]), Qt.SolidPattern))
            painter.drawRect(pos[0], pos[1], size[0], size[1])
        #paint robots
        bkd_robots = self.parent.backend.annu.robots
        for robot in bkd_robots:
            robot_pos = [bkd_robots[robot].x, bkd_robots[robot].y, bkd_robots[robot].theta]
            robot_size = [ROBOT_SIZE, ROBOT_SIZE]
            mrbsize, mrbpos = self.calc_pos_size(robot_size, robot_pos)
            if self.selected_robot == robot:
                painter.setBrush(SELECTED_RB_BRUSH)
            else:
                painter.setBrush(ROBOT_BRUSH)
            pos_offset = [mrbpos[0] - mrbsize[0]/2, mrbpos[1] - mrbsize[1]/2]
            big_offset = [mrbpos[0] - mrbsize[0], mrbpos[1] - mrbsize[1]]
            robot_rect = QRect(pos_offset[0], pos_offset[1], mrbsize[0], mrbsize[1])
            outer_rect = QRect(big_offset[0], big_offset[1], 2*mrbsize[0], 2*mrbsize[1])
            start_angle = (robot_pos[2] - 1) * 16
            span_angle = 2 * 16
            painter.drawPie(outer_rect, start_angle, span_angle)
            painter.drawEllipse(robot_rect)
            painter.drawText(robot_rect, Qt.AlignCenter, robot)
        #paint mouse pos dans un coin
        height = self.geometry().height()
        rlp = self.relative_mspos
        painter.drawText(0, height-20, "x: {} y: {}".format(int(rlp[0]), int(rlp[1])))

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
        except Exception as exc:
            print(exc)

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
            new_pos[1] = height - (int(new_pos[1])//resize_factor +
                         self.map_margin//resize_factor + height/2 -
                         map_ttl_height//resize_factor/2)
            new_size[0] = (int(new_size[0])//resize_factor)
            new_size[1] = -(int(new_size[1])//resize_factor)
        else:
            resize_factor = map_ttl_height/height
            new_pos[0] = (int(new_pos[0])//resize_factor +
                         self.map_margin//resize_factor + width/2 -
                         map_ttl_width//resize_factor/2)
            new_pos[1] = height - (int(new_pos[1])//resize_factor + self.map_margin//resize_factor)
            new_size[0] = (int(new_size[0])//resize_factor)
            new_size[1] = -(int(new_size[1])//resize_factor)
        return new_size, new_pos

    def keyPressEvent(self, event):
        """Une touche du clavier est pressée"""
        if event.key() == Qt.Key_F5:
            pass

    def mousePressEvent(self, event):
        """La souris est cliquée"""
        self.mouse_pos = event.localPos()
        self.relative_mspos = self.reverse_mouse_pos(self.mouse_pos)
        if event.button() == Qt.LeftButton:
            if self.selected_robot is not None:
                cmd_pos = [0, 0, None]
                cmd_pos[0] = self.relative_mspos[0]
                cmd_pos[1] = self.relative_mspos[1]
                self.parent.backend.sendposcmd_robot(self.selected_robot, cmd_pos)
                self.selected_robot = None
        elif event.button() == Qt.RightButton:
            self.selected_robot = None
            for robot in self.parent.backend.annu.robots:
                if self.distance(robot) < ROBOT_SIZE:
                    self.selected_robot = robot

    def distance(self, rb_nm):
        """Calcule la distance entre la souris et un robot"""
        rb_x = self.parent.backend.annu.robots[rb_nm].x
        rb_y = self.parent.backend.annu.robots[rb_nm].y
        dist = sqrt((self.relative_mspos[0] - rb_x)**2 +
                    (self.relative_mspos[1] - rb_y)**2)
        return dist

    def mouseMoveEvent(self, event):
        """Quand la souris est bougée sur la fenêtre"""
        self.mouse_pos = event.localPos()
        self.relative_mspos = self.reverse_mouse_pos(self.mouse_pos)

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
            new_pos[0] = (int(new_pos[0] - 1) - self.map_margin//resize_factor)*resize_factor
            new_pos[1] = (int(-new_pos[1] + height + 2) - self.map_margin//resize_factor -
                         height/2 + map_ttl_height//resize_factor/2)*resize_factor
        else:
            resize_factor = map_ttl_height/height
            new_pos[0] = (int(new_pos[0] - 1) - self.map_margin//resize_factor -
                         width/2 + map_ttl_width//resize_factor/2)*resize_factor
            new_pos[1] = (int(-new_pos[1] + height + 2) -
                         self.map_margin//resize_factor)*resize_factor
        return new_pos


#class RobotItem(): #QGraphicsEllipseItem):
#    """The view of a robot in the GraphicsScene"""

#    def __init__(self, *args):
#        """RobotItem constructor, creates the ellipse and adds to the scene"""
#        super().__init__(None)
#        self.setZValue(mapview.PLOT_Z_VALUE)
#        # build the ellipse
#        width = 5
#        self.setRect(-width, -width, width * 2, width * 2)

        #todo # add tooltip
#        tooltip = r.type.name
#        self.setToolTip(tooltip)


#    def controlclicevent(self, event):
#        self.controlclic()

#    def controlclic(self):
#        """controle du robot en cliquant sur la carte """
#        destination=[]
#        destination=self.buttonDownPos
#        if destination!=robot.getposition:
#            parent.backend.sendposcmd_robot(self,robot_name,destination)

#    def controledragndropevent(self,event):
#        self.controldragndrop()

#    def controldragndrop(self):
#        """controle avec drag and drop"""

#    def controleclavierevent(self,event):
#        self.controleclavier()

#    def controleclavier(self):
#        shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(text), self)
#        shortcut.activated.connect(slot)
        #add_shortcut('b_up', lambda: pass)
        #add_shortcut('b_down', lambda:)
        #add_shortcut('b_left', lambda: )
        #add_shortcut('b_right', lambda: )
        #return toolbar
        #event.accept()
