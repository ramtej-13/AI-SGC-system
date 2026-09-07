import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.models import User, Department, UserRole
from app.services.auth import get_password_hash, create_access_token

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    depts = [
        Department(code="DEPT-IT", name="IT & Network Services", is_active=True),
        Department(code="DEPT-ELEC", name="Electrical Maintenance", is_active=True),
        Department(code="DEPT-PLUMB", name="Plumbing & Water Works", is_active=True),
        Department(code="DEPT-HOUSEKEEPING", name="Sanitation & Housekeeping", is_active=True),
        Department(code="DEPT-LAB", name="Laboratory & Technical Infrastructure", is_active=True),
        Department(code="DEPT-INFRA", name="Estate & Civil Infrastructure", is_active=True),
        Department(code="DEPT-ACADEMIC", name="Academic Affairs & Examination", is_active=True),
        Department(code="DEPT-HOSTEL", name="Hostel Administration & Dining", is_active=True),
        Department(code="DEPT-ADMIN", name="General Helpdesk & Central Administration", is_active=True),
    ]
    db.add_all(depts)
    db.commit()

    admin_dept = db.query(Department).filter(Department.code == "DEPT-ADMIN").first()

    users = [
        User(id=1, email="admin@test.local", full_name="Admin User", role=UserRole.ADMIN, hashed_password=get_password_hash("Pass@123"), department_id=admin_dept.id),
        User(id=2, email="student1@test.local", full_name="Student One", role=UserRole.STUDENT, hashed_password=get_password_hash("Pass@123")),
        User(id=3, email="student2@test.local", full_name="Student Two", role=UserRole.STUDENT, hashed_password=get_password_hash("Pass@123")),
    ]
    db.add_all(users)
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def student_auth_headers():
    token = create_access_token(data={"sub": "student1@test.local", "role": UserRole.STUDENT, "id": 2})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def student2_auth_headers():
    token = create_access_token(data={"sub": "student2@test.local", "role": UserRole.STUDENT, "id": 3})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_auth_headers():
    token = create_access_token(data={"sub": "admin@test.local", "role": UserRole.ADMIN, "id": 1})
    return {"Authorization": f"Bearer {token}"}
