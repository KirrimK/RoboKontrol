from PyQt5 import Qwidget
import #todo
import #liste_rect
import math 
import Box_robot
class Carte(Qwidget):
    def __init__(self, QWidget_parent=None):
        super().__init__(QWidget_parent)

        self.ui =#todo
        self.ui.setupUi(self)
        
        self.setWindowTitle('controle du robot')#todo
        self.resize(WIDTH, HEIGHT)
        self.show ()
class MyButton(QPushButton):
    def __init__(self, label):
        """diriger le robot en cliquant sur la carte"""
        # calls super constuctor
        super(MyButton, self).__init__(label)
        # adds custom logic
        self.setWindowTitle()
        self.setGeometry(300, 300, 250, 150)#todo #taille totale de la carte
        self.show()

    def paintEvent(self, event):
        """ the slot triggered each time required """
        # calls super paintEvent method
        QPushButton.paintEvent(self, event)
        # adds custom drawing code
        qp = QPainter()
        qp.begin(self)
        qp.setPen(Qt.red)
        qp.drawRect(10, 10, 20, 20)
        qp.end()
     
    def add_carte_items(self):
        #bases
        pen = QPen(QtGui.QColor(#couleur), epaisseur)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        for #base in:
            path = QtGui.QPainterPath()
            path.moveTo(coordonnees_base)
            for xy in base.coords[1:]:
                path.lineTo(xy.x, xy.y)
            item = QtWidgets.QGraphicsPathItem(path, airport_group)
            item.setPen(pen)
            item.setToolTip(nom_base)         
        #robot(s)
        
        
    