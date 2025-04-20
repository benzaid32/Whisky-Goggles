import requests
import sys
import os
import base64
import time
import json
from PIL import Image

def test_identify(api_url, image_path):
    """
    Test the image identification endpoint with a file upload.
    
    Args:
        api_url: Base URL of the API
        image_path: Path to test image
    """
    print(f"\nTesting /api/identify with {image_path}")
    
    # Prepare file for upload
    files = {
        'file': open(image_path, 'rb')
    }
    
    # Send request
    start_time = time.time()
    response = requests.post(f"{api_url}/api/identify", files=files)
    elapsed = time.time() - start_time
    
    # Process response
    if response.status_code == 200:
        result = response.json()
        print(f"Success! API responded in {elapsed:.3f} seconds.")
        print(f"Processing time reported by API: {result.get('processing_time_ms', 0)/1000:.3f} seconds")
        print("\nTop matches:")
        for i, match in enumerate(result.get('matches', [])):
            print(f"  {i+1}. {match.get('name')} - {match.get('confidence')*100:.1f}% confidence")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def test_identify_base64(api_url, image_path):
    """
    Test the base64 image identification endpoint.
    
    Args:
        api_url: Base URL of the API
        image_path: Path to test image
    """
    print(f"\nTesting /api/identify_base64 with {image_path}")
    
    # Read image and convert to base64
    with open(image_path, 'rb') as img_file:
        b64_string = base64.b64encode(img_file.read()).decode('utf-8')
    
    # Send request
    start_time = time.time()
    response = requests.post(
        f"{api_url}/api/identify_base64", 
        json={'base64_image': b64_string}
    )
    elapsed = time.time() - start_time
    
    # Process response
    if response.status_code == 200:
        result = response.json()
        print(f"Success! API responded in {elapsed:.3f} seconds.")
        print(f"Processing time reported by API: {result.get('processing_time_ms', 0)/1000:.3f} seconds")
        print("\nTop matches:")
        for i, match in enumerate(result.get('matches', [])):
            print(f"  {i+1}. {match.get('name')} - {match.get('confidence')*100:.1f}% confidence")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def test_list_bottles(api_url):
    """Test the endpoint to list all bottles."""
    print("\nTesting /api/bottles")
    response = requests.get(f"{api_url}/api/bottles")
    
    if response.status_code == 200:
        bottles = response.json()
        print(f"Success! Found {len(bottles)} bottles in database.")
        print(f"First 5 bottles:")
        for i, bottle in enumerate(bottles[:5]):
            print(f"  {i+1}. {bottle.get('name')}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def main():
    """Run API tests."""
    if len(sys.argv) < 2:
        print("Usage: python test_api.py <image_path> [api_url]")
        print("Example: python test_api.py path/to/bottle.jpg http://localhost:8000")
        sys.exit(1)
    
    image_path = sys.argv[1]
    api_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"
    
    # Validate image path
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        sys.exit(1)
    
    # Run tests
    test_identify(api_url, image_path)
    test_identify_base64(api_url, image_path)
    test_list_bottles(api_url)

if __name__ == "__main__":
    main() 