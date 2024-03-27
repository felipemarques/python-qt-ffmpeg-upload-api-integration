import sys
import time
import os

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import qApp, QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSystemTrayIcon, QMenu, QProgressBar, QAction, QTextEdit
from PyQt5.QtGui import QIcon

from dotenv import load_dotenv

# import classes
from app_settings import SettingsDialog
from src.classes.AboutDialog import AboutDialog
from src.classes.Util import Util
from src.classes.ToastMessage import ToastMessage
from src.classes.API.MediaManagerAPI import MediaManagerAPI
from src.UploadVideos import UploadVideos

# Importações dos scripts
# TODO: faze rum refactor aqui
from src.split_videos_directory_ffmpeg import process_directory as split_videos
#from src.send_all_videos_and_segments import send_files

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Usar variáveis de ambiente
URL_API = os.getenv("URL_API")
USER_TOKEN = os.getenv("USER_TOKEN")
DIRECTORY = os.getenv("DIRECTORY")

mediaManagerAPI = MediaManagerAPI()
mediaManagerAPI.setBaseEndpoint(URL_API)
mediaManagerAPI.setUserToken(USER_TOKEN)

class SendAllVideosAndSegmentsTaskThread(QThread):
    
    update_progress = pyqtSignal(int)
    logOutput = pyqtSignal(str)

    def run(self):
        upload = UploadVideos()
        upload.setMediaManagerAPI(mediaManagerAPI)
        upload.setUpdateProgress(self.update_progress)
        upload.setLogOutput(self.logOutput)
        upload.process(DIRECTORY)


class SplitVideosTaskThread(QThread):
    update_progress = pyqtSignal(int)
    logOutput = pyqtSignal(str)

    def run(self):
        split_videos(DIRECTORY, 30, self.update_progress, self.logOutput)        

# TODO: remover este metodo fake
class TaskThread(QThread):
    update_progress = pyqtSignal(int)

    def run(self):
        for i in range(101):
            self.update_progress.emit(i)  # Atualiza a barra de progresso
            time.sleep(0.1)  # Simula uma tarefa de longa duração

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        self.setWindowTitle('MM Sync Videos with Media Manager')
        self.setGeometry(300, 300, 500, 300)
        self.setWindowIcon(QIcon('icon.png'))

        # Configura o widget central e o layout
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout(self.centralWidget)

        self.progressBar = QProgressBar(self)
        self.progressBar.hide()
        self.layout.addWidget(self.progressBar)

        self.progressBar2 = QProgressBar(self)
        self.progressBar2.setMinimum(0)
        self.progressBar2.setMaximum(0)
        self.progressBar2.hide()
        self.layout.addWidget(self.progressBar2)

        self.logOutput = QTextEdit(self)
        self.logOutput.setText('Log outputs will shown here...')
        self.logOutput.setReadOnly(True)  # Torna o QTextEdit somente leitura
        self.layout.addWidget(self.logOutput)

        # Configura o botão "Split videos"
        self.buttonSplitVideos = QPushButton('Split Videos')
        self.buttonSplitVideos.clicked.connect(lambda: self.on_click_split_videos())
        self.layout.addWidget(self.buttonSplitVideos)

        # Configura o botão "Send All Videos and Segments"
        self.buttonSendAll = QPushButton('Send All Videos and Segments')
        self.buttonSendAll.clicked.connect(lambda: self.on_click_send_all_videos_segments())
        self.layout.addWidget(self.buttonSendAll)

        self.showMenuBar()

        toast = ToastMessage("Não se esqueça de checar as configurações e variáveis de ambiente.", 3000, self)
        toast.show()

    # TODO: remove here
    def startLongTask(self):
        self.progressBar.show()

        def toast(self):
            Util.showAlert(self, "Conclusão da Tarefa", "A tarefa de dividir vídeos foi completada com sucesso.")

            toast = ToastMessage("A tarefa de dividir vídeos foi completada.", 3000, self)
            toast.show()

        self.thread = TaskThread()
        self.thread.update_progress.connect(self.progressBar.setValue)
        self.thread.finished.connect(lambda: toast(self))
        self.thread.start()

    def on_click_split_videos(self):
        print('Split Videos clicado')
        
        self.buttonSplitVideos.setEnabled(False)

        self.progressBar.hide()
        self.progressBar2.show()
        
        self.thread = SplitVideosTaskThread()
        self.thread.update_progress.connect(self.progressBar.setValue)
        self.thread.logOutput.connect(self.logOutput.append)
        self.thread.finished.connect(self.split_videos_thread_completed)
        self.thread.start()

    def split_videos_thread_completed(self):
        Util.showAlert(self, "Conclusão da Tarefa", "A tarefa de dividir vídeos foi completada com sucesso.")
        toast = ToastMessage("A tarefa de dividir vídeos foi completada.", 3000, self)
        toast.show()
        self.progressBar2.hide()            
        self.buttonSplitVideos.setEnabled(True)

    def send_all_videos_segments_thread_completed(self):
        Util.showAlert(self, "Conclusão da Tarefa", "A tarefa de enviar os videos e segmentos foi completada com sucesso.")
        
        self.progressBar.hide()
        self.progressBar2.hide()    
        self.buttonSendAll.setEnabled(True)

    def on_click_send_all_videos_segments(self):
        print('Send All Videos and Segments clicado')
        self.progressBar.show()
        self.progressBar2.show()
        
        self.buttonSendAll.setEnabled(False)

        self.thread = SendAllVideosAndSegmentsTaskThread()
        self.thread.update_progress.connect(self.progressBar.setValue)
        self.thread.logOutput.connect(self.logOutput.append)
        self.thread.finished.connect(self.send_all_videos_segments_thread_completed)
        self.thread.start()        

    def showMenuBar(self):
        # Cria uma barra de menu
        menubar = self.menuBar()
        
        # Cria menus na barra de menu
        menuBarItem = menubar.addMenu('Menu')
        helpMenu = menubar.addMenu('Ajuda')
        
        # Cria ações para o menu 'Settings'
        settingsAction = QAction('Configurações', self)
        settingsAction.setShortcut('Ctrl+P')
        settingsAction.setStatusTip('Configurações')
        settingsAction.triggered.connect(openSettingsDialog)

        # Cria ações para o menu 'Arquivo'
        exitAction = QAction('Sair', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Sair da aplicação')
        exitAction.triggered.connect(qApp.quit)

        menuBarItem.addAction(settingsAction)
        menuBarItem.addAction(exitAction)

        # Cria ações para o menu 'Ajuda'
        aboutAction = QAction('Sobre', self)
        aboutAction.setStatusTip('Mostrar informações sobre a aplicação')
        aboutAction.triggered.connect(self.showAboutDialog)
        
        helpMenu.addAction(aboutAction)        

    def showAboutDialog(self):
       dialog = AboutDialog()
       dialog.exec_()

def openSettingsDialog(self):
    dialog = SettingsDialog()
    dialog.exec_()

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('icon.png'))
    window = MainWindow()

    # Configura o ícone da bandeja
    trayIcon = QSystemTrayIcon(QIcon('icon.png'), app)
    trayIcon.setToolTip('Clique para abrir a aplicação')

    # Configura o menu da bandeja
    menu = QMenu()
    
    openAction = menu.addAction('Abrir')
    openAction.triggered.connect(window.show)
    
    settingsAction = menu.addAction('Settings')
    settingsAction.triggered.connect(openSettingsDialog)

    exitAction = menu.addAction('Sair')
    exitAction.triggered.connect(app.quit)
    
    trayIcon.setContextMenu(menu)
    trayIcon.show()

    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
