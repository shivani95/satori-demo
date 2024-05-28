import os
import requests
import logging
from flask import Flask, request, jsonify, redirect, url_for
from dotenv import load_dotenv
from google.cloud import storage, speech
from server.api.zoom import get_access_token, get_meeting_recording, handle_zoom_event
from server.api.gemini import generate_summary
import urllib.parse

# Load environment variables from .env file

load_dotenv()
print("env variables load completed")

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Debugging step: print all environment variables
for key, value in os.environ.items():
    logger.debug(f"{key}: {value}")

# Set the Google Application Credentials environment variable
google_application_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
if google_application_credentials is None:
    raise EnvironmentError("GOOGLE_APPLICATION_CREDENTIALS not set in environment variables")
else:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_application_credentials

# Initialize Google Cloud clients
storage_client = storage.Client()
speech_client = speech.SpeechClient()

tokens = {}

@app.route('/')
def home():
    return 'Zoom Integration App'

@app.route('/authorize')
def authorize():
    redirect_uri = os.getenv('REDIRECT_URI')
    if redirect_uri is None:
        raise EnvironmentError("REDIRECT_URI not set in environment variables")
    
    # Debugging step: print the redirect URI and its type
    print(f"Redirect URI: {redirect_uri}, Type: {type(redirect_uri)}")
    
    # Ensure redirect_uri is a string before encoding
    if not isinstance(redirect_uri, str):
        raise TypeError("REDIRECT_URI must be a string")
    
    encoded_redirect_uri = urllib.parse.quote(redirect_uri, safe='')
    print(f"Encoded Redirect URI: {encoded_redirect_uri}")
    
    return redirect(f"https://zoom.us/oauth/authorize?response_type=code&client_id={os.getenv('ZOOM_CLIENT_ID')}&redirect_uri={encoded_redirect_uri}")

@app.route('/oauth/callback')
def oauth_callback():
    code = request.args.get('code')
    print("Authorization code received:", code)
    if code:
        try:
            token_response = get_access_token(code)
            access_token = token_response.get('access_token')
            refresh_token = token_response.get('refresh_token')
            tokens['access_token'] = access_token
            tokens['refresh_token'] = refresh_token
            return f"Access Token: {access_token}, Refresh Token: {refresh_token}"
        except requests.exceptions.HTTPError as e:
            print("HTTPError occurred:", e)
            return f"HTTPError occurred: {e}", 400
    return "No code provided", 400

@app.route('/webhook', methods=['POST'])
def webhook():
    print("Webhook received")
    event = request.json
    print(event)

    if 'access_token' not in tokens:
        return redirect(url_for('authorize'))

    recording_url = handle_zoom_event(event, tokens['access_token'])
    if recording_url:
        print(f"Recording URL: {recording_url}")
        transcript = transcribe_recording(recording_url)
        print(f"Transcript: {transcript}")
        summary = generate_summary(transcript)
        print(f"Summary: {summary}")
        return jsonify({'summary': summary})
    return jsonify({'status': 'ignored'}), 200

def transcribe_recording(recording_url):
    bucket = storage_client.bucket('your_bucket_name')
    blob = bucket.blob(f'recordings/{os.path.basename(recording_url)}')
    blob.upload_from_string(requests.get(recording_url).content)
    
    audio = speech.RecognitionAudio(uri=f'gs://your_bucket_name/recordings/{os.path.basename(recording_url)}')
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US"
    )

    operation = speech_client.long_running_recognize(config=config, audio=audio)
    response = operation.result(timeout=600)
    
    if response is None or not hasattr(response, 'results'):
        print("No results found in the response.")
        return ""

    transcript = ''
    for result in response.results:
        transcript += result.alternatives[0].transcript
    return transcript

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)