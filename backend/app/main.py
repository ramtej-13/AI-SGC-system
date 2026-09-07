from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import auth, grievances, department, admin
from app.ml.predict import get_classifier

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-style Academic System for AI-Based Student Grievance Classification and Smart Routing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(grievances.router, prefix=settings.API_V1_STR)
app.include_router(department.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def startup_event():
    # Warm up ML classifier
    classifier = get_classifier()
    print(f"[*] System Startup: Grievance Classifier ready state: {classifier.is_ready}")

@app.get("/")
def root():
    return {
        "system": settings.PROJECT_NAME,
        "version": "1.0.0",
        "status": "operational",
        "api_docs": "/docs",
        "api_base": settings.API_V1_STR
    }

@app.get("/api/health")
def health():
    classifier = get_classifier()
    return {
        "status": "healthy",
        "model_loaded": classifier.is_ready,
        "active_threshold": classifier.DEFAULT_THRESHOLD
    }
