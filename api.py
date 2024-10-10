from enum import Enum
import os
import time

from flask import Flask, request, jsonify
from pyngrok import ngrok
import requests
import whisper

# Define available Whisper model names
class ModelNames(str, Enum):
    tiny = 'tiny'
    tiny_en = 'tiny.en'
    base = 'base'
    base_en = 'base.en'
    small = 'small'
    small_en = 'small.en'
    medium = 'medium'
    medium_en = 'medium.en'
    large_v1 = 'large-v1'
    large_v2 = 'large-v2'
    large_v3 = 'large-v3'
    large = 'large'
    large_v3_turbo = 'large-v3-turbo'
    turbo = 'turbo'

# Store loaded Whisper models
WhisperModels = {k: None for k in ModelNames.__members__}

def load_model(model_name):
    """Function to load the Whisper model, caching it to avoid reloading."""
    try:
        # Access model value (string) from the enum
        if WhisperModels[model_name] is None:
            print(f"Loading model {model_name}")
            WhisperModels[model_name] = whisper.load_model(ModelNames[model_name].value)
        return WhisperModels[model_name], None, None

    except (RuntimeError, MemoryError) as e:
        # Catch memory-related errors and reset the loaded models
        print(f"Error loading model {model_name}: {e}")
        print("Clearing all models to free up memory.")

        # Clear all loaded models to free up memory
        WhisperModels.clear()
        WhisperModels.update({k: None for k in ModelNames.__members__})

        # Attempt to load the model again after clearing memory
        try:
            print(f"Retrying loading model {model_name}")
            WhisperModels[model_name] = whisper.load_model(ModelNames[model_name].value)
            return WhisperModels[model_name], None, None
        except (RuntimeError, MemoryError) as retry_error:
            # If it fails again, return a message indicating the memory issue
            print(f"Failed to load model {model_name} after memory reset: {retry_error}")
            # raise RuntimeError(f"Unable to load the model '{model_name}' due to insufficient memory.") from retry_error
            return None, jsonify({'error': f"Unable to load the model '{model_name}' due to insufficient memory."}), 500

def handle_file_upload(request):
    # Handle file in form-data (local file upload)
    if 'file' in request.files:
        file_input = request.files['file']
        if file_input.filename == '':
            return None, jsonify({'error': 'No file selected for uploading'}), 400
        file_path = os.path.join('temp_audio', file_input.filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file_input.save(file_path)
        return file_path, None, None

    # Handle JSON-encoded remote URL
    elif 'file' in request.json and isinstance(request.json['file'], str):
        file_input = request.json['file']
        if file_input.startswith('http') or file_input.startswith('https'):
            try:
                response = requests.get(file_input)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                return None, jsonify({'error': f'Failed to download file: {e}'}), 400

            # Save the downloaded file to a temporary location
            file_path = os.path.join('temp_audio', 'remote_audio.mp3')
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return file_path, None, None
        else:
            return None, jsonify({'error': 'Invalid URL provided'}), 400
    else:
        return None, jsonify({'error': 'No valid file or URL provided'}), 400


# Initialize ngrok connection
if __name__ == "__main__":
    tunnel = ngrok.connect("8008")
    print("ngrok connected: ", tunnel.public_url)

    # Initialize Flask app
    app = Flask(__name__, template_folder='.')

    @app.route('/transcribe', methods=['POST'])
    def transcribe():
        # Check if user passed in a model, or default to `tiny`
        if request.is_json and 'model' in request.json:
            model_name = request.json.get('model', 'tiny')
        else:
            model_name = request.form.get('model', 'tiny')

        # Validate that the model is a valid option
        if model_name not in ModelNames.__members__:
            return jsonify({'error': f'Invalid model name provided. Valid models are: {list(ModelNames.__members__.keys())}'}), 400

        # Load the specified or default model
        model, error_response, status_code = load_model(model_name)
        if error_response:
            return error_response, status_code

        # Handle file upload (local or remote) via helper function
        file_path, error_response, status_code = handle_file_upload(request)
        if error_response:
            return error_response, status_code

        # Transcribe the file using the selected model
        start_time = time.time()
        result = model.transcribe(file_path)
        inference_time = time.time() - start_time

        # Remove the temporary file
        os.remove(file_path)

        # Return the transcription
        return jsonify({
            'model_name': model_name,
            'transcript': result['text'],
            'inference_time': inference_time  # Include the timing data in the response
        })

    # Default route
    @app.route('/')
    def initial():
        return '<p>Hello from your Flask Whisper API!</p>'

    # Run the Flask app
    try:
      app.run(port=8008)
    finally:
      ngrok.kill()
      print('ngrok session terminated')