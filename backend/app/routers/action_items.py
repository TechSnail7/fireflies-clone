"""
Action Items CRUD API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ActionItem, Meeting
from app.schemas import ActionItemCreate, ActionItemUpdate, ActionItemResponse

router = APIRouter(prefix="/api", tags=["action-items"])


@router.get("/meetings/{meeting_id}/action-items", response_model=list[ActionItemResponse])
def list_action_items(meeting_id: int, db: Session = Depends(get_db)):
    """List all action items for a meeting."""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return db.query(ActionItem).filter(
        ActionItem.meeting_id == meeting_id
    ).order_by(ActionItem.created_at).all()


@router.post("/meetings/{meeting_id}/action-items", response_model=ActionItemResponse, status_code=201)
def create_action_item(meeting_id: int, data: ActionItemCreate, db: Session = Depends(get_db)):
    """Create a new action item for a meeting."""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    action_item = ActionItem(
        meeting_id=meeting_id,
        text=data.text,
        assignee=data.assignee,
        is_completed=data.is_completed,
        due_date=data.due_date,
    )
    db.add(action_item)
    db.commit()
    db.refresh(action_item)
    return action_item


@router.put("/action-items/{item_id}", response_model=ActionItemResponse)
def update_action_item(item_id: int, data: ActionItemUpdate, db: Session = Depends(get_db)):
    """Update an action item."""
    action_item = db.query(ActionItem).filter(ActionItem.id == item_id).first()
    if not action_item:
        raise HTTPException(status_code=404, detail="Action item not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(action_item, key, value)

    db.commit()
    db.refresh(action_item)
    return action_item


@router.delete("/action-items/{item_id}", status_code=204)
def delete_action_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an action item."""
    action_item = db.query(ActionItem).filter(ActionItem.id == item_id).first()
    if not action_item:
        raise HTTPException(status_code=404, detail="Action item not found")

    db.delete(action_item)
    db.commit()
    return None
