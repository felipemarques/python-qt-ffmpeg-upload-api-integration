import os
import requests
import re
import time
from urllib3.exceptions import InsecureRequestWarning
from tqdm import tqdm
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Desativar apenas o aviso InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Usar variáveis de ambiente
url_api = os.getenv("URL_API")
url_auth = url_api + "/users/token/auth"
userToken = os.getenv("USER_TOKEN")
directory = os.getenv("DIRECTORY")

def get_token(userToken):
    data = {"token": userToken}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url_auth, json=data, headers=headers, verify=False)

    if response.status_code == 200:
        try:
            access_token = response.json().get('token')
            return access_token
        except Exception as e:
            print(f"Error decoding JSON: {e}")
    else:
        print(f"Error obtaining access token. Status: {response.status_code}, Response: {response.text}")

def send_file(filePath, token):
    headers = {"Authorization": "Bearer " + token}

    with open(filePath, 'rb') as file:

        file_name = os.path.basename(filePath)
        title_description = re.sub(r'[-_]', ' ', re.sub(r'\.\w+$', '', file_name))
        files = {'file': (file_name, file, 'application/octet-stream')}
        data = {
            'title': title_description,
            'description': title_description,
        }

        print(f"Sending file {file_name} ... ")

        response = requests.post(url_api + "/media/upload", files=files, data=data, headers=headers, verify=False)
        
        if response.status_code in [200, 201]:
            print(f"Upload of file {file_name} completed successfully.")
        else:
            print(f"Failed to send {file_name}. Status: {response.status_code}, Response: {response.text}")

token_access = get_token(userToken)
if token_access:
    print(f"Access token obtained: {token_access}")
    for file in os.listdir(directory):
        full_path = os.path.join(directory, file)
        if os.path.isfile(full_path):
            send_file(full_path, token_access)
            # Aguarda 15 segundos antes de enviar o proximo arquivo
            time.sleep(15)
else:
    print("Failed to obtain the access token.")
