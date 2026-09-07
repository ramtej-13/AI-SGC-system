from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Auth schemas
class LoginRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    full_name: str
    role: str
    department_id: Optional[int] = None
    department_code: Optional[str] = None
    department_name: Optional[str] = None

class TokenData(BaseModel):
    email: Optional[str] = None

# User schemas
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: str
    department_id: Optional[int] = None
    is_active: bool
    created_at: datetime

# Department schemas
class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: Optional[str] = None
    contact_email: Optional[str] = None
    is_active: bool

# Grievance schemas
class GrievanceCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200, description="Short summary of issue")
    description: str = Field(..., min_length=10, max_length=2000, description="Detailed student grievance explanation")

class GrievanceStatusUpdate(BaseModel):
    status: str = Field(..., description="Target workflow status")
    remarks: Optional[str] = Field(None, max_length=1000, description="Audit/resolution remarks")

class ManualReviewAction(BaseModel):
    assigned_category: str
    assigned_department_id: Optional[int] = None
    review_notes: Optional[str] = None

class TopPredictionItem(BaseModel):
    category: str
    probability: float

class ModelPredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    predicted_category: str
    confidence_score: float
    is_fallback: bool
    raw_predicted_category: Optional[str] = None
    raw_confidence: Optional[float] = None
    top_predictions: List[TopPredictionItem] = []
    inference_time_ms: Optional[float] = None

class GrievanceHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    previous_status: Optional[str] = None
    new_status: str
    remarks: Optional[str] = None
    changed_by_name: Optional[str] = None
    created_at: datetime

class GrievanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_number: str
    title: str
    description: str
    category: str
    department_id: int
    department_code: Optional[str] = None
    department_name: Optional[str] = None
    priority: str
    priority_reason: Optional[str] = None
    status: str
    is_low_confidence: bool
    resolution_remarks: Optional[str] = None
    student_id: int
    student_name: Optional[str] = None
    student_email: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    prediction: Optional[ModelPredictionResponse] = None
    history: List[GrievanceHistoryResponse] = []

# Live generalization test
class ModelGeneralizationTestRequest(BaseModel):
    text: str = Field(..., min_length=5, max_length=2000)
    threshold: Optional[float] = 0.70

class ModelGeneralizationTestResponse(BaseModel):
    predicted_category: str
    confidence: float
    is_low_confidence: bool
    suggested_department: str
    suggested_priority: str
    priority_reason: str
    top_predictions: List[TopPredictionItem]
    raw_predicted_category: str
    raw_confidence: float
    cleaned_text: str

# Analytics schemas
class AnalyticsResponse(BaseModel):
    total_grievances: int
    status_distribution: Dict[str, int]
    category_distribution: Dict[str, int]
    department_distribution: Dict[str, int]
    priority_distribution: Dict[str, int]
    low_confidence_count: int
    resolved_count: int
    avg_resolution_hours: Optional[float] = None
