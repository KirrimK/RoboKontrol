"""Module carte.py - gestion de l'affichage sur la carte"""

#couleurs aleat pour distinguer robots

from math import atan, pi, sqrt
from random import randint
from time import time

from PyQt5 import QtSvg, QtWidgets
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal, QT_VERSION_STR
from PyQt5.QtGui import QBrush, QColor, QPainter, QFont, QPen

ROBOT_COLOR = 'green'
SELECT_COLOR = 'white'
STOPPED_COLOR = 'red'
CLICK_COLOR = 'white'
ROBOT_BRUSH = QBrush(QColor(ROBOT_COLOR), Qt.SolidPattern)
SELECTED_RB_BRUSH = QBrush(QColor(SELECT_COLOR), Qt.SolidPattern)
STOPPED_BRUSH = QBrush(QColor(STOPPED_COLOR), Qt.SolidPattern)
CLICK_BRUSH = QBrush(QColor(CLICK_COLOR), Qt.Dense7Pattern)
ROBOT_SIZE = 200

class MapView(QtWidgets.QWidget):
    """Un widget permettant de visualiser la carte et les robots dessus"""
    # Création d'un signal de sélection du robot sur la map
    selected_robot_signal = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.width = self.geometry().width()
        self.height = self.geometry().height()
        self.svg_data = None
        self.map_height = 2000
        self.map_width = 3000

        self.mouse_pos = QPoint(0, 0)
        self.relative_mspos = [0, 0]
        self.selected_robot = None
        self.mouse_pos_init = QPoint(0, 0)
        self.relative_init_mspos = [0, 0]

        self.clicking = False

        self.color_dict = {}
        self.robot_number = 0
        self.old_pos_dict = {}
        self.old_selected = None
        self.last_repaint = 0

        version = QT_VERSION_STR.split(".")
        self.qt_is_compatible = float(version[0]) >= 5 and float(version[1]) >= 15
        self.svg_scl = False

        self.parent.backend.widget.MapTrigger.connect(self.should_repaint)

        self.setMouseTracking(True)
        self.key_binding={}

        self.selected_robot_signal.connect(lambda rid: self.select_robot(rid))

        self.setFocusPolicy(Qt.StrongFocus)

        self.show()

    def should_repaint(self):
        """Décide si repeindre la map lors d'un MapTrigger est utile
        permet d'économiser de la performance, surtout si le scaling n'est
        pas activé"""
        new_robot_number = len(self.parent.backend.annu.robots.keys())
        should_repaint = False

        #limitation des repaints à 13 par seconde
        try:
            max_period = 1/float(self.parent.settings_dict["Carte (FPS Max)"])
        except Exception as exc:
            print(exc)
            print("Valeur de FPS Max invalide. Mise à 10 FPS par défaut.")
            max_period = 0.1

        if time() - self.last_repaint < max_period:
            should_repaint = False
            return None

        #les robots ont-ils bougé?
        for robot_nm in self.parent.backend.annu.robots:
            robot = self.parent.backend.annu.robots[robot_nm]
            robot_pos = [robot.x, robot.y, robot.theta]
            if self.old_pos_dict.get(robot) is None:
                self.old_pos_dict[robot] = robot_pos
                should_repaint = True
            elif self.old_pos_dict.get(robot_nm) != robot_pos:
                self.old_pos_dict[robot_nm] = robot_pos
                should_repaint = True
        #des robots sont-ils apparus ou ont-ils disparus?
        if new_robot_number != self.robot_number:
            self.robot_number = new_robot_number
            should_repaint = True
        #le robot sélectionné est-il tjrs le même?
        if self.old_selected != self.selected_robot:
            self.old_selected = self.selected_robot
            should_repaint = True
        #un clic glissé est-il réalisé (dessin vecteur)
        if self.clicking:
            should_repaint = True

        if should_repaint:
            self.last_repaint = time()
            self.repaint()

    def paintEvent(self, event):
        """Evt appellé à chaque fois que le widget est resize ou caché"""
        self.paint()

    def select_robot(self, rid):
        """ Le robot associé à rid devient le robot sélectionné"""
        self.selected_robot = rid

    def paint_robots(self, painter):
        """Dessin des robots sur la carte"""
        #paint robots
        bkd_robots = self.parent.backend.annu.robots
        for robot in bkd_robots:
            #attribution de couleurs aléatoires
            if robot not in self.color_dict: #le robot n'a pas de couleur associée
                self.color_dict[robot] = QColor(randint(0, 255), randint(0, 255), randint(0, 255))
            #calcul de la position du robot dans le repère du widget
            robot_pos = [bkd_robots[robot].x, bkd_robots[robot].y, bkd_robots[robot].theta]
            robot_size = [ROBOT_SIZE, ROBOT_SIZE]
            mrbsize, mrbpos = self.calc_pos_size(robot_size, robot_pos[:2])
            #dessin
            if robot == 'C3PO' :
                painter.setBrush(QBrush (QColor('gold'), Qt.SolidPattern))
            else:
                painter.setBrush(QBrush (self.color_dict[robot], Qt.SolidPattern))
            pos_offset = [mrbpos[0] - mrbsize[0]/2, mrbpos[1] - mrbsize[1]/2]
            big_offset = [mrbpos[0] - mrbsize[0], mrbpos[1] - mrbsize[1]]
            robot_rect = QRect(pos_offset[0], pos_offset[1], mrbsize[0], mrbsize[1])
            outer_rect = QRect(big_offset[0], big_offset[1], 2*mrbsize[0], 2*mrbsize[1])
            start_angle = (robot_pos[2] + 3) * 16
            span_angle = 6 * 16
            old_pen = painter.pen()
            if self.selected_robot == robot:
                painter.setPen(QPen(QColor(self.parent.settings_dict["Carte (Couleur Sélection)"]), 4, Qt.SolidLine))
            if bkd_robots[robot].isStopped:
                painter.setPen(QPen(Qt.red, 4, Qt.SolidLine))
            painter.drawPie(outer_rect, start_angle, span_angle)
            painter.drawEllipse(robot_rect)
            painter.setPen(old_pen)
            font = QFont()
            font.setPointSize(8)
            painter.setFont(font)
            painter.drawText(robot_rect, Qt.AlignCenter, robot)

    def paint_map(self, painter):
        """Dessin de la carte"""
        #paint map
        self.svg_data.render(painter)

        #paint map outline (for alignment purposes)
        if self.parent.settings_dict["Carte (Outline)"]:
            maprt_size, maprt_pos = self.calc_pos_size([self.map_width, self.map_height], [0, 0])
            painter.drawRect(QRect(maprt_pos[0], maprt_pos[1], maprt_size[0], maprt_size[1]))

    def paint_vector(self, painter):
        """Dessine la ligne pour les clics-glissés"""
        if self.clicking:
            painter.drawLine(self.mouse_pos_init, self.mouse_pos)

    def paint(self):
        """Dessin de la map et des robots"""
        self.width = self.geometry().width()
        self.height = self.geometry().height()
        painter = QPainter(self)

        self.paint_map(painter)
        self.paint_robots(painter)
        self.paint_vector(painter)

    def updt_map_data(self, config_path, width, height):
        """Mise à jour des objets à dessiner sur la map

        Entrée:
            - config_path (str): le chemin du fichier svg de map
            - height (int): taille de la carte, en mm
            - width (int): taille de la carte, en mm
        """
        self.svg_scl = self.qt_is_compatible and self.parent.settings_dict['Carte (Scaling)']
        self.map_width = width
        self.map_height = height

        self.svg_data = QtSvg.QSvgRenderer(config_path)
        if self.svg_scl:
            self.svg_data.setAspectRatioMode(Qt.KeepAspectRatio)

    def calc_pos_size(self, size, pos):
        """Calcule les positions et tailles en fonction de la taille du widget"""
        new_pos = pos
        new_size = size
        if self.svg_scl: #si le SVG Scaling est activé
            if self.map_width/self.width >= self.map_height/self.height:
                resize_factor = self.map_width/self.width
                new_pos[0] = (int(new_pos[0])//resize_factor)
                new_pos[1] = self.map_height//resize_factor - (int(new_pos[1])//resize_factor -
                            self.height/2 + self.map_height//resize_factor/2)
                new_size[0] = (int(new_size[0])//resize_factor)
                new_size[1] = -(int(new_size[1])//resize_factor)
            else:
                resize_factor = self.map_height/self.height
                new_pos[0] = (int(new_pos[0])//resize_factor +
                            self.width/2 - self.map_width//resize_factor/2)
                new_pos[1] = self.map_height//resize_factor - int(new_pos[1])//resize_factor
                new_size[0] = (int(new_size[0])//resize_factor)
                new_size[1] = -(int(new_size[1])//resize_factor)
        else: #sinon, stretching de base
            resize_fctwdt = self.map_width/self.width
            resize_fcthgt = self.map_height/self.height
            new_pos[0] = (int(new_pos[0])//resize_fctwdt)
            new_pos[1] = self.map_height - (int(new_pos[1])//resize_fcthgt)
            new_size[0] = (int(new_size[0])//resize_fctwdt)
            new_size[1] = -(int(new_size[1])//resize_fcthgt)
        return new_size, new_pos

    def keyPressEvent(self, event):
        """Une touche du clavier est pressée"""
        #self.key_binding={}
        print(event.key())
        self.setFocusPolicy(Qt.StrongFocus)
        bkd_robots = self.parent.backend.annu.robots
        incr=10
        cmd_pos=[0,0,None]
        if self.selected_robot is not None:
            selec_rob = bkd_robots[self.selected_robot]
            robot_pos = [selec_rob.x, selec_rob.y, selec_rob.theta]
            if event.key() == Qt.Key_Z:
                cmd_pos=[robot_pos[0], robot_pos[1] + incr, None]
            if event.key() == Qt.Key_S:
                cmd_pos=[robot_pos[0], robot_pos[1] - incr, None]
            if event.key() == Qt.Key_Q:
                cmd_pos=[robot_pos[0]-incr, robot_pos[1], None]
            if event.key() == Qt.Key_D:
                cmd_pos=[robot_pos[0]+incr, robot_pos[1], None]
            self.parent.backend.sendposcmd_robot(self.selected_robot, cmd_pos)
        else:
            pass

    def mousePressEvent(self, event):
        """La souris est cliquée"""
        self.mouse_pos = event.localPos()
        self.relative_mspos = self.reverse_pos(self.mouse_pos)
        if event.button() == Qt.LeftButton:
            self.mouse_pos_init = event.localPos()
            self.relative_init_mspos = self.reverse_pos(self.mouse_pos)
            self.clicking = True
            #if self.selected_robot is not None:
            #    cmd_pos = [0, 0, None]
            #    cmd_pos[0] = self.relative_mspos[0]
            #    cmd_pos[1] = self.relative_mspos[1]
            #    self.parent.backend.sendposcmd_robot(self.selected_robot, cmd_pos)
            #    cmd_x_le = str(cmd_pos[0])[:4]
            #    cmd_y_le = str(cmd_pos[1])[:4]
            #    qle_poscmd = self.parent.current_robots_dic[self.selected_robot].QLineEdit_positionCommand
            #    qle_poscmd.setText("{} : {} : 000".format(cmd_x_le, cmd_y_le))
        elif event.button() == Qt.RightButton:
            self.selected_robot = None
            for robot in self.parent.backend.annu.robots:
                if self.distance(robot) < ROBOT_SIZE/2:
                    self.selected_robot = robot
                    self.selected_robot_signal.emit(robot)

    def distance(self, rb_nm):
        """Calcule la distance entre la souris et un robot,
        à l'échelle de la carte"""
        rb_x = self.parent.backend.annu.robots[rb_nm].x
        rb_y = self.parent.backend.annu.robots[rb_nm].y
        dist = sqrt((self.relative_mspos[0] - rb_x)**2 +
                    (self.relative_mspos[1] - rb_y)**2)
        return dist

    def mouseReleaseEvent(self, event):
        """Quand la souris est relachée"""
        if self.clicking:
            self.clicking = False
            pos = event.localPos()
            pos_x = pos.x()
            pos_y = pos.y()
            old_pos = self.mouse_pos_init
            opos_x = old_pos.x()
            opos_y = old_pos.y()
            if sqrt((pos_x - opos_x)**2 + (pos_y - opos_y)**2) > 0:
                #le clic n'était pas statique
                try:
                    angle = atan(-(pos_y - opos_y)/(pos_x - opos_x))*360/(2*pi) + (180 if (pos_x - opos_x) < 0 else 0)
                    cmd = [self.relative_init_mspos[0], self.relative_init_mspos[1], angle]
                    self.parent.backend.sendposcmd_robot(self.selected_robot, cmd)
                    qle_poscmd = self.parent.current_robots_dic[self.selected_robot].QLineEdit_positionCommand
                    qle_poscmd.setText("{} : {} : {}".format(int(cmd[0]), int(cmd[1]), int(cmd[2])))
                    print(cmd)
                except Exception as exc:
                    print(exc) #surement une div/zéro ou autre
            else:
                cmd = [self.relative_init_mspos[0], self.relative_init_mspos[1], None]
                self.parent.backend.sendposcmd_robot(self.selected_robot, cmd)
                qle_poscmd = self.parent.current_robots_dic[self.selected_robot].QLineEdit_positionCommand
                qle_poscmd.setText("{} : {} : 000".format(cmd[0], cmd[1]))

    def mouseMoveEvent(self, event):
        """Quand la souris est bougée sur la fenêtre"""
        self.mouse_pos = event.localPos()
        rlp = self.reverse_pos(self.mouse_pos)
        self.relative_mspos = rlp
        #mise à jour du texte de la status bar
        tooltip_str = ''
        for robot in self.parent.backend.annu.robots:
            rb_x = int(self.parent.backend.annu.robots[robot].x)
            rb_y = int(self.parent.backend.annu.robots[robot].y)
            if self.distance(robot) < ROBOT_SIZE/2:
                tooltip_str += "[{} x: {} y: {}] ".format(robot, rb_x, rb_y)
        tooltip_str += 'x: {} y: {}'.format(int(rlp[0]), int(rlp[1]))
        self.parent.statuslabel.setText(tooltip_str)
        #drag and drop (dessin du vecteur sur la carte)
        #if self.selected_robot is not None:
        #    if event.button == Qt.LeftButton:
        #        pos_cmd=[0,0,None]
        #        pos_cmd[0]=pos_cmd[0]+(self.relative_mpos[0]-self.relative_init_mpos[0])
        #        pos_cmd[1]=pos_cmd[1]+self.relative.mpos[1]-self.relative_init_mpos[1]
        #        self.parent.backend.sendposcmd_robot(self.selected_robot, pos_cmd)

    def reverse_pos(self, qpoint):
        """Calcule la position de la souris relative à la carte"""
        qpoint_x = qpoint.x()
        qpoint_y = qpoint.y()
        new_pos = [qpoint_x, qpoint_y]
        if self.svg_scl:
            if self.map_width/self.width >= self.map_height/self.height:
                resize_factor = self.map_width/self.width
                new_pos[0] = (int(new_pos[0] - 1))*resize_factor
                new_pos[1] = (int(- new_pos[1] + self.map_height//resize_factor - 1) + self.height/2 -
                                self.map_height//resize_factor/2)*resize_factor
            else:
                resize_factor = self.map_height/self.height
                new_pos[0] = (int(new_pos[0] - 1) - self.width/2 +
                                self.map_width//resize_factor/2)*resize_factor
                new_pos[1] = (int(-new_pos[1] + self.map_height//resize_factor - 1))*resize_factor
        else:
            resize_fctwdt = self.map_width/self.width
            resize_fcthgt = self.map_height/self.height
            new_pos[0] = new_pos[0]*resize_fctwdt - 2
            new_pos[1] = (-new_pos[1] + self.map_height//resize_fcthgt)*resize_fcthgt - 2
        return new_pos
