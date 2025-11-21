import requests

url = "http://127.0.0.1:5000/chat"

payload = {
    "message": "Hello, how are you?",
    "language": "tamil"
}

response = requests.post(url, json=payload)
print(response.json())
