import urllib.request

try:
    resp = urllib.request.urlopen("http://localhost:5000/")
    print(f"Server is up! Status: {resp.status}")
except Exception as e:
    print(f"Server check failed: {e}")
