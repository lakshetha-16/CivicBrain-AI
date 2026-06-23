import requests

url = "http://127.0.0.1:5000/analyze"

data = {
    "text": "Street light not working in my area"
}

response = requests.post(url, json=data)

print(response.json())