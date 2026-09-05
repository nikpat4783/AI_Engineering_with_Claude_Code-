from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Float, Enum, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class TestCaseStatus(str, enum.Enum):
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    PENDING = "pending"

class DefectSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class DefectStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(String, primary_key=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    module = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    test_results = relationship("TestResult", back_populates="test_case", cascade="all, delete-orphan")

class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(String, primary_key=True)
    test_case_id = Column(String, ForeignKey("test_cases.id"), index=True)
    status = Column(Enum(TestCaseStatus), default=TestCaseStatus.PENDING)
    executed_at = Column(DateTime, default=datetime.utcnow)
    execution_time_ms = Column(Integer)
    notes = Column(Text)

    test_case = relationship("TestCase", back_populates="test_results")

class Defect(Base):
    __tablename__ = "defects"

    id = Column(String, primary_key=True)
    title = Column(String, index=True)
    description = Column(Text)
    severity = Column(Enum(DefectSeverity), default=DefectSeverity.MEDIUM)
    status = Column(Enum(DefectStatus), default=DefectStatus.OPEN)
    test_case_id = Column(String, ForeignKey("test_cases.id"))
    assigned_to = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

class QualityMetric(Base):
    __tablename__ = "quality_metrics"

    id = Column(String, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    total_test_cases = Column(Integer)
    passed_tests = Column(Integer)
    failed_tests = Column(Integer)
    blocked_tests = Column(Integer)
    pending_tests = Column(Integer)
    pass_rate = Column(Float)
    defects_open = Column(Integer)
    defects_critical = Column(Integer)
    defects_high = Column(Integer)
