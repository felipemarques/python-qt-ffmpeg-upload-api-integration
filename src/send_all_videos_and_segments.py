import os
import requests
from urllib3.exceptions import InsecureRequestWarning
from tqdm import tqdm
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Desativar apenas o aviso InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Usar variáveis de ambiente
URL_API = os.getenv("URL_API")
USER_TOKEN = os.getenv("USER_TOKEN")
DIRECTORY = os.getenv("DIRECTORY")

def get_token(userToken):
    data = {"token": userToken}
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{URL_API}/users/token/auth", json=data, headers=headers, verify=False, timeout=(10, 300))

    if response.status_code == 200:
        try:
            access_token = response.json().get('token')
            return access_token
        except Exception as e:
            print(f"Error decoding JSON: {e}")
    else:
        print(f"Error obtaining access token. Status: {response.status_code}, Response: {response.text}")

def get_media_video_token(token, description, segments_list, original_file_name):
    """
    Solicita um token específico do vídeo para associar os segmentos enviados.
    """
    headers = {"Authorization": f"Bearer {token}"}

    data = {
        "description": description,
        "segments_list": segments_list,
        "original_file_name": original_file_name
    }
    response = requests.post(f"{URL_API}/media/video-token",json=data, headers=headers, verify=False)
    
    if response.status_code == 200:
        try:
            return response.json().get('token')
        except Exception as e:
            print(f"Error decoding JSON for video token: {e}")
    else:
        print(f"Error obtaining video token. Status: {response.status_code}, Response: {response.text}")
    return None

def send_file(file_path, video_token, token):
    """
    Envia um arquivo de segmento ou o arquivo video_segments.txt para o servidor.
    """
    file_name = os.path.basename(file_path)
    headers = {"Authorization": f"Bearer {token}"}
    files = {'file': (file_name, open(file_path, 'rb'), 'application/octet-stream')}
    data = {
        "video-token": video_token
    }

    response = requests.post(f"{URL_API}/media/multi-upload", files=files, data=data, headers=headers, verify=False)
    
    if response.status_code in [200, 201]:
        print(f"Upload of '{file_name}' completed successfully.")
        print(response.content)
        #os.remove(file_path)
    else:
        print(f"Failed to send '{file_name}'. Status: {response.status_code}, Response: {response.text}")
    
    # Fechar arquivo aberto
    files['file'][1].close()

def send_files(directory_path, token):
    """
    Envia múltiplos arquivos de vídeo e o arquivo .txt com a ordem dos segmentos.
    """
    for root, dirs, files in os.walk(directory_path):
        for dir_name in tqdm(dirs):
            with open(os.path.join(root, dir_name + "/video_segments.txt")) as file:
                segments_list = file.read()
            
            video_dir = os.path.join(root, dir_name)
            video_token = get_media_video_token(token, description=dir_name, segments_list=segments_list, original_file_name=dir_name)

            if video_token:
                for file_name in os.listdir(video_dir):
                    if file_name == "video_segments.txt":
                        continue
                    file_path = os.path.join(video_dir, file_name)
                    send_file(file_path, video_token, token)

if __name__ == "__main__":
    token_access = get_token(USER_TOKEN)
    if token_access:
        print(f"Access token obtained: {token_access}")
        send_files(DIRECTORY, token_access)
    else:
        print("Failed to obtain the access token.")
