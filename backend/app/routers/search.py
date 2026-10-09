"""
Search and Upload API endpoints.
"""
import re
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models import Meeting, TranscriptSegment, Summary, ActionItem
from app.schemas import SearchResult, UploadResponse

router = APIRouter(prefix="/api", tags=["search", "upload"])


@router.get("/search", response_model=list[SearchResult])
def global_search(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    Global search across all meetings: titles, transcripts, summaries, and action items.
    Returns results grouped by match type with context.
    """
    results: list[SearchResult] = []
    search_term = f"%{q}%"

    # Search meeting titles
    title_matches = db.query(Meeting).filter(
        Meeting.title.ilike(search_term)
    ).limit(limit).all()
    for m in title_matches:
        results.append(SearchResult(
            meeting_id=m.id,
            meeting_title=m.title,
            meeting_date=m.date,
            text=m.title,
            match_type="title",
        ))

    # Search transcript segments
    segment_matches = db.query(TranscriptSegment).join(Meeting).filter(
        TranscriptSegment.text.ilike(search_term)
    ).limit(limit).all()
    for seg in segment_matches:
        meeting = db.query(Meeting).filter(Meeting.id == seg.meeting_id).first()
        if meeting:
            results.append(SearchResult(
                meeting_id=meeting.id,
                meeting_title=meeting.title,
                meeting_date=meeting.date,
                segment_id=seg.id,
                speaker=seg.speaker,
                text=seg.text,
                start_time=seg.start_time,
                match_type="transcript",
            ))

    # Search summaries
    summary_matches = db.query(Summary).join(Meeting).filter(
        Summary.overview.ilike(search_term)
    ).limit(limit).all()
    for summ in summary_matches:
        meeting = db.query(Meeting).filter(Meeting.id == summ.meeting_id).first()
        if meeting:
            results.append(SearchResult(
                meeting_id=meeting.id,
                meeting_title=meeting.title,
                meeting_date=meeting.date,
                text=summ.overview[:200],
                match_type="summary",
            ))

    # Search action items
    ai_matches = db.query(ActionItem).join(Meeting).filter(
        ActionItem.text.ilike(search_term)
    ).limit(limit).all()
    for ai in ai_matches:
        meeting = db.query(Meeting).filter(Meeting.id == ai.meeting_id).first()
        if meeting:
            results.append(SearchResult(
                meeting_id=meeting.id,
                meeting_title=meeting.title,
                meeting_date=meeting.date,
                text=ai.text,
                match_type="action_item",
            ))

    return results[:limit]


def _parse_vtt(content: str) -> list[dict]:
    """Parse a WebVTT file into transcript segments."""
    segments = []
    lines = content.strip().split("\n")
    i = 0
    order = 0

    while i < len(lines):
        line = lines[i].strip()

        # Skip WEBVTT header and empty lines
        if not line or line.startswith("WEBVTT") or line.startswith("NOTE"):
            i += 1
            continue

        # Check for timestamp line (e.g., "00:00:01.000 --> 00:00:05.000")
        timestamp_match = re.match(
            r"(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})",
            line
        )
        if timestamp_match:
            start_str, end_str = timestamp_match.groups()
            start_time = _vtt_time_to_seconds(start_str)
            end_time = _vtt_time_to_seconds(end_str)

            # Collect text lines until next empty line
            i += 1
            text_lines = []
            while i < len(lines) and lines[i].strip():
                text_lines.append(lines[i].strip())
                i += 1

            full_text = " ".join(text_lines)

            # Try to extract speaker from "<v Speaker Name>text" format
            speaker_match = re.match(r"<v\s+([^>]+)>(.*)", full_text)
            if speaker_match:
                speaker = speaker_match.group(1).strip()
                text = speaker_match.group(2).strip()
            else:
                # Try "Speaker: text" format
                colon_match = re.match(r"^([^:]{1,50}):\s*(.*)", full_text)
                if colon_match:
                    speaker = colon_match.group(1).strip()
                    text = colon_match.group(2).strip()
                else:
                    speaker = "Speaker"
                    text = full_text

            if text:
                segments.append({
                    "speaker": speaker,
                    "text": text,
                    "start_time": start_time,
                    "end_time": end_time,
                    "order_index": order,
                })
                order += 1
        else:
            i += 1

    return segments


def _parse_txt(content: str) -> list[dict]:
    """Parse a plain text transcript into segments."""
    segments = []
    lines = content.strip().split("\n")
    order = 0
    time_offset = 0.0

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Try formats:
        # [00:01:30] Speaker: Text
        # 00:01:30 - Speaker: Text
        # Speaker: Text
        timestamp_match = re.match(
            r"[\[\(]?(\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?)[\]\)]?\s*[-–]?\s*(.*)",
            line
        )

        if timestamp_match:
            time_str = timestamp_match.group(1)
            rest = timestamp_match.group(2)
            start_time = _parse_simple_time(time_str)
        else:
            rest = line
            start_time = time_offset

        # Extract speaker
        colon_match = re.match(r"^([^:]{1,50}):\s*(.*)", rest)
        if colon_match:
            speaker = colon_match.group(1).strip()
            text = colon_match.group(2).strip()
        else:
            speaker = "Speaker"
            text = rest

        if text:
            end_time = start_time + max(len(text) * 0.06, 2.0)  # Estimate ~60ms per char
            segments.append({
                "speaker": speaker,
                "text": text,
                "start_time": start_time,
                "end_time": end_time,
                "order_index": order,
            })
            order += 1
            time_offset = end_time

    return segments


def _parse_json_transcript(content: str) -> list[dict]:
    """Parse a JSON transcript file."""
    import json
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")

    segments = []
    items = data if isinstance(data, list) else data.get("segments", data.get("transcript", []))

    for i, item in enumerate(items):
        segments.append({
            "speaker": item.get("speaker", "Speaker"),
            "text": item.get("text", ""),
            "start_time": float(item.get("start_time", item.get("start", 0))),
            "end_time": float(item.get("end_time", item.get("end", 0))),
            "order_index": i,
        })

    return segments


def _vtt_time_to_seconds(time_str: str) -> float:
    """Convert VTT timestamp (HH:MM:SS.mmm) to seconds."""
    parts = time_str.split(":")
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    return hours * 3600 + minutes * 60 + seconds


def _parse_simple_time(time_str: str) -> float:
    """Convert simple timestamp (MM:SS or HH:MM:SS) to seconds."""
    parts = time_str.split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    return 0.0


@router.post("/meetings/upload", response_model=UploadResponse)
async def upload_transcript(
    file: UploadFile = File(...),
    title: str = Form(...),
    host: str = Form(default="Unknown"),
    participants: str = Form(default=""),
    db: Session = Depends(get_db),
):
    """
    Upload a transcript file (.txt, .vtt, .json) to create a new meeting.
    Parses the file and creates transcript segments automatically.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ("txt", "vtt", "json"):
        raise HTTPException(status_code=400, detail="Unsupported file type. Use .txt, .vtt, or .json")

    content = (await file.read()).decode("utf-8")

    # Parse based on file type
    if ext == "vtt":
        segments_data = _parse_vtt(content)
    elif ext == "json":
        segments_data = _parse_json_transcript(content)
    else:
        segments_data = _parse_txt(content)

    if not segments_data:
        raise HTTPException(status_code=400, detail="No transcript segments could be parsed from the file")

    # Calculate duration from last segment
    duration = max(s["end_time"] for s in segments_data) if segments_data else 0

    # Parse participants
    participant_list = [p.strip() for p in participants.split(",") if p.strip()] if participants else []

    # Extract unique speakers from transcript
    speakers = list(set(s["speaker"] for s in segments_data))
    all_participants = list(set(participant_list + speakers))

    # Create meeting
    meeting = Meeting(
        title=title,
        date=datetime.utcnow(),
        duration_seconds=int(duration),
        host=host,
        participants=all_participants,
        status="completed",
        meeting_type="audio",
    )
    db.add(meeting)
    db.flush()

    # Create segments
    for seg in segments_data:
        segment = TranscriptSegment(
            meeting_id=meeting.id,
            speaker=seg["speaker"],
            text=seg["text"],
            start_time=seg["start_time"],
            end_time=seg["end_time"],
            order_index=seg["order_index"],
        )
        db.add(segment)

    # Create a basic auto-generated summary
    overview_parts = []
    topic_speakers = {}
    for seg in segments_data[:20]:  # Use first 20 segments for overview
        if seg["speaker"] not in topic_speakers:
            topic_speakers[seg["speaker"]] = []
        topic_speakers[seg["speaker"]].append(seg["text"])

    overview = f"Meeting '{title}' with {len(speakers)} participants: {', '.join(speakers)}. "
    overview += f"The meeting lasted approximately {int(duration // 60)} minutes."

    summary = Summary(
        meeting_id=meeting.id,
        overview=overview,
        key_topics=[{"title": "Uploaded Transcript", "description": "Transcript uploaded and parsed successfully."}],
        chapters=[],
        outline=[],
    )
    db.add(summary)

    db.commit()

    return UploadResponse(
        meeting_id=meeting.id,
        segments_count=len(segments_data),
        message=f"Successfully created meeting with {len(segments_data)} transcript segments",
    )
