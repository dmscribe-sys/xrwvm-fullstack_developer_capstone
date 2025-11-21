# server/djangoapp/restapis.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv(
    'backend_url', default="http://localhost:3000")
sentiment_analyzer_url = os.getenv(
    'sentiment_analyzer_url', default="http://localhost:5050")

# Create a get_request helper function to make HTTP GET requests
def get_request(endpoint, **kwargs):
    url = backend_url + endpoint
    params = ""
    if kwargs:
        for key, value in kwargs.items():
            params = params + key + "=" + value + "&"
    request_url = url + "?" + params if params else url
    print(f"GET from {request_url}")
    try:
        response = requests.get(request_url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Network exception occurred: {e}")
        return {}

# Create a analyze_review_sentiments helper function
def analyze_review_sentiments(text):
    request_url = sentiment_analyzer_url + "analyze/" + text
    print(f"Analyzing sentiment from {request_url}")
    try:
        response = requests.get(request_url)
        return response.json()
    except Exception as e:
        print(f"Error calling sentiment analyzer: {e}")
        return {"sentiment": "unknown"}

# Create a post_review helper function
def post_review(data_dict):
    request_url = backend_url + "/insertReview"
    print(f"POST to {request_url}")
    try:
        response = requests.post(request_url, json=data_dict)
        return response.json()
    except Exception as e:
        print(f"Error posting review: {e}")
        return {"status": "error"}