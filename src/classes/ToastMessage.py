from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import qApp, QVBoxLayout, QLabel, QDialog

class ToastMessage(QDialog):
    def __init__(self, message, duration=2000, parent=None):
        super().__init__(parent)
        self.initUI(message, duration)

    def initUI(self, message, duration):
        self.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setGeometry(500, 500, 300, 50)
        layout = QVBoxLayout()
        messageLabel = QLabel(message, self)
        layout.addWidget(messageLabel)
        self.setLayout(layout)

        # Fechar a janela automaticamente após 'duration' milissegundos
        QTimer.singleShot(duration, self.close)