import requests

new_meeting = {
    "title": "Test Upload",
    "date": "2026-10-09T00:00:00Z",
    "duration_seconds": 1800,
    "host": "You",
    "participants": ["You", "AI Assistant"],
    "status": "completed",
    "meeting_type": "video",
    "tags": ["Uploaded"],
    "transcript_segments": [
        {"speaker": "You", "text": "Test", "start_time": 0, "end_time": 5},
        {"speaker": "AI", "text": "Test 2", "start_time": 6, "end_time": 10}
    ],
    "summary": {
        "overview": "Overview",
        "key_topics": [{"title": "T", "description": "D"}],
        "chapters": [{"title": "C", "start_time": 0, "end_time": 10, "summary": "S"}],
        "outline": [{"heading": "H", "points": ["P"]}]
    },
    "action_items": [
        {"text": "Review", "assignee": "You", "is_completed": False, "due_date": None}
    ]
}

response = requests.post("http://localhost:8000/api/meetings", json=new_meeting)
print(response.status_code)
print(response.text)
