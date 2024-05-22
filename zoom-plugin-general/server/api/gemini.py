import requests

def generate_summary(transcript):
    api_key = 'your_gemini_api_key'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'prompt': f"Summarize the following meeting transcript:\n\n{transcript}",
        'max_tokens': 500
    }
    response = requests.post('https://api.gemini.com/v1/gpt', headers=headers, json=data)
    return response.json()['summary']
