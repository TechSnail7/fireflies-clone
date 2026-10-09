import urllib.request
import json
import uuid

url = 'http://localhost:8001/api/process-video'
boundary = uuid.uuid4().hex
headers = {'Content-Type': f'multipart/form-data; boundary={boundary}'}

data = []
data.append(f'--{boundary}')
data.append('Content-Disposition: form-data; name="file"; filename="test.txt"')
data.append('Content-Type: text/plain')
data.append('')
data.append('fake data')
data.append(f'--{boundary}--')
data.append('')
body = '\r\n'.join(data).encode('utf-8')

req = urllib.request.Request(url, data=body, headers=headers, method='POST')
try:
    with urllib.request.urlopen(req, timeout=5) as response:
        print(response.status)
        print(response.read().decode())
except Exception as e:
    print("Error:", e)
