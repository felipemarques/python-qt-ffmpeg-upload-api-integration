from PyQt5.QtWidgets import QMessageBox

class Util:

    def showAlert(self, title, message):
        alert = QMessageBox()
        alert.setWindowTitle(title)
        alert.setText(message)
        alert.exec_()