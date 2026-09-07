import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class UserRole:
    STUDENT = "student"
    ADMIN = "admin"

class GrievanceStatus:
    SUBMITTED = "Submitted"
    ASSIGNED = "Assigned"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    contact_email = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    users = relationship("User", back_populates="department")
    grievances = relationship("Grievance", back_populates="department")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False, default=UserRole.STUDENT)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    department = relationship("Department", back_populates="users")
    grievances = relationship("Grievance", back_populates="student", foreign_keys="Grievance.student_id")
    history_entries = relationship("GrievanceHistory", back_populates="changed_by_user")

class Grievance(Base):
    __tablename__ = "grievances"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(50), unique=True, index=True, nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # ML predicted or manually overridden category
    category = Column(String(100), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    
    # Priority engine (Rule-based)
    priority = Column(String(20), nullable=False, default="Medium")
    priority_reason = Column(String(255), nullable=True)
    
    # Workflow status
    status = Column(String(50), nullable=False, default=GrievanceStatus.SUBMITTED)
    is_low_confidence = Column(Boolean, default=False)
    resolution_remarks = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    student = relationship("User", back_populates="grievances", foreign_keys=[student_id])
    department = relationship("Department", back_populates="grievances")
    history = relationship("GrievanceHistory", back_populates="grievance", cascade="all, delete-orphan", order_by="GrievanceHistory.created_at")
    prediction = relationship("ModelPrediction", back_populates="grievance", uselist=False, cascade="all, delete-orphan")
    manual_review = relationship("ManualReview", back_populates="grievance", uselist=False, cascade="all, delete-orphan")

class GrievanceHistory(Base):
    __tablename__ = "grievance_histories"

    id = Column(Integer, primary_key=True, index=True)
    grievance_id = Column(Integer, ForeignKey("grievances.id"), nullable=False)
    changed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    previous_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    grievance = relationship("Grievance", back_populates="history")
    changed_by_user = relationship("User", back_populates="history_entries")

class ModelPrediction(Base):
    __tablename__ = "model_predictions"

    id = Column(Integer, primary_key=True, index=True)
    grievance_id = Column(Integer, ForeignKey("grievances.id"), nullable=False)
    predicted_category = Column(String(100), nullable=False)
    confidence_score = Column(Float, nullable=False)
    is_fallback = Column(Boolean, default=False)
    raw_predicted_category = Column(String(100), nullable=True)
    raw_confidence = Column(Float, nullable=True)
    top_classes_json = Column(Text, nullable=False)  # JSON string of top 3 classes
    raw_text_cleaned = Column(Text, nullable=True)
    inference_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    grievance = relationship("Grievance", back_populates="prediction")

class ManualReview(Base):
    __tablename__ = "manual_reviews"

    id = Column(Integer, primary_key=True, index=True)
    grievance_id = Column(Integer, ForeignKey("grievances.id"), nullable=False)
    original_category = Column(String(100), nullable=False)
    assigned_category = Column(String(100), nullable=True)
    reviewed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(30), default="pending")  # pending, reviewed
    review_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    grievance = relationship("Grievance", back_populates="manual_review")
