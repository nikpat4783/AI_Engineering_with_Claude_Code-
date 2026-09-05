from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TestCaseStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    PENDING = "pending"

class DefectSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class DefectStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TestCaseCreate(BaseModel):
    name: str
    description: str
    module: str

class TestCaseResponse(BaseModel):
    id: str
    name: str
    description: str
    module: str
    created_at: datetime
    updated_at: datetime

class TestResultCreate(BaseModel):
    test_case_id: str
    status: TestCaseStatus
    execution_time_ms: int
    notes: Optional[str] = None

class TestResultResponse(BaseModel):
    id: str
    test_case_id: str
    status: TestCaseStatus
    executed_at: datetime
    execution_time_ms: int
    notes: Optional[str]

class DefectCreate(BaseModel):
    title: str
    description: str
    severity: DefectSeverity
    test_case_id: Optional[str] = None
    assigned_to: Optional[str] = None

class DefectResponse(BaseModel):
    id: str
    title: str
    description: str
    severity: DefectSeverity
    status: DefectStatus
    test_case_id: Optional[str]
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]

class DefectUpdate(BaseModel):
    status: Optional[DefectStatus] = None
    assigned_to: Optional[str] = None
    description: Optional[str] = None

class QualityMetricResponse(BaseModel):
    id: str
    date: datetime
    total_test_cases: int
    passed_tests: int
    failed_tests: int
    blocked_tests: int
    pending_tests: int
    pass_rate: float
    defects_open: int
    defects_critical: int
    defects_high: int

class DashboardStatsResponse(BaseModel):
    total_test_cases: int
    total_defects: int
    pass_rate: float
    critical_defects: int
    tests_passed_today: int
    tests_failed_today: int
    tests_blocked_today: int

class SearchResultItem(BaseModel):
    title: str
    url: str
    snippet: str

class SearchRequest(BaseModel):
    query: str
    max_results: int = 10

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
