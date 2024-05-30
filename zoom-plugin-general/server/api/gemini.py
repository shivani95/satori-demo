import os
import requests
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2 import service_account

# Load environment variables
load_dotenv()

GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# Load the service account credentials and specify the required scopes
scopes = ['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/generative-language']
credentials = service_account.Credentials.from_service_account_file(
    GOOGLE_APPLICATION_CREDENTIALS, scopes=scopes
)

def generate_summary(transcript):
    # Obtain access token
    auth_request = Request()
    credentials.refresh(auth_request)
    access_token = credentials.token
    
    # Define the endpoint and headers
    endpoint = "https://generativelanguage.googleapis.com/v1beta2/models/text-bison-001:generateText"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Define the request payload
    data = {
        'prompt': {
            'text': f"Summarize the following meeting transcript for two different people, one for the therapist and one for the patient:\n\n{transcript}"
        },
        'temperature': 0.7,
        'candidateCount': 1,
        'maxOutputTokens': 1000,
        'topP': 1.0,
        'topK': 40
    }
    
    # Make the request
    response = requests.post(endpoint, headers=headers, json=data)
    response.raise_for_status()
    
    # Parse the response
    response_json = response.json()
    return response_json.get('candidates', [{}])[0].get('output', '')
