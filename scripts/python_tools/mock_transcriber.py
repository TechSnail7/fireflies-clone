from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

import traceback
import datetime

def log_debug(msg):
    with open("mock_transcriber_debug.log", "a") as f:
        f.write(f"[{datetime.datetime.now()}] {msg}\n")

from fastapi import Request

@app.post("/api/process-video")
async def process_video(request: Request, file: UploadFile = File(...)):
    cl = request.headers.get("Content-Length")
    log_debug(f"Incoming request Content-Length: {cl}")
    log_debug(f"Processing uploaded video: {file.filename}")
    
    # Use a secure random name for the temporary file to avoid path issues
    import uuid
    import shutil
    
    safe_ext = file.filename.split('.')[-1] if '.' in file.filename else 'mp4'
    temp_video_path = f"temp_{uuid.uuid4().hex}.{safe_ext}"
    
    try:
        await file.seek(0)
        data = await file.read()
        log_debug(f"Read {len(data)} bytes using await file.read()")
        
        # Save the uploaded file to the backend uploads directory so it can be served
        backend_uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "uploads")
        os.makedirs(backend_uploads_dir, exist_ok=True)
        final_video_path = os.path.join(backend_uploads_dir, temp_video_path)
        
        with open(final_video_path, "wb") as buffer:
            buffer.write(data)
            
        file_size = os.path.getsize(final_video_path)
        log_debug(f"Saved file to {final_video_path}, size: {file_size} bytes")
        
        if file_size == 0:
            raise ValueError(f"Uploaded file is 0 bytes! Request Content-Length was {cl}. This means the file was empty on the client side.")
            
        from fastapi.concurrency import run_in_threadpool
        
        def run_aai():
            import assemblyai as aai
            aai.settings.api_key = "1189d26771a14b71875662d7b37ae5f3"
            transcriber = aai.Transcriber()
            config = aai.TranscriptionConfig(
                speaker_labels=True,
                summarization=True,
                summary_model=aai.SummarizationModel.informative,
                summary_type=aai.SummarizationType.bullets
            )
            return transcriber.transcribe(final_video_path, config)

        log_debug("Starting AssemblyAI transcription...")
        transcript = await run_in_threadpool(run_aai)
        
        if transcript.error:
            raise ValueError(f"AssemblyAI Error: {transcript.error}")
            
        transcript_segments = []
        if transcript.utterances:
            for utterance in transcript.utterances:
                transcript_segments.append({
                    "speaker": f"Speaker {utterance.speaker}",
                    "text": utterance.text,
                    "start": utterance.start / 1000.0,
                    "end": utterance.end / 1000.0
                })
        elif transcript.text:
            transcript_segments.append({
                "speaker": "Speaker A",
                "text": transcript.text,
                "start": 0,
                "end": transcript.audio_duration if transcript.audio_duration else 0
            })
            
        summary_text = transcript.summary if transcript.summary else "Transcription completed successfully."
        
        # Do not remove the video file, we need it for playback
        # if os.path.exists(temp_video_path): os.remove(temp_video_path)
            
        log_debug("Done processing video with AssemblyAI.")
    except Exception as e:
        log_debug(f"Transcription error: {e}\n{traceback.format_exc()}")
        transcript_segments = [
            {"speaker": "System", "text": f"Failed to transcribe: {str(e)}", "start": 0, "end": 5}
        ]
        summary_text = "Transcription failed due to an internal error."
    
    return {
        "transcript": transcript_segments,
        "summary": summary_text,
        "video_url": f"http://localhost:8000/uploads/{temp_video_path}"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
