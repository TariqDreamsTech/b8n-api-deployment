import requests
import json

# API endpoint
API_URL = "http://localhost:5000/scrape"

# Headers
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


def test_scrape_api():
    print("\n🧪 Testing: Scrape with password")

    try:
        # Send POST request with password
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json={"password": "0724"},  # Replace with your actual password
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")

    print("-" * 50)


if __name__ == "__main__":
    test_scrape_api()
