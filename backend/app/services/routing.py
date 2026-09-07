from typing import Dict
from sqlalchemy.orm import Session
from app.models.models import Department

CATEGORY_TO_DEPT_CODE: Dict[str, str] = {
    "IT / Network": "DEPT-IT",
    "Electrical": "DEPT-ELEC",
    "Plumbing": "DEPT-PLUMB",
    "Cleaning / Housekeeping": "DEPT-HOUSEKEEPING",
    "Laboratory": "DEPT-LAB",
    "Infrastructure / Maintenance": "DEPT-INFRA",
    "Academic": "DEPT-ACADEMIC",
    "Hostel / Canteen": "DEPT-HOSTEL",
    "Other / Manual Review": "DEPT-ADMIN"
}

DEFAULT_FALLBACK_CODE = "DEPT-ADMIN"

def route_category_to_department_code(category: str) -> str:
    """
    Deterministic rule-based routing:
    Maps AI-classified category string to the corresponding college department code.
    Explicitly decoupled from the ML model to maintain clean system boundaries.
    """
    return CATEGORY_TO_DEPT_CODE.get(category, DEFAULT_FALLBACK_CODE)

def get_department_for_category(category: str, db: Session) -> Department:
    """
    Resolves the target Department record from the database.
    If specific department is not found, safely routes to central admin.
    """
    dept_code = route_category_to_department_code(category)
    dept = db.query(Department).filter(Department.code == dept_code).first()
    if not dept:
        # Fallback to any active department or DEPT-ADMIN
        dept = db.query(Department).filter(Department.code == DEFAULT_FALLBACK_CODE).first()
        if not dept:
            dept = db.query(Department).first()
    return dept
