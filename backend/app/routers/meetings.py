"""
Meeting CRUD API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, or_, func
from typing import Optional
from datetime import datetime
import os
import uuid
import traceback
from fastapi.concurrency import run_in_threadpool
from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File

from app.database import get_db
from app.models import Meeting, TranscriptSegment, Summary, ActionItem, Tag, meeting_tags
from app.schemas import (
    MeetingCreate, MeetingUpdate, MeetingListResponse,
    MeetingDetailResponse, TranscriptSegmentResponse,
    SummaryResponse, SummaryUpdate, SummaryCreate,
)

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


def _get_meeting_or_404(db: Session, meeting_id: int) -> Meeting:
    """Helper to fetch a meeting or raise 404."""
    meeting = db.query(Meeting).options(
        joinedload(Meeting.tags),
        joinedload(Meeting.action_items),
    ).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


def _to_list_response(meeting: Meeting) -> MeetingListResponse:
    """Convert a Meeting ORM object to a list response."""
    return MeetingListResponse(
        id=meeting.id,
        title=meeting.title,
        date=meeting.date,
        duration_seconds=meeting.duration_seconds,
        host=meeting.host,
        participants=meeting.participants or [],
        status=meeting.status,
        meeting_type=meeting.meeting_type,
        video_url=meeting.video_url,
        tags=[{"id": t.id, "name": t.name, "color": t.color} for t in meeting.tags],
        action_items_count=len(meeting.action_items),
        action_items_completed=sum(1 for ai in meeting.action_items if ai.is_completed),
        created_at=meeting.created_at,
        updated_at=meeting.updated_at,
    )


@router.get("", response_model=list[MeetingListResponse])
def list_meetings(
    search: Optional[str] = Query(None, description="Search in title, host, participants"),
    sort_by: str = Query("date", description="Sort field: date, title, duration_seconds"),
    sort_order: str = Query("desc", description="Sort order: asc, desc"),
    tag: Optional[str] = Query(None, description="Filter by tag name"),
    status: Optional[str] = Query(None, description="Filter by status"),
    date_from: Optional[str] = Query(None, description="Filter from date (ISO)"),
    date_to: Optional[str] = Query(None, description="Filter to date (ISO)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all meetings with optional search, filter, and sort."""
    query = db.query(Meeting).options(
        joinedload(Meeting.tags),
        joinedload(Meeting.action_items),
    )

    # Search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Meeting.title.ilike(search_term),
                Meeting.host.ilike(search_term),
                Meeting.participants.like(search_term),
            )
        )

    # Tag filter
    if tag:
        query = query.join(Meeting.tags).filter(Tag.name == tag)

    # Status filter
    if status:
        query = query.filter(Meeting.status == status)

    # Date filters
    if date_from:
        try:
            dt_from = datetime.fromisoformat(date_from)
            query = query.filter(Meeting.date >= dt_from)
        except ValueError:
            pass
    if date_to:
        try:
            dt_to = datetime.fromisoformat(date_to)
            query = query.filter(Meeting.date <= dt_to)
        except ValueError:
            pass

    # Sorting
    sort_column = getattr(Meeting, sort_by, Meeting.date)
    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Use unique() to handle joined eager loads properly
    meetings = query.offset(skip).limit(limit).all()
    seen_ids = set()
    unique_meetings = []
    for m in meetings:
        if m.id not in seen_ids:
            seen_ids.add(m.id)
            unique_meetings.append(m)

    return [_to_list_response(m) for m in unique_meetings]


@router.post("", response_model=MeetingDetailResponse, status_code=201)
def create_meeting(data: MeetingCreate, db: Session = Depends(get_db)):
    """Create a new meeting with optional transcript, summary, and action items."""
    meeting = Meeting(
        title=data.title,
        date=data.date,
        duration_seconds=data.duration_seconds,
        host=data.host,
        participants=data.participants,
        status=data.status,
        meeting_type=data.meeting_type,
        video_url=data.video_url,
    )
    db.add(meeting)
    db.flush()

    # Add tags (create if they don't exist)
    for tag_name in data.tags:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            db.flush()
        meeting.tags.append(tag)

    # Add transcript segments
    for i, seg in enumerate(data.transcript_segments):
        segment = TranscriptSegment(
            meeting_id=meeting.id,
            speaker=seg.speaker,
            text=seg.text,
            start_time=seg.start_time,
            end_time=seg.end_time,
            order_index=seg.order_index if seg.order_index else i,
        )
        db.add(segment)

    # Add summary
    if data.summary:
        summary = Summary(
            meeting_id=meeting.id,
            overview=data.summary.overview,
            key_topics=data.summary.key_topics,
            chapters=data.summary.chapters,
            outline=data.summary.outline,
        )
        db.add(summary)

    # Add action items
    for ai_data in data.action_items:
        action_item = ActionItem(
            meeting_id=meeting.id,
            text=ai_data.text,
            assignee=ai_data.assignee,
            is_completed=ai_data.is_completed,
            due_date=ai_data.due_date,
        )
        db.add(action_item)

    db.commit()
    db.refresh(meeting)

    # Re-fetch with all relationships
    return _get_meeting_detail(db, meeting.id)


@router.get("/{meeting_id}", response_model=MeetingDetailResponse)
def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    """Get a single meeting with all details."""
    return _get_meeting_detail(db, meeting_id)


def _get_meeting_detail(db: Session, meeting_id: int) -> MeetingDetailResponse:
    """Build a full meeting detail response."""
    meeting = db.query(Meeting).options(
        joinedload(Meeting.tags),
        joinedload(Meeting.segments),
        joinedload(Meeting.summary),
        joinedload(Meeting.action_items),
    ).filter(Meeting.id == meeting_id).first()

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return MeetingDetailResponse(
        id=meeting.id,
        title=meeting.title,
        date=meeting.date,
        duration_seconds=meeting.duration_seconds,
        host=meeting.host,
        participants=meeting.participants or [],
        status=meeting.status,
        meeting_type=meeting.meeting_type,
        video_url=meeting.video_url,
        tags=[{"id": t.id, "name": t.name, "color": t.color} for t in meeting.tags],
        action_items_count=len(meeting.action_items),
        action_items_completed=sum(1 for ai in meeting.action_items if ai.is_completed),
        created_at=meeting.created_at,
        updated_at=meeting.updated_at,
        segments=[TranscriptSegmentResponse.model_validate(s) for s in meeting.segments],
        summary=SummaryResponse.model_validate(meeting.summary) if meeting.summary else None,
        action_items=meeting.action_items,
    )


@router.put("/{meeting_id}", response_model=MeetingDetailResponse)
def update_meeting(meeting_id: int, data: MeetingUpdate, db: Session = Depends(get_db)):
    """Update meeting metadata."""
    meeting = _get_meeting_or_404(db, meeting_id)

    update_data = data.model_dump(exclude_unset=True)
    tags_data = update_data.pop("tags", None)

    for key, value in update_data.items():
        setattr(meeting, key, value)

    meeting.updated_at = datetime.utcnow()

    # Update tags if provided
    if tags_data is not None:
        meeting.tags.clear()
        for tag_name in tags_data:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.flush()
            meeting.tags.append(tag)

    db.commit()
    return _get_meeting_detail(db, meeting_id)


@router.delete("/{meeting_id}", status_code=204)
def delete_meeting(meeting_id: int, db: Session = Depends(get_db)):
    """Delete a meeting and all associated data."""
    meeting = _get_meeting_or_404(db, meeting_id)
    db.delete(meeting)
    db.commit()
    return None


# ──────────────────────────── Transcript Endpoints ────────────────────────────

@router.get("/{meeting_id}/transcript", response_model=list[TranscriptSegmentResponse])
def get_transcript(
    meeting_id: int,
    search: Optional[str] = Query(None, description="Search within transcript text"),
    db: Session = Depends(get_db),
):
    """Get transcript segments for a meeting, with optional search."""
    _get_meeting_or_404(db, meeting_id)

    query = db.query(TranscriptSegment).filter(
        TranscriptSegment.meeting_id == meeting_id
    )

    if search:
        query = query.filter(TranscriptSegment.text.ilike(f"%{search}%"))

    return query.order_by(TranscriptSegment.order_index).all()


# ──────────────────────────── Summary Endpoints ────────────────────────────

@router.get("/{meeting_id}/summary", response_model=Optional[SummaryResponse])
def get_summary(meeting_id: int, db: Session = Depends(get_db)):
    """Get the AI summary for a meeting."""
    _get_meeting_or_404(db, meeting_id)
    summary = db.query(Summary).filter(Summary.meeting_id == meeting_id).first()
    return summary


@router.put("/{meeting_id}/summary", response_model=SummaryResponse)
def update_summary(meeting_id: int, data: SummaryUpdate, db: Session = Depends(get_db)):
    """Update or create the summary for a meeting."""
    _get_meeting_or_404(db, meeting_id)
    summary = db.query(Summary).filter(Summary.meeting_id == meeting_id).first()

    if not summary:
        summary = Summary(meeting_id=meeting_id)
        db.add(summary)

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(summary, key, value)

    db.commit()
    db.refresh(summary)
    return summary


# ──────────────────────────── Video Processing Endpoint ────────────────────────────

@router.post("/process-video")
async def process_video(request: Request, file: UploadFile = File(...)):
    """Process a video file using AssemblyAI and return transcript and summary."""
    cl = request.headers.get("Content-Length")
    
    safe_ext = file.filename.split('.')[-1] if '.' in file.filename else 'mp4'
    temp_video_path = f"temp_{uuid.uuid4().hex}.{safe_ext}"
    
    try:
        await file.seek(0)
        data = await file.read()
        
        # Save the uploaded file to the backend uploads directory so it can be served
        backend_uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
        os.makedirs(backend_uploads_dir, exist_ok=True)
        final_video_path = os.path.join(backend_uploads_dir, temp_video_path)
        
        with open(final_video_path, "wb") as buffer:
            buffer.write(data)
            
        file_size = os.path.getsize(final_video_path)
        
        if file_size == 0:
            raise ValueError(f"Uploaded file is 0 bytes! Request Content-Length was {cl}.")
            
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
            
    except Exception as e:
        transcript_segments = [
            {"speaker": "System", "text": f"Failed to transcribe: {str(e)}", "start": 0, "end": 5}
        ]
        summary_text = "Transcription failed due to an internal error."
    
    return {
        "transcript": transcript_segments,
        "summary": summary_text,
        "video_url": f"/uploads/{temp_video_path}"
    }
