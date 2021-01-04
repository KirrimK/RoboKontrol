from PyQt5 import Qwidget
import #todo
import #liste_rect
class Carte(Qwidget):
    def __init__(self, QWidget_parent=None):
        super().__init__(QWidget_parent)

        self.ui =#todo
        self.ui.setupUi(self)
        
class MyButton(QPushButton):
    def __init__(self, label):
        """diriger le robot en cliquant sur la carte"""
        # calls super constuctor
        super(MyButton, self).__init__(label)
        # adds custom logic
        self.setWindowTitle("tp flot d'execution")
        self.setGeometry(300, 300, 250, 150)#todo
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
        print("paintEvent has been triggered")       
        
        
    