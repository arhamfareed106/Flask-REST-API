import requests
import json
from http import HTTPStatus

BASE = "http://127.0.0.1:5000/"

def test_crud_operations():
    # Test data
    test_videos = [
        {"name": "Flask Tutorial", "views": 100, "likes": 50},
        {"name": "Python Basics", "views": 200, "likes": 75},
        {"name": "REST API Design", "views": 150, "likes": 60}
    ]
    
    # Test CREATE (PUT)
    print("\nTesting CREATE operations:")
    for i, video_data in enumerate(test_videos):
        response = requests.put(f"{BASE}video/{i+1}", json=video_data)
        print(f"Creating video {i+1}:", response.status_code, response.json() if response.text else '')
        
    # Test READ (GET)
    print("\nTesting READ operations:")
    for i in range(len(test_videos)):
        response = requests.get(f"{BASE}video/{i+1}")
        print(f"Reading video {i+1}:", response.status_code, response.json() if response.text else '')
    
    # Test UPDATE (PATCH)
    print("\nTesting UPDATE operations:")
    update_data = {"name": "Updated Video", "views": 500, "likes": 200}
    response = requests.patch(f"{BASE}video/1", json=update_data)
    print("Updating video 1:", response.status_code, response.json() if response.text else '')
    
    # Test DELETE
    print("\nTesting DELETE operations:")
    response = requests.delete(f"{BASE}video/1")
    print("Deleting video 1:", response.status_code, response.text if response.text else 'Success')
    
    # Verify DELETE
    response = requests.get(f"{BASE}video/1")
    print("Verifying deletion:", response.status_code, response.json() if response.text else '')

if __name__ == "__main__":
    try:
        test_crud_operations()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the Flask application is running.")