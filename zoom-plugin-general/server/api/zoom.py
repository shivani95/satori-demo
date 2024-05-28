import requests
import base64
import os
import urllib.parse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ZOOM_CLIENT_ID = os.getenv('ZOOM_CLIENT_ID')
ZOOM_CLIENT_SECRET = os.getenv('ZOOM_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

# Ensure redirect_uri is a string before encoding
if not isinstance(REDIRECT_URI, str):
    raise TypeError("REDIRECT_URI must be a string")

# URL encode the redirect URI
encoded_redirect_uri = urllib.parse.quote(REDIRECT_URI, safe='')
print(f"Encoded Redirect URI: {encoded_redirect_uri}")

def get_access_token(code):
    """
    Exchange authorization code for an access token
    """
    token_url = 'https://zoom.us/oauth/token'
    auth_header = base64.b64encode(f"{ZOOM_CLIENT_ID}:{ZOOM_CLIENT_SECRET}".encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI  # Note: Use the unencoded URI here
    }
    print("Request Headers:", headers)
    print("Request Data:", data)
    response = requests.post(token_url, headers=headers, data=data)
    print("Response status code:", response.status_code)
    print("Response content:", response.content.decode())
    if response.status_code != 200:
        print(f"Error response from Zoom: {response.json()}")
    response.raise_for_status()  # This will raise the HTTPError if the status is 4xx or 5xx
    return response.json()

def get_meeting_recording(meeting_id, access_token):
    """
    Retrieve the recording URL for a specific meeting
    """
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(f'https://api.zoom.us/v2/meetings/{meeting_id}/recordings', headers=headers)
    response.raise_for_status()
    recording_files = response.json().get('recording_files', [])
    for file in recording_files:
        if file['file_type'] == 'MP4':
            return file['download_url']
    return None

def handle_zoom_event(event, access_token):
    """
    Handle Zoom webhook events (e.g., recording completed)
    """
    if event['event'] == 'recording.completed':
        meeting_id = event['payload']['object']['id']
        recording_url = get_meeting_recording(meeting_id, access_token)
        return recording_url
    return None
