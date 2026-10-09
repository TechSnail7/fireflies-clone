"""
SQLAlchemy ORM models for the Fireflies clone database.

Schema Design:
- Meeting: core entity holding metadata (title, date, duration, host, participants)
- TranscriptSegment: individual lines of a transcript with speaker, timestamps, and text
- Summary: AI-generated meeting summary with overview, key topics, and chapters
- ActionItem: extracted tasks/action items from a meeting
- Tag: reusable labels for categorizing meetings
- MeetingTag: many-to-many association between meetings and tags
"""
import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON, Table
)
from sqlalchemy.orm import relationship
from app.database import Base


# Many-to-many association table for Meeting <-> Tag
meeting_tags = Table(
    "meeting_tags",
    Base.metadata,
    Column("meeting_id", Integer, ForeignKey("meetings.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Meeting(Base):
    """
    Represents a recorded meeting with metadata.
    Participants are stored as a JSON array of strings for flexibility.
    """
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    date = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    duration_seconds = Column(Integer, nullable=False, default=0)
    host = Column(String(100), nullable=False, default="Unknown")
    participants = Column(JSON, nullable=False, default=list)
    status = Column(String(50), nullable=False, default="completed")  # completed, processing, failed
    meeting_type = Column(String(50), nullable=False, default="video")  # video, audio, in_person
    video_url = Column(String(1024), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    segments = relationship("TranscriptSegment", back_populates="meeting", cascade="all, delete-orphan", order_by="TranscriptSegment.order_index")
    summary = relationship("Summary", back_populates="meeting", uselist=False, cascade="all, delete-orphan")
    action_items = relationship("ActionItem", back_populates="meeting", cascade="all, delete-orphan", order_by="ActionItem.created_at")
    tags = relationship("Tag", secondary=meeting_tags, back_populates="meetings")


class TranscriptSegment(Base):
    """
    Individual segment/line of a transcript.
    Stored as separate rows (not JSON blob) for efficient search and timestamp-seeking.
    """
    __tablename__ = "transcript_segments"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    speaker = Column(String(100), nullable=False)
    text = Column(Text, nullable=False)
    start_time = Column(Float, nullable=False, default=0.0)  # seconds from meeting start
    end_time = Column(Float, nullable=False, default=0.0)
    order_index = Column(Integer, nullable=False, default=0)

    # Relationships
    meeting = relationship("Meeting", back_populates="segments")


class Summary(Base):
    """
    AI-generated meeting summary with structured sections.
    Key topics and chapters are stored as JSON arrays for flexibility.
    """
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    overview = Column(Text, nullable=False, default="")
    key_topics = Column(JSON, nullable=False, default=list)    # [{title, description}]
    chapters = Column(JSON, nullable=False, default=list)      # [{title, start_time, end_time, summary}]
    outline = Column(JSON, nullable=False, default=list)       # [{heading, points: []}]

    # Relationships
    meeting = relationship("Meeting", back_populates="summary")


class ActionItem(Base):
    """
    Task/action item extracted from a meeting.
    Can be assigned to a participant and marked as completed.
    """
    __tablename__ = "action_items"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    assignee = Column(String(100), nullable=True)
    is_completed = Column(Boolean, nullable=False, default=False)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    # Relationships
    meeting = relationship("Meeting", back_populates="action_items")


class Tag(Base):
    """
    Reusable label/category for organizing meetings.
    """
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    color = Column(String(20), nullable=False, default="#7C3AED")

    # Relationships
    meetings = relationship("Meeting", secondary=meeting_tags, back_populates="tags")
