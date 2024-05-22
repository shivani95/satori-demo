import os
import requests
from google.cloud import storage, speech
from flask import Flask, request, jsonify
GEMINI_API_KEY='AIzaSyDUl_VA_VHc7tQ38D7O8kzLstASc-N_AJE'
ZOOM_API_KEY='PWUduPaDSyy7LmF8GxDQHA'

app = Flask(__name__)

# Set up Google Cloud Storage and Speech-to-Text clients
storage_client = storage.Client()
speech_client = speech.SpeechClient()

# Load environment variables
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/shivanipatel/Satori-Demo-with-VertexAI/credentials/satori-ai-demo-571aba22c2f4.json"
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
ZOOM_API_KEY = os.environ.get('ZOOM_API_KEY')

@app.route('/webhook', methods=['POST'])
def webhook():
    event = request.json
    if event['event'] == 'recording.completed':
        meeting_id = event['payload']['object']['id']
        recording_url = get_meeting_recording(meeting_id)
        transcript = transcribe_recording(recording_url)
        summary = generate_summary(transcript)
        return jsonify({'summary': summary})
    return jsonify({'status': 'ignored'}), 200

def get_meeting_recording(meeting_id):
    headers = {
        'Authorization': f'Bearer {ZOOM_API_KEY}'
    }
    response = requests.get(f'https://api.zoom.us/v2/meetings/{meeting_id}/recordings', headers=headers)
    recording_files = response.json().get('recording_files', [])
    for file in recording_files:
        if file['file_type'] == 'MP4':
            return file['download_url']
    return None

def transcribe_recording(recording_url):
    # Download the recording file to Google Cloud Storage
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

    transcript = ''
    for result in response.results:
        transcript += result.alternatives[0].transcript
    return transcript

def generate_summary(transcript):
    headers = {
        'Authorization': f'Bearer {GEMINI_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'prompt': f"Summarize the following meeting transcript:\n\n{transcript}",
        'max_tokens': 500
    }
    response = requests.post('https://api.gemini.com/v1/gpt', headers=headers, json=data)
    return response.json().get('choices', [{}])[0].get('text', '')

if __name__ == '__main__':
    app.run(debug=True)
