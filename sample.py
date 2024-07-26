from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)


WINDOW_SIZE = 10
BASE_URL = "http://20.244.56.144/test"
ENDPOINTS = {
    "p": f"{BASE_URL}/primes",
    "f": f"{BASE_URL}/fibonacci",
    "e": f"{BASE_URL}/even",
    "r": f"{BASE_URL}/random"
}


window = []
client_id = None
client_secret = None
access_token = None

def register_company():
    global client_id, client_secret
    data = {
        "companyName": "goMart",
        "ownerName": "Rahul",
        "rollNo": "1",
        "ownerEmail": "rahul@abc.edu",
        "accessCode": "ZngVRi"
    }
    try:
        response = requests.post(f"{BASE_URL}/register", json=data, timeout=0.5)
        if response.status_code == 200:
            response_data = response.json()
            client_id = response_data.get('clientID')
            client_secret = response_data.get('clientSecret')
            return True
        return False
    except requests.RequestException:
        return False

def get_access_token():
    global access_token
    data = {
        "companyName": "goMart",
        "clientID": client_id,
        "clientSecret": client_secret,
        "ownerName": "Rahul"
    }
    try:
        response = requests.post(f"{BASE_URL}/auth", json=data, timeout=0.5)
        if response.status_code == 200:
            response_data = response.json()
            access_token = response_data.get('access_token')
            return True
        return False
    except requests.RequestException:
        return False

def fetch_numbers(number_type):
    if not access_token:
        return []
    url = ENDPOINTS.get(number_type)
    if not url:
        return []
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    try:
        start_time = time.time()
        response = requests.get(url, headers=headers, timeout=0.5)
        elapsed_time = time.time() - start_time
        if elapsed_time > 0.5 or response.status_code != 200:
            return []
        numbers = response.json().get('numbers', [])
        return list(set(numbers))  # Remove duplicates
    except requests.RequestException:
        return []

@app.route('/numbers/<number_type>', methods=['GET'])
def get_numbers(number_type):
    if number_type not in ENDPOINTS:
        return jsonify({"error": "Invalid number type"}), 400

    if not client_id or not client_secret:
        if not register_company():
            return jsonify({"error": "Registration failed"}), 500

    if not access_token:
        if not get_access_token():
            return jsonify({"error": "Authorization failed"}), 500

    numbers = fetch_numbers(number_type)
    if not numbers:
        return jsonify({"error": "Failed to fetch numbers"}), 500

    window_prev_state = list(window)
    for number in numbers:
        if number not in window:
            if len(window) >= WINDOW_SIZE:
                window.pop(0)
            window.append(number)

    window_curr_state = list(window)
    avg = sum(window_curr_state) / len(window_curr_state) if window_curr_state else 0

    return jsonify({
        "numbers": numbers,
        "windowPrevState": window_prev_state,
        "windowCurrState": window_curr_state,
        "avg": round(avg, 2)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9876)
