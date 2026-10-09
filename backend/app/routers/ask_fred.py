"""
Ask Fred AI Assistant router powered by Groq LLM.
Provides intelligent answers, action items, key decisions, and meeting insights.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import Meeting, TranscriptSegment, Summary, ActionItem
from app.llm import ask_fred_llm_chat

router = APIRouter(prefix="/api/ask-fred", tags=["ask-fred"])


class AskFredRequest(BaseModel):
    query: str
    channel: Optional[str] = "My Meetings"
    meeting_id: Optional[int] = None


class AskFredResponse(BaseModel):
    reply: str
    query_type: str
    items: Optional[List[Any]] = None
    references: Optional[List[dict]] = None


@router.post("", response_model=AskFredResponse)
def ask_fred(req: AskFredRequest, db: Session = Depends(get_db)):
    query = req.query.strip()
    q_lower = query.lower()

    # Collect workspace meeting context for the LLM
    context_docs: List[Dict[str, Any]] = []

    # If meeting_id is specified, target that meeting
    if req.meeting_id:
        target_meeting = db.query(Meeting).filter(Meeting.id == req.meeting_id).first()
        meetings = [target_meeting] if target_meeting else []
    else:
        meetings = db.query(Meeting).order_by(desc(Meeting.date)).limit(6).all()

    for m in meetings:
        summary_obj = db.query(Summary).filter(Summary.meeting_id == m.id).first()
        action_items = db.query(ActionItem).filter(ActionItem.meeting_id == m.id).all()
        
        # Pull top segments or matching segments
        segments = (
            db.query(TranscriptSegment)
            .filter(TranscriptSegment.meeting_id == m.id)
            .order_by(TranscriptSegment.order_index)
            .limit(10)
            .all()
        )

        excerpt_text = "\n".join([f"[{s.speaker}]: {s.text}" for s in segments])

        context_docs.append({
            "title": m.title,
            "date": m.date.isoformat() if hasattr(m.date, 'isoformat') else str(m.date),
            "host": m.host,
            "overview": summary_obj.overview if summary_obj else "",
            "action_items": [{"text": ai.text, "assignee": ai.assignee, "is_completed": ai.is_completed} for ai in action_items],
            "transcript_excerpt": excerpt_text
        })

    # Determine query type
    is_action_items = any(k in q_lower for k in ["action item", "action items", "tasks", "my tasks", "to do", "todo"])
    is_decisions = any(k in q_lower for k in ["decision", "decisions", "what was decided", "agreement"])
    is_initiatives = any(k in q_lower for k in ["initiative", "initiatives", "roadmap", "goals", "strategic"])

    if is_action_items:
        query_type = "action_items"
    elif is_decisions:
        query_type = "decisions"
    elif is_initiatives:
        query_type = "initiatives"
    else:
        query_type = "qa"

    # Call Groq LLM
    llm_reply = ask_fred_llm_chat(query, req.channel or "My Meetings", context_docs)

    # For structured action items query, also fetch action items list for the UI checkboxes
    items_data = None
    if is_action_items:
        db_action_items = (
            db.query(ActionItem, Meeting)
            .join(Meeting, ActionItem.meeting_id == Meeting.id)
            .order_by(desc(Meeting.date))
            .limit(10)
            .all()
        )
        items_data = [
            {
                "id": ai.id,
                "text": ai.text,
                "assignee": ai.assignee or "Unassigned",
                "is_completed": ai.is_completed,
                "due_date": ai.due_date,
                "meeting_title": m.title,
                "meeting_id": m.id,
            }
            for ai, m in db_action_items
        ]

    return AskFredResponse(
        reply=llm_reply,
        query_type=query_type,
        items=items_data,
        references=[]
    )
