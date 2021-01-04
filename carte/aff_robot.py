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
        qp.drawEllipse(#position du robot)#todo
        qp.end()
        #change la position affichée(a faire)
        root_layout = QtWidgets.QVBoxLayout(self)
        self.scene = QtWidgets.QGraphicsScene()
         
