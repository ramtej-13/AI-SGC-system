import os
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.models import (
    Grievance, GrievanceHistory, ModelPrediction, ManualReview,
    Department, User, UserRole, GrievanceStatus
)
from app.schemas.schemas import (
    GrievanceResponse, DepartmentResponse, UserResponse,
    ManualReviewAction, ModelGeneralizationTestRequest, ModelGeneralizationTestResponse,
    AnalyticsResponse
)
from app.services.auth import require_role, get_current_user
from app.services.routing import route_category_to_department_code, get_department_for_category
from app.services.priority import calculate_priority
from app.ml.predict import get_classifier
from app.routers.grievances import build_grievance_response

router = APIRouter(tags=["Admin & Institutional Operations"])

@router.get("/admin/grievances", response_model=List[GrievanceResponse])
def get_all_grievances(
    status: Optional[str] = None,
    category: Optional[str] = None,
    department_id: Optional[int] = None,
    priority: Optional[str] = None,
    low_confidence: Optional[bool] = None,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    query = db.query(Grievance)
    if status:
        query = query.filter(Grievance.status == status)
    if category:
        query = query.filter(Grievance.category == category)
    if department_id:
        query = query.filter(Grievance.department_id == department_id)
    if priority:
        query = query.filter(Grievance.priority == priority)
    if low_confidence is not None:
        query = query.filter(Grievance.is_low_confidence == low_confidence)

    grievances = query.order_by(Grievance.created_at.desc()).all()
    return [build_grievance_response(g) for g in grievances]

@router.get("/admin/analytics", response_model=AnalyticsResponse)
def get_analytics(
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    total = db.query(Grievance).count()

    # Status distribution
    status_counts = dict(
        db.query(Grievance.status, func.count(Grievance.id)).group_by(Grievance.status).all()
    )

    # Category distribution
    cat_counts = dict(
        db.query(Grievance.category, func.count(Grievance.id)).group_by(Grievance.category).all()
    )

    # Department distribution
    dept_rows = (
        db.query(Department.name, func.count(Grievance.id))
        .join(Grievance, Grievance.department_id == Department.id, isouter=True)
        .group_by(Department.name)
        .all()
    )
    dept_counts = {name: count for name, count in dept_rows if count > 0}

    # Priority distribution
    priority_counts = dict(
        db.query(Grievance.priority, func.count(Grievance.id)).group_by(Grievance.priority).all()
    )

    low_conf_count = db.query(Grievance).filter(Grievance.is_low_confidence == True).count()
    resolved_count = (
        db.query(Grievance)
        .filter(Grievance.status.in_([GrievanceStatus.RESOLVED, GrievanceStatus.CLOSED]))
        .count()
    )

    # Average resolution time calculation
    resolved_grievances = (
        db.query(Grievance)
        .filter(Grievance.status.in_([GrievanceStatus.RESOLVED, GrievanceStatus.CLOSED]))
        .all()
    )
    total_hours = 0.0
    count_resolved_with_time = 0
    for g in resolved_grievances:
        if g.updated_at and g.created_at:
            delta = (g.updated_at - g.created_at).total_seconds() / 3600.0
            total_hours += max(delta, 0.1)
            count_resolved_with_time += 1

    avg_hours = round(total_hours / count_resolved_with_time, 1) if count_resolved_with_time > 0 else None

    return {
        "total_grievances": total,
        "status_distribution": status_counts,
        "category_distribution": cat_counts,
        "department_distribution": dept_counts,
        "priority_distribution": priority_counts,
        "low_confidence_count": low_conf_count,
        "resolved_count": resolved_count,
        "avg_resolution_hours": avg_hours
    }

@router.get("/admin/model-performance")
def get_model_performance(
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    classifier = get_classifier()
    meta_path = os.path.join(classifier.artifacts_dir, "metadata.json")
    if not os.path.exists(meta_path):
        raise HTTPException(
            status_code=404,
            detail="Model metadata artifact not found. Please train the model first."
        )
    with open(meta_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

@router.post("/admin/model-test", response_model=ModelGeneralizationTestResponse)
def test_unseen_sentence(
    payload: ModelGeneralizationTestRequest,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Real-time inference and explainability sandbox for arbitrary unseen test inputs.
    Demonstrates model generalization, fallback thresholds, and rule-based priority.
    """
    classifier = get_classifier()
    pred_res = classifier.predict(payload.text, threshold=payload.threshold)
    
    cat = pred_res["predicted_category"]
    dept_code = route_category_to_department_code(cat)
    dept = db.query(Department).filter(Department.code == dept_code).first()
    dept_name = dept.name if dept else f"Target: {dept_code}"
    
    priority_level, priority_reason = calculate_priority(payload.text, cat)

    return {
        "predicted_category": cat,
        "confidence": pred_res["confidence"],
        "is_low_confidence": pred_res["is_low_confidence"],
        "suggested_department": dept_name,
        "suggested_priority": priority_level,
        "priority_reason": priority_reason,
        "top_predictions": pred_res["top_predictions"],
        "raw_predicted_category": pred_res["raw_predicted_category"],
        "raw_confidence": pred_res["raw_confidence"],
        "cleaned_text": pred_res["cleaned_text"]
    }

@router.get("/admin/low-confidence", response_model=List[GrievanceResponse])
def get_low_confidence_queue(
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    grievances = (
        db.query(Grievance)
        .filter(Grievance.is_low_confidence == True)
        .order_by(Grievance.created_at.desc())
        .all()
    )
    return [build_grievance_response(g) for g in grievances]

@router.post("/admin/manual-review/{id}", response_model=GrievanceResponse)
def resolve_manual_review(
    id: int,
    action: ManualReviewAction,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    g = db.query(Grievance).filter(Grievance.id == id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Grievance not found")

    # Determine department
    if action.assigned_department_id:
        target_dept = db.query(Department).filter(Department.id == action.assigned_department_id).first()
    else:
        target_dept = get_department_for_category(action.assigned_category, db)

    if not target_dept:
        raise HTTPException(status_code=400, detail="Invalid target department")

    old_cat = g.category
    old_dept_name = g.department.name if g.department else "None"
    previous_status = g.status
    
    g.category = action.assigned_category
    g.department_id = target_dept.id
    g.is_low_confidence = False
    g.status = GrievanceStatus.ASSIGNED
    g.updated_at = datetime.utcnow()

    # Update manual review record if exists
    mr = db.query(ManualReview).filter(ManualReview.grievance_id == g.id).first()
    if mr:
        mr.assigned_category = action.assigned_category
        mr.reviewed_by_user_id = current_user.id
        mr.status = "reviewed"
        mr.review_notes = action.review_notes or "Reclassified and routed by Administrator."
        mr.updated_at = datetime.utcnow()

    # Log history with actual previous status
    hist = GrievanceHistory(
        grievance_id=g.id,
        changed_by_user_id=current_user.id,
        previous_status=previous_status,
        new_status=GrievanceStatus.ASSIGNED,
        remarks=f"Manual review completed by Administrator {current_user.full_name}: Category updated from '{old_cat}' to '{action.assigned_category}'. Routed from '{old_dept_name}' to '{target_dept.name}'. Action notes: {action.review_notes or 'None'}",
        created_at=datetime.utcnow()
    )
    db.add(hist)
    db.commit()
    db.refresh(g)

    return build_grievance_response(g)

@router.get("/departments", response_model=List[DepartmentResponse])
def get_departments(db: Session = Depends(get_db)):
    return db.query(Department).filter(Department.is_active == True).all()

@router.get("/users", response_model=List[UserResponse])
def get_users(
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    return db.query(User).all()
