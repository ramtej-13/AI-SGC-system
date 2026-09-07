from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Grievance, GrievanceHistory, User, UserRole
from app.schemas.schemas import GrievanceResponse, GrievanceStatusUpdate
from app.services.auth import require_role
from app.routers.grievances import build_grievance_response

router = APIRouter(tags=["Admin Grievance Management"])

@router.get("/department/grievances", response_model=List[GrievanceResponse])
def get_department_grievances(
    department_id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Administrator department-wise grievance view with filtering by department, status, and priority.
    """
    query = db.query(Grievance)
    if department_id:
        query = query.filter(Grievance.department_id == department_id)
    if status:
        query = query.filter(Grievance.status == status)
    if priority:
        query = query.filter(Grievance.priority == priority)
        
    grievances = query.order_by(Grievance.created_at.desc()).all()
    return [build_grievance_response(g) for g in grievances]

@router.patch("/grievances/{id}/status", response_model=GrievanceResponse)
def update_grievance_status(
    id: int,
    payload: GrievanceStatusUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Administrator updates grievance workflow status and appends resolution remarks to the audit trail.
    """
    g = db.query(Grievance).filter(Grievance.id == id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Grievance not found")

    prev_status = g.status
    if payload.status == prev_status:
        raise HTTPException(
            status_code=400,
            detail=f"Grievance is already in '{prev_status}' status. Choose a different status to update."
        )

    g.status = payload.status
    g.updated_at = datetime.utcnow()
    
    if payload.remarks:
        g.resolution_remarks = payload.remarks

    history_entry = GrievanceHistory(
        grievance_id=g.id,
        changed_by_user_id=current_user.id,
        previous_status=prev_status,
        new_status=payload.status,
        remarks=payload.remarks or f"Status transitioned from '{prev_status}' to '{payload.status}' by Administrator",
        created_at=datetime.utcnow()
    )
    db.add(history_entry)
    db.commit()
    db.refresh(g)

    return build_grievance_response(g)
