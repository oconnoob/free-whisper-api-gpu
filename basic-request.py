import json
import os

import requests

API_URL = "http://127.0.0.1:8008/"
# Or your ngrok url when running in colab: https://YOUR-URL.ngrok-free.app/"
TRANSCRIBE_ENDPOINT = os.path.join(API_URL, "transcribe")

json_data = {'file': "https://storage.googleapis.com/aai-web-samples/Custom-Home-Builder.mp3"}
remote_response = requests.post(TRANSCRIBE_ENDPOINT, json=json_data)

with open('Custom-Home-Builder.mp3', 'rb') as f:
    files = {'file': f}
    local_response = requests.post(TRANSCRIBE_ENDPOINT, files=files, data={'model': 'tiny'})

print("REMOTE JSON:")
print(remote_response.json())
print("\nLOCAL TRANSCRIPT:")
print(local_response.json()['transcript'])

