from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Department
from app.schemas.schemas import LoginRequest, Token, UserResponse
from app.services.auth import verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )

    dept = db.query(Department).filter(Department.id == user.department_id).first() if user.department_id else None

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "department_id": user.department_id,
        "department_code": dept.code if dept else None,
        "department_name": dept.name if dept else None
    }

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dept = db.query(Department).filter(Department.id == current_user.department_id).first() if current_user.department_id else None
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "department_id": current_user.department_id,
        "department_code": dept.code if dept else None,
        "department_name": dept.name if dept else None,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at
    }
