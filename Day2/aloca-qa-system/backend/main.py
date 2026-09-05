from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
import uuid
import logging
from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from models import Base, TestCase, TestResult, Defect, QualityMetric, TestCaseStatus, DefectSeverity, DefectStatus
from schemas import (
    TestCaseCreate, TestCaseResponse, TestResultCreate, TestResultResponse,
    DefectCreate, DefectResponse, DefectUpdate, QualityMetricResponse,
    DashboardStatsResponse, SearchRequest, SearchResponse
)
from mcp_client import search_web

load_dotenv()
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./aloca_qa.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ALOCA+ QA System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting Configuration
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."}
    )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
@limiter.limit("300/minute")
def read_root(request: Request):
    return {"message": "ALOCA+ QA System API", "version": "1.0.0"}

@app.get("/health")
@limiter.limit("200/minute")
def health_check(request: Request):
    return {"status": "healthy"}

@app.get("/dashboard/stats", response_model=DashboardStatsResponse)
@limiter.limit("60/minute")
def get_dashboard_stats(request: Request, db: Session = Depends(get_db)):
    total_cases = db.query(func.count(TestCase.id)).scalar() or 0
    total_defects = db.query(func.count(Defect.id)).scalar() or 0
    critical_defects = db.query(func.count(Defect.id)).filter(Defect.severity == DefectSeverity.CRITICAL).scalar() or 0

    passed = db.query(func.count(TestResult.id)).filter(TestResult.status == TestCaseStatus.PASSED).scalar() or 0
    failed = db.query(func.count(TestResult.id)).filter(TestResult.status == TestCaseStatus.FAILED).scalar() or 0
    blocked = db.query(func.count(TestResult.id)).filter(TestResult.status == TestCaseStatus.BLOCKED).scalar() or 0

    pass_rate = (passed / (passed + failed + blocked) * 100) if (passed + failed + blocked) > 0 else 0

    today = datetime.utcnow().date()
    tests_today = db.query(TestResult).filter(
        func.date(TestResult.executed_at) == today
    ).all()

    passed_today = len([t for t in tests_today if t.status == TestCaseStatus.PASSED])
    failed_today = len([t for t in tests_today if t.status == TestCaseStatus.FAILED])
    blocked_today = len([t for t in tests_today if t.status == TestCaseStatus.BLOCKED])

    return DashboardStatsResponse(
        total_test_cases=total_cases,
        total_defects=total_defects,
        pass_rate=round(pass_rate, 2),
        critical_defects=critical_defects,
        tests_passed_today=passed_today,
        tests_failed_today=failed_today,
        tests_blocked_today=blocked_today,
    )

@app.post("/test-cases", response_model=TestCaseResponse)
@limiter.limit("10/minute")
def create_test_case(request: Request, test_case: TestCaseCreate, db: Session = Depends(get_db)):
    existing = db.query(TestCase).filter(TestCase.name == test_case.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Test case already exists")

    db_test_case = TestCase(
        id=str(uuid.uuid4()),
        name=test_case.name,
        description=test_case.description,
        module=test_case.module
    )
    db.add(db_test_case)
    db.commit()
    db.refresh(db_test_case)
    return db_test_case

@app.get("/test-cases", response_model=list[TestCaseResponse])
@limiter.limit("100/minute")
def list_test_cases(request: Request, module: str = None, db: Session = Depends(get_db)):
    query = db.query(TestCase)
    if module:
        query = query.filter(TestCase.module == module)
    return query.all()

@app.get("/test-cases/{test_case_id}", response_model=TestCaseResponse)
@limiter.limit("100/minute")
def get_test_case(request: Request, test_case_id: str, db: Session = Depends(get_db)):
    test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    return test_case

@app.post("/test-results", response_model=TestResultResponse)
@limiter.limit("20/minute")
def create_test_result(request: Request, result: TestResultCreate, db: Session = Depends(get_db)):
    test_case = db.query(TestCase).filter(TestCase.id == result.test_case_id).first()
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")

    db_result = TestResult(
        id=str(uuid.uuid4()),
        test_case_id=result.test_case_id,
        status=result.status,
        execution_time_ms=result.execution_time_ms,
        notes=result.notes
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

@app.get("/test-results", response_model=list[TestResultResponse])
@limiter.limit("100/minute")
def list_test_results(request: Request, test_case_id: str = None, db: Session = Depends(get_db)):
    query = db.query(TestResult)
    if test_case_id:
        query = query.filter(TestResult.test_case_id == test_case_id)
    return query.order_by(TestResult.executed_at.desc()).all()

@app.post("/defects", response_model=DefectResponse)
@limiter.limit("10/minute")
def create_defect(request: Request, defect: DefectCreate, db: Session = Depends(get_db)):
    db_defect = Defect(
        id=str(uuid.uuid4()),
        title=defect.title,
        description=defect.description,
        severity=defect.severity,
        test_case_id=defect.test_case_id,
        assigned_to=defect.assigned_to
    )
    db.add(db_defect)
    db.commit()
    db.refresh(db_defect)
    return db_defect

@app.get("/defects", response_model=list[DefectResponse])
@limiter.limit("100/minute")
def list_defects(request: Request, status: str = None, severity: str = None, db: Session = Depends(get_db)):
    query = db.query(Defect)
    if status:
        query = query.filter(Defect.status == status)
    if severity:
        query = query.filter(Defect.severity == severity)
    return query.order_by(Defect.created_at.desc()).all()

@app.get("/defects/{defect_id}", response_model=DefectResponse)
@limiter.limit("100/minute")
def get_defect(request: Request, defect_id: str, db: Session = Depends(get_db)):
    defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if not defect:
        raise HTTPException(status_code=404, detail="Defect not found")
    return defect

@app.patch("/defects/{defect_id}", response_model=DefectResponse)
@limiter.limit("20/minute")
def update_defect(request: Request, defect_id: str, update: DefectUpdate, db: Session = Depends(get_db)):
    defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if not defect:
        raise HTTPException(status_code=404, detail="Defect not found")

    if update.status:
        defect.status = update.status
        if update.status == DefectStatus.RESOLVED or update.status == DefectStatus.CLOSED:
            defect.resolved_at = datetime.utcnow()
    if update.assigned_to:
        defect.assigned_to = update.assigned_to
    if update.description:
        defect.description = update.description

    defect.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(defect)
    return defect

@app.get("/metrics", response_model=list[QualityMetricResponse])
@limiter.limit("60/minute")
def get_metrics(request: Request, days: int = 7, db: Session = Depends(get_db)):
    start_date = datetime.utcnow() - timedelta(days=days)
    metrics = db.query(QualityMetric).filter(QualityMetric.date >= start_date).order_by(QualityMetric.date.desc()).all()
    return metrics

@app.post("/metrics/generate")
@limiter.limit("5/minute")
def generate_metrics(request: Request, db: Session = Depends(get_db)):
    passed = db.query(func.count(TestResult.id)).filter(TestResult.status == TestCaseStatus.PASSED).scalar() or 0
    failed = db.query(func.count(TestResult.id)).filter(TestResult.status == TestCaseStatus.FAILED).scalar() or 0
    blocked = db.query(func.count(TestResult.id)).filter(TestResult.status == TestCaseStatus.BLOCKED).scalar() or 0
    pending = db.query(func.count(TestResult.id)).filter(TestResult.status == TestCaseStatus.PENDING).scalar() or 0
    total = passed + failed + blocked + pending

    defects_open = db.query(func.count(Defect.id)).filter(Defect.status == DefectStatus.OPEN).scalar() or 0
    critical = db.query(func.count(Defect.id)).filter(Defect.severity == DefectSeverity.CRITICAL).scalar() or 0
    high = db.query(func.count(Defect.id)).filter(Defect.severity == DefectSeverity.HIGH).scalar() or 0

    pass_rate = (passed / total * 100) if total > 0 else 0

    metric = QualityMetric(
        id=str(uuid.uuid4()),
        total_test_cases=total,
        passed_tests=passed,
        failed_tests=failed,
        blocked_tests=blocked,
        pending_tests=pending,
        pass_rate=pass_rate,
        defects_open=defects_open,
        defects_critical=critical,
        defects_high=high
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric

@app.post("/search", response_model=SearchResponse)
@limiter.limit("20/minute")
async def search(request: Request, payload: SearchRequest):
    """Search the web via Apify's MCP-hosted rag-web-browser actor."""
    try:
        results = await search_web(payload.query, payload.max_results)
        return SearchResponse(query=payload.query, results=results)
    except RuntimeError as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=502, detail="Search service unavailable")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
