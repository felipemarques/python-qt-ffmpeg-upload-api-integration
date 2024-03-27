import os
import requests
import time
from urllib3.exceptions import InsecureRequestWarning
from tqdm import tqdm
import pprint

from PyQt5.QtCore import pyqtSignal
from src.classes.API.MediaManagerAPI import MediaManagerAPI, Result

# Desativar apenas o aviso InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

class UploadVideos:

    def setMediaManagerAPI(self, mediaManagerAPI: MediaManagerAPI):
        self.mediaManagerAPI = mediaManagerAPI

    def setUpdateProgress(self, update_progress: pyqtSignal):
        self.update_progress: pyqtSignal = update_progress

    def setLogOutput(self, logOutput: pyqtSignal):
        self.logOutput: pyqtSignal = logOutput    

    def emitLogOutput(self, text):
        if self.logOutput:
            self.logOutput.emit(text)

    def process(self, directory_path):
        """
        Envia múltiplos arquivos de vídeo e o arquivo .txt com a ordem dos segmentos.
        """
        for root, dirs, files in os.walk(directory_path):
            for dir_name in tqdm(dirs):

                with open(os.path.join(root, dir_name + "/video_segments.txt")) as file:
                    segments_list = file.read()
                
                video_token = self.mediaManagerAPI.get_media_video_token(
                    description=dir_name, 
                    segments_list=segments_list, 
                    original_file_name=dir_name
                )

                video_dir = os.path.join(root, dir_name)

                if video_token:

                    countFiles = len([item for item in os.listdir(video_dir) if os.path.isfile(os.path.join(video_dir, item))])

                    self.update_progress.emit(1)

                    for index, file_name in enumerate(os.listdir(video_dir)):

                        if index == 0:
                            self.emitLogOutput('============================================================')
                            self.emitLogOutput(f'Uploading {file_name} that have {countFiles} segments ...')
                            self.emitLogOutput('============================================================')
                            time.sleep(2)

                        if file_name == "video_segments.txt":
                            continue

                        file_path = os.path.join(video_dir, file_name)
                        result:Result = self.mediaManagerAPI.sendFile(file_path, video_token)

                        percent = round( ((index + 1) * 100) / countFiles)
                        print('percent: ', percent, '%')
                        self.update_progress.emit(percent)
                        
                        self.emitLogOutput(result.message)

                        if result.status == 200:
                            # TODO: REMOVER O COMENTARIO
                            # TODO: REMOVER O COMENTARIO
                            #os.remove(file_path)
                            pass