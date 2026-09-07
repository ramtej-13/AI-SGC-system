import time
import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import (
    Grievance, GrievanceHistory, ModelPrediction, ManualReview,
    User, UserRole, Department, GrievanceStatus
)
from app.schemas.schemas import (
    GrievanceCreate, GrievanceResponse, ModelPredictionResponse,
    GrievanceHistoryResponse, TopPredictionItem
)
from app.services.auth import get_current_user
from app.services.routing import get_department_for_category
from app.services.priority import calculate_priority
from app.ml.predict import get_classifier

router = APIRouter(prefix="/grievances", tags=["Grievances"])

def build_grievance_response(g: Grievance) -> dict:
    dept = g.department
    student = g.student
    pred = g.prediction
    
    top_preds = []
    if pred and pred.top_classes_json:
        try:
            top_preds = json.loads(pred.top_classes_json)
        except Exception:
            top_preds = []

    pred_resp = None
    if pred:
        pred_resp = {
            "predicted_category": pred.predicted_category,
            "confidence_score": pred.confidence_score,
            "is_fallback": pred.is_fallback,
            "raw_predicted_category": pred.raw_predicted_category,
            "raw_confidence": pred.raw_confidence,
            "top_predictions": top_preds,
            "inference_time_ms": pred.inference_time_ms
        }

    history_resp = [
        {
            "id": h.id,
            "previous_status": h.previous_status,
            "new_status": h.new_status,
            "remarks": h.remarks,
            "changed_by_name": h.changed_by_user.full_name if h.changed_by_user else "System AI",
            "created_at": h.created_at
        }
        for h in (g.history or [])
    ]

    return {
        "id": g.id,
        "ticket_number": g.ticket_number,
        "title": g.title,
        "description": g.description,
        "category": g.category,
        "department_id": g.department_id,
        "department_code": dept.code if dept else None,
        "department_name": dept.name if dept else None,
        "priority": g.priority,
        "priority_reason": g.priority_reason,
        "status": g.status,
        "is_low_confidence": g.is_low_confidence,
        "resolution_remarks": g.resolution_remarks,
        "student_id": g.student_id,
        "student_name": student.full_name if student else "Unknown Student",
        "student_email": student.email if student else None,
        "created_at": g.created_at,
        "updated_at": g.updated_at,
        "prediction": pred_resp,
        "history": history_resp
    }

@router.post("", response_model=GrievanceResponse, status_code=status.HTTP_201_CREATED)
def submit_grievance(
    payload: GrievanceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # ML Classification
    classifier = get_classifier()
    t_start = time.perf_counter()
    pred_result = classifier.predict(payload.description)
    t_elapsed_ms = round((time.perf_counter() - t_start) * 1000, 2)

    predicted_cat = pred_result["predicted_category"]
    is_low_conf = pred_result["is_low_confidence"]
    raw_cat = pred_result["raw_predicted_category"]
    raw_conf = pred_result["raw_confidence"]
    top_preds = pred_result["top_predictions"]

    # Deterministic Routing to Department
    dept = get_department_for_category(predicted_cat, db)
    if not dept:
        raise HTTPException(status_code=500, detail="Unable to route grievance: No target department configured")

    # Rule-Based Priority Engine
    priority_level, priority_reason = calculate_priority(payload.description, predicted_cat)

    # Generate sequential ticket number (safe against record deletions)
    max_id = db.query(func.max(Grievance.id)).scalar() or 0
    current_year = datetime.utcnow().year
    ticket_num = f"GRV-{current_year}-{(max_id + 1):04d}"

    # Create Grievance
    new_grievance = Grievance(
        ticket_number=ticket_num,
        student_id=current_user.id,
        title=payload.title.strip(),
        description=payload.description.strip(),
        category=predicted_cat,
        department_id=dept.id,
        priority=priority_level,
        priority_reason=priority_reason,
        status=GrievanceStatus.SUBMITTED,
        is_low_confidence=is_low_conf,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_grievance)
    db.flush()

    # Save Model Prediction record
    pred_record = ModelPrediction(
        grievance_id=new_grievance.id,
        predicted_category=predicted_cat,
        confidence_score=raw_conf if not is_low_conf else pred_result["confidence"],
        is_fallback=is_low_conf,
        raw_predicted_category=raw_cat,
        raw_confidence=raw_conf,
        top_classes_json=json.dumps(top_preds),
        raw_text_cleaned=pred_result["cleaned_text"],
        inference_time_ms=t_elapsed_ms,
        created_at=datetime.utcnow()
    )
    db.add(pred_record)

    # If low confidence, flag for Manual Review queue
    if is_low_conf:
        manual_review = ManualReview(
            grievance_id=new_grievance.id,
            original_category=raw_cat,
            status="pending",
            review_notes=f"Low confidence score ({raw_conf:.2f} < threshold {pred_result['threshold_applied']:.2f}). Auto-routed to Central Helpdesk for human triage.",
            created_at=datetime.utcnow()
        )
        db.add(manual_review)

    # Audit history entry
    hist_entry = GrievanceHistory(
        grievance_id=new_grievance.id,
        changed_by_user_id=current_user.id,
        previous_status=None,
        new_status=GrievanceStatus.SUBMITTED,
        remarks=f"Grievance filed by student. AI classified as '{predicted_cat}' (Confidence: {raw_conf:.2f}), routed to {dept.name} with {priority_level} priority.",
        created_at=datetime.utcnow()
    )
    db.add(hist_entry)
    db.commit()
    db.refresh(new_grievance)

    return build_grievance_response(new_grievance)

@router.get("/my", response_model=List[GrievanceResponse])
def get_my_grievances(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    grievances = (
        db.query(Grievance)
        .filter(Grievance.student_id == current_user.id)
        .order_by(Grievance.created_at.desc())
        .all()
    )
    return [build_grievance_response(g) for g in grievances]

@router.get("/{id}", response_model=GrievanceResponse)
def get_grievance_by_id(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    g = db.query(Grievance).filter(Grievance.id == id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Grievance not found")

    # Authorization check: Student can access only their own grievances; Admin can access all
    if current_user.role == UserRole.STUDENT and g.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied to this grievance")

    return build_grievance_response(g)
