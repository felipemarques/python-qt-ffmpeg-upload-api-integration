from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLabel, QDialog
from PyQt5.QtGui import QPixmap

from dotenv import load_dotenv
from datetime import datetime

class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Sobre')
        self.setGeometry(300, 300, 400, 300)
        layout = QVBoxLayout()

        imageLabel = QLabel(self)
        pixmap = QPixmap('logo-mm.png')
        scaledPixmap = pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        imageLabel.setPixmap(scaledPixmap)
        layout.addWidget(imageLabel)

        currentYear = datetime.now().year

        # Adiciona texto de copyright e ajuda
        layout.addWidget(QLabel('Informações de ajuda e suporte aqui.'))
        layout.addWidget(QLabel('Para mais informações, visite nosso site: https://mmtec.site'))
        layout.addWidget(QLabel(f'© 2020-{currentYear} MM Tecnologia de Informação LTDA. Todos os direitos reservados.', self))

        # Adiciona um botão de Ok para fechar o diálogo
        okButton = QPushButton('Ok', self)
        okButton.clicked.connect(self.accept)
        layout.addWidget(okButton)

        self.setLayout(layout)