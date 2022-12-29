import requests

input_parameters_template = {
    "memory_request": 1,
    "load_request": 10
}

url = "http://localhost:5000"
r = requests.post(url, json=input_parameters_template)
print(r.json())