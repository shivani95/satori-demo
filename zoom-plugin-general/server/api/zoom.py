import requests

def handle_zoom_event(event):
    if event['event'] == 'recording.completed':
        meeting_id = event['payload']['object']['id']
        # Further processing or saving event details

def get_meeting_recording(meeting_id):
    access_token = 'your_zoom_access_token'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(f'https://api.zoom.us/v2/meetings/{meeting_id}/recordings', headers=headers)
    recording_files = response.json()['recording_files']
    for file in recording_files:
        if file['file_type'] == 'MP4':
            return file['download_url']
