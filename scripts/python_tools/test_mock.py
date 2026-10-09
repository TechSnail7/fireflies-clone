import requests

try:
    files = {'file': ('test.txt', b'fake data')}
    response = requests.post("http://localhost:8001/api/process-video", files=files)
    print(response.status_code)
    print(response.json())
except Exception as e:
    print(e)
