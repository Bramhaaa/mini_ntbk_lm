import requests

API_KEY = "AIzaSyBFNK4aKhzc6QiAsUFYS97PbypGPdBQHFs"

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
resp = requests.get(url)
resp.raise_for_status()
data = resp.json()

for m in data.get("models", []):
    print("Model name:", m.get("name"))
    print("  Description / metadata:", m)
    print()
