import requests
import os

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def generate_summary(transcript):
    headers = {
        'Authorization': f'Bearer {GEMINI_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'prompt': f"Summarize the following meeting transcript for two different people, one for the therapist and on for the patient:\n\n{transcript}",
        'max_tokens': 1000
    }
    response = requests.post('https://api.gemini.com/v1/gpt', headers=headers, json=data)
    response.raise_for_status()
    return response.json().get('choices', [{}])[0].get('text', '')

