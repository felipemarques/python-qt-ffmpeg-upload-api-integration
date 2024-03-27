import os
import sys

from dotenv import load_dotenv
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QApplication, QDialog, QFileDialog)

class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.loadSettings()

    def initUI(self):
        self.setWindowTitle('Configurações')
        self.layout = QVBoxLayout()

        # Campo para URL da API
        self.layout.addWidget(QLabel('URL da API:'))
        self.api_url_edit = QLineEdit(self)
        self.layout.addWidget(self.api_url_edit)

        # Campo para User Token
        self.layout.addWidget(QLabel('User Token:'))
        self.user_token_edit = QLineEdit(self)
        self.layout.addWidget(self.user_token_edit)

        # Campo para Directory
        self.layout.addWidget(QLabel('Directory:'))
        self.directory_edit = QLineEdit(self)
        self.layout.addWidget(self.directory_edit)

        # Select directory
        self.button = QPushButton('Selecionar Diretório', self)
        self.button.clicked.connect(self.openDirectoryDialog)
        self.layout.addWidget(self.button)

        # Botões Salvar e Cancelar
        self.save_button = QPushButton('Salvar')
        self.save_button.clicked.connect(self.saveSettings)
        self.cancel_button = QPushButton('Cancelar')
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        self.layout.addLayout(buttons_layout)
        
        self.setLayout(self.layout)

    def openDirectoryDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        directory = QFileDialog.getExistingDirectory(self, "Selecionar Diretório", "", options=options)
        if directory:
            self.directory_edit.setText(directory)

    def loadSettings(self):
        self.api_url_edit.setText(os.getenv('URL_API', ''))
        self.user_token_edit.setText(os.getenv('USER_TOKEN', ''))
        self.directory_edit.setText(os.getenv('DIRECTORY', ''))

    def saveSettings(self):
        with open('.env', 'w') as f:
            f.write(f'URL_API={self.api_url_edit.text()}\n')
            f.write(f'USER_TOKEN={self.user_token_edit.text()}\n')
            f.write(f'DIRECTORY={self.directory_edit.text()}\n')
        self.accept()


def main():
    load_dotenv()

    app = QApplication(sys.argv)
    settingsDialog = SettingsDialog()
    settingsDialog.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
