from enum import Enum
from urllib.parse import urljoin

import requests

# Define available Whisper model names
class ModelNames(str, Enum):
    tiny = 'tiny'
    tiny_en = 'tiny_en'
    base = 'base'
    base_en = 'base_en'
    small = 'small'
    small_en = 'small_en'
    medium = 'medium'
    medium_en = 'medium_en'
    large_v1 = 'large_v1'
    large_v2 = 'large_v2'
    large_v3 = 'large_v3'
    large = 'large'
    large_v3_turbo = 'large_v3_turbo'
    turbo = 'turbo'


class Transcriber:
    def __init__(self, api_url):
        self.api_url = api_url

    @property
    def transcribe_endpoint(self):
        return urljoin(self.api_url, 'transcribe')
    
    def is_remote_url(self, file):
        return isinstance(file, str) and (file.startswith('http') or file.startswith('https'))

    def transcribe(self, file, model=ModelNames.tiny):
        if self.is_remote_url(file):
            return self.transcribe_remote(file, model)
        else:
            return self.transcribe_local(file, model)

    def transcribe_remote(self, url, model):
        json_data = {'file': url, 'model': model}
        response = requests.post(self.transcribe_endpoint, json=json_data)
        response.raise_for_status()
        return response.json()

    def transcribe_local(self, file_path, model):
        with open(file_path, 'rb') as file:
            files = {'file': file}
            data = {'model': model.value}
            response = requests.post(self.transcribe_endpoint, files=files, data=data)
            response.raise_for_status()
            return response.json()

if __name__ == "__main__":
    API_URL = "http://127.0.0.1:8008/"
    # Or your ngrok url when running in colab: https://YOUR-URL.ngrok-free.app/"

    transcriber = Transcriber(API_URL)

    # Remote file example
    remote_result = transcriber.transcribe(
        'https://storage.googleapis.com/aai-web-samples/Custom-Home-Builder.mp3',
        ModelNames.medium)
    print("Remote transcription:", remote_result)

    # Local file example
    local_result = transcriber.transcribe('Custom-Home-Builder.mp3')
    print("Local transcription:", local_result)
