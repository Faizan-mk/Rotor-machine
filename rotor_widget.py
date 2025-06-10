from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QFont

class RotorWidget(QWidget):
    def __init__(self, rotor, parent=None):
        super().__init__(parent)
        self.rotor = rotor
        self.setFixedSize(100, 300)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor("#444"))
        painter.drawRect(0, 0, self.width(), self.height())
        
        painter.setFont(QFont("Consolas", 14))
        for i in range(26):
            y = (i * 12 + (self.rotor.position % 12))
            c = chr((i + 65) % 256)
            painter.setPen(QColor("white"))
            painter.drawText(40, y + 20, c)

    def mousePressEvent(self, event):
        self.rotor.step()
        self.update()
