import urllib.request
import json
import uuid
import os

video_path = r"c:\Projects\fireflies\vidssave.com Finance & Corporate Committee - Zoom Meeting 720P - Trim.mp4"
md_path = r"c:\Projects\fireflies\meeting_transcript.md"

if not os.path.exists(video_path):
    print("File not found!")
else:
    url = 'http://localhost:8001/api/process-video'
    boundary = uuid.uuid4().hex
    headers = {'Content-Type': f'multipart/form-data; boundary={boundary}'}

    with open(video_path, 'rb') as f:
        file_content = f.read()

    data = []
    data.append(f'--{boundary}'.encode('utf-8'))
    data.append(f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(video_path)}"'.encode('utf-8'))
    data.append('Content-Type: video/mp4'.encode('utf-8'))
    data.append(b'')
    data.append(file_content)
    data.append(f'--{boundary}--'.encode('utf-8'))
    data.append(b'')
    
    body = b'\r\n'.join(data)

    req = urllib.request.Request(url, data=body, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=1800) as response:
            result = json.loads(response.read().decode())
            
            with open(md_path, "w", encoding="utf-8") as out:
                out.write(f"# Transcript for {os.path.basename(video_path)}\n\n")
                out.write("## Summary\n")
                out.write(f"{result.get('summary', 'No summary generated.')}\n\n")
                
                out.write("## Transcript\n\n")
                for seg in result.get('transcript', []):
                    out.write(f"**[{seg.get('start')}s - {seg.get('end')}s] {seg.get('speaker')}**: {seg.get('text')}\n\n")
            print("Successfully wrote transcript to MD file.")
    except Exception as e:
        print("Error:", e)
        with open(md_path, "w") as out:
            out.write(f"# Transcription Failed\n\nError: {e}")
