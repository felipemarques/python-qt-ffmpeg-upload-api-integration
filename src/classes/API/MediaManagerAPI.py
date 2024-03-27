import requests
import os
from dataclasses import dataclass

@dataclass
class Result:
    status: int
    message: str
    file_name: str

class MediaManagerAPI:

    def __init__(self):
        self.URL_API = None
        self.USER_TOKEN = None
        self.ACCESS_TOKEN = None

    def setBaseEndpoint(self, URL_API):
        self.URL_API = URL_API
    
    def setUserToken(self, user_token):
        self.USER_TOKEN = user_token

    def get_token(self):
        if self.ACCESS_TOKEN:
            return self.ACCESS_TOKEN
        
        data = {"token": self.USER_TOKEN}
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{self.URL_API}/users/token/auth", json=data, headers=headers, verify=False, timeout=(10, 300))

        if response.status_code == 200:
            try:
                access_token = response.json().get('token')
                self.ACCESS_TOKEN = access_token
                return access_token
            except Exception as e:
                print(f"Error decoding JSON: {e}")
        else:
            print(f"Error obtaining access token. Status: {response.status_code}, Response: {response.text}")

    def get_media_video_token(self, description, segments_list, original_file_name):
        """
        Solicita um token específico do vídeo para associar os segmentos enviados.
        """
        token = self.get_token()
        headers = {"Authorization": f"Bearer {token}"}

        data = {
            "description": description,
            "segments_list": segments_list,
            "original_file_name": original_file_name
        }
        response = requests.post(f"{self.URL_API}/media/video-token",json=data, headers=headers, verify=False)
        
        if response.status_code == 200:
            try:
                return response.json().get('token')
            except Exception as e:
                print(f"Error decoding JSON for video token: {e}")
        else:
            print(f"Error obtaining video token. Status: {response.status_code}, Response: {response.text}")
        return None
    
    def sendFile(self, file_path, video_token) -> Result:
        """
        Envia um arquivo de segmento ou o arquivo video_segments.txt para o servidor.
        """
        result = None
        token = self.get_token()
        file_name = os.path.basename(file_path)
        headers = {"Authorization": f"Bearer {token}"}
        files = {'file': (file_name, open(file_path, 'rb'), 'application/octet-stream')}
        data = {
            "video-token": video_token
        }

        response = requests.post(f"{self.URL_API}/media/multi-upload", files=files, data=data, headers=headers, verify=False)
        
        if response.status_code in [200, 201]:
            print(f"Upload of '{file_name}' completed successfully.")
            #print(response.content)

            result = Result(
                status = response.status_code,
                message = f"Upload of '{file_name}' completed successfully.",
                file_name = file_name
            )
        else:
            print(f"Failed to send '{file_name}'. Status: {response.status_code}, Response: {response.text}")

            result = Result(
                status = response.status_code,
                message = f"Failed to upload '{file_name}'.",
                file_name = file_name
            )
        
        files['file'][1].close()    

        return result