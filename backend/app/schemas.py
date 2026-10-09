"""
Pydantic schemas for request/response validation and serialization.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ──────────────────────────── Tag ────────────────────────────

class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(default="#7C3AED", max_length=20)

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: int
    class Config:
        from_attributes = True


# ──────────────────────────── Transcript Segment ────────────────────────────

class TranscriptSegmentBase(BaseModel):
    speaker: str = Field(..., min_length=1, max_length=100)
    text: str = Field(..., min_length=1)
    start_time: float = Field(default=0.0, ge=0)
    end_time: float = Field(default=0.0, ge=0)
    order_index: int = Field(default=0, ge=0)

class TranscriptSegmentCreate(TranscriptSegmentBase):
    pass

class TranscriptSegmentResponse(TranscriptSegmentBase):
    id: int
    meeting_id: int
    class Config:
        from_attributes = True


# ──────────────────────────── Summary ────────────────────────────

class SummaryBase(BaseModel):
    overview: str = Field(default="")
    key_topics: list = Field(default_factory=list)
    chapters: list = Field(default_factory=list)
    outline: list = Field(default_factory=list)

class SummaryCreate(SummaryBase):
    pass

class SummaryUpdate(BaseModel):
    overview: Optional[str] = None
    key_topics: Optional[list] = None
    chapters: Optional[list] = None
    outline: Optional[list] = None

class SummaryResponse(SummaryBase):
    id: int
    meeting_id: int
    class Config:
        from_attributes = True


# ──────────────────────────── Action Item ────────────────────────────

class ActionItemBase(BaseModel):
    text: str = Field(..., min_length=1)
    assignee: Optional[str] = None
    is_completed: bool = Field(default=False)
    due_date: Optional[datetime] = None

class ActionItemCreate(ActionItemBase):
    pass

class ActionItemUpdate(BaseModel):
    text: Optional[str] = None
    assignee: Optional[str] = None
    is_completed: Optional[bool] = None
    due_date: Optional[datetime] = None

class ActionItemResponse(ActionItemBase):
    id: int
    meeting_id: int
    created_at: datetime
    class Config:
        from_attributes = True


# ──────────────────────────── Meeting ────────────────────────────

class MeetingBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    date: datetime = Field(default_factory=datetime.utcnow)
    duration_seconds: int = Field(default=0, ge=0)
    host: str = Field(default="Unknown", max_length=100)
    participants: list[str] = Field(default_factory=list)
    status: str = Field(default="completed", pattern="^(completed|processing|failed)$")
    meeting_type: str = Field(default="video", pattern="^(video|audio|in_person)$")
    video_url: Optional[str] = None

class MeetingCreate(MeetingBase):
    tags: list[str] = Field(default_factory=list)  # tag names
    transcript_segments: list[TranscriptSegmentCreate] = Field(default_factory=list)
    summary: Optional[SummaryCreate] = None
    action_items: list[ActionItemCreate] = Field(default_factory=list)

class MeetingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    date: Optional[datetime] = None
    duration_seconds: Optional[int] = Field(None, ge=0)
    host: Optional[str] = Field(None, max_length=100)
    participants: Optional[list[str]] = None
    status: Optional[str] = Field(None, pattern="^(completed|processing|failed)$")
    meeting_type: Optional[str] = Field(None, pattern="^(video|audio|in_person)$")
    tags: Optional[list[str]] = None

class MeetingListResponse(BaseModel):
    id: int
    title: str
    date: datetime
    duration_seconds: int
    host: str
    participants: list[str]
    status: str
    meeting_type: str
    video_url: Optional[str] = None
    tags: list[TagResponse] = []
    action_items_count: int = 0
    action_items_completed: int = 0
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class MeetingDetailResponse(MeetingListResponse):
    segments: list[TranscriptSegmentResponse] = []
    summary: Optional[SummaryResponse] = None
    action_items: list[ActionItemResponse] = []
    class Config:
        from_attributes = True


# ──────────────────────────── Search ────────────────────────────

class SearchResult(BaseModel):
    meeting_id: int
    meeting_title: str
    meeting_date: datetime
    segment_id: Optional[int] = None
    speaker: Optional[str] = None
    text: str
    start_time: Optional[float] = None
    match_type: str  # "title", "transcript", "summary", "action_item"


# ──────────────────────────── Upload ────────────────────────────

class UploadResponse(BaseModel):
    meeting_id: int
    segments_count: int
    message: str
