# Backend Route Security & Architecture Rules

This document outlines mandatory security and architecture rules for modifying backend routes in the ALOCA+ QA System.

---

## 🔐 Security Rules

### 1. Input Validation

**MANDATORY**: All user inputs must be validated using Pydantic schemas.

```python
# ✅ CORRECT
class TestCaseCreate(BaseModel):
    name: str  # Required, validated as string
    description: str
    module: str

@app.post("/test-cases", response_model=TestCaseResponse)
def create_test_case(test_case: TestCaseCreate, db: Session = Depends(get_db)):
    # Input is automatically validated by Pydantic
    pass

# ❌ WRONG - No validation
@app.post("/test-cases")
def create_test_case(name, description, module):
    # Raw input not validated - SECURITY RISK
    pass
```

**Rule**: Every endpoint parameter must have a corresponding Pydantic schema.

### 2. SQL Injection Prevention

**MANDATORY**: Use SQLAlchemy ORM exclusively. Never write raw SQL queries.

```python
# ✅ CORRECT - Using ORM
test_cases = db.query(TestCase).filter(TestCase.module == module).all()

# ❌ WRONG - Raw SQL
db.execute(f"SELECT * FROM test_cases WHERE module = '{module}'")
```

**Rule**: All database queries must use SQLAlchemy ORM methods.

### 3. Authentication & Authorization

**REQUIRED FOR PRODUCTION**: All endpoints currently lack authentication.

```python
# Current status: CORS open, no auth
# ⚠️  FOR PRODUCTION - Add JWT or OAuth

from jose import JWTError, jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
```

**Rule**: Authentication middleware required before deployment.

### 4. CORS Configuration

**MANDATORY**: Restrict CORS origins in production.

```python
# ❌ CURRENT (Development Only)
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# ✅ REQUIRED FOR PRODUCTION
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)
```

**Rule**: CORS origins must be restricted to explicitly allowed domains.

### 5. Error Handling

**MANDATORY**: Never expose internal errors to clients.

```python
# ✅ CORRECT
@app.post("/test-cases")
def create_test_case(test_case: TestCaseCreate, db: Session = Depends(get_db)):
    try:
        existing = db.query(TestCase).filter(TestCase.name == test_case.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Test case already exists")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating test case: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ❌ WRONG - Exposing internal error details
raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
```

**Rule**: Log internal errors but return generic messages to clients.

### 6. Rate Limiting

**RECOMMENDED**: Implement rate limiting on all public endpoints.

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/test-cases")
@limiter.limit("10/minute")
def create_test_case(request: Request, ...):
    pass
```

**Rule**: Production endpoints should have rate limiting configured.

### 7. Data Validation

**MANDATORY**: Validate data types, lengths, and formats.

```python
class DefectCreate(BaseModel):
    title: str  # Min length implicit
    description: str
    severity: DefectSeverity  # Enum validation
    assigned_to: Optional[str] = None

# Pydantic automatically validates:
# - Type checking (str, int, bool, etc.)
# - Required vs optional fields
# - Enum values
# - Custom validators
```

**Rule**: Use Pydantic Field validators for complex validation.

---

## 🏗️ Architecture Rules

### 1. Endpoint Design

**MANDATORY**: Follow REST conventions.

```
GET    /resource              - List all
GET    /resource/{id}         - Get single
POST   /resource              - Create
PATCH  /resource/{id}         - Update
DELETE /resource/{id}         - Delete
```

**Rule**: All routes must follow REST principles.

### 2. Response Format

**MANDATORY**: All responses must use consistent schema format.

```python
# ✅ CORRECT - Pydantic schema response
@app.post("/test-cases", response_model=TestCaseResponse)
def create_test_case(...):
    return db_test_case  # Automatically serialized to TestCaseResponse

# ❌ WRONG - Raw dictionary
@app.post("/test-cases")
def create_test_case(...):
    return {"id": tc.id, "name": tc.name}  # No schema validation
```

**Rule**: All endpoints must return a Pydantic response model.

### 3. Database Access

**MANDATORY**: Use dependency injection for database sessions.

```python
# ✅ CORRECT
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/test-cases")
def create_test_case(data: TestCaseCreate, db: Session = Depends(get_db)):
    pass

# ❌ WRONG - Global database connection
db = SessionLocal()
@app.post("/test-cases")
def create_test_case(data: TestCaseCreate):
    pass
```

**Rule**: All database access must use `Depends(get_db)` pattern.

### 4. ID Generation

**MANDATORY**: Use UUID strings for all primary keys.

```python
import uuid

# ✅ CORRECT
db_item = TestCase(id=str(uuid.uuid4()), name=test_case.name)

# ❌ WRONG - Sequential IDs
db_item = TestCase(id=auto_increment, name=test_case.name)

# ❌ WRONG - Untyped ID
db_item = TestCase(id=uuid.uuid4(), name=test_case.name)  # Not string
```

**Rule**: All IDs must be `str(uuid.uuid4())`.

### 5. Error Status Codes

**MANDATORY**: Use correct HTTP status codes.

```python
200  - Success (GET, PATCH)
201  - Created (POST)
204  - No Content (DELETE)
400  - Bad Request (validation error)
401  - Unauthorized (auth failed)
403  - Forbidden (auth passed but not allowed)
404  - Not Found (resource doesn't exist)
500  - Server Error (unexpected failure)
```

**Rule**: Use semantically correct HTTP status codes.

### 6. Relationship Handling

**MANDATORY**: Validate foreign key relationships.

```python
# ✅ CORRECT - Validate relationship exists
@app.post("/test-results", response_model=TestResultResponse)
def create_test_result(result: TestResultCreate, db: Session = Depends(get_db)):
    test_case = db.query(TestCase).filter(TestCase.id == result.test_case_id).first()
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    db_result = TestResult(...)
    db.add(db_result)
    db.commit()
    return db_result

# ❌ WRONG - No validation
def create_test_result(result: TestResultCreate, db: Session):
    db_result = TestResult(...)  # Assumes test_case exists
    db.add(db_result)
    db.commit()
```

**Rule**: Always validate foreign key existence before creating related records.

### 7. Filtering & Pagination

**RECOMMENDED**: Support filtering and pagination on GET endpoints.

```python
# ✅ CORRECT - With filtering
@app.get("/defects", response_model=List[DefectResponse])
def list_defects(
    status: str = None,
    severity: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Defect)
    if status:
        query = query.filter(Defect.status == status)
    if severity:
        query = query.filter(Defect.severity == severity)
    return query.offset(skip).limit(limit).all()
```

**Rule**: GET list endpoints should support filtering parameters.

### 8. Transaction Management

**MANDATORY**: Handle database transactions properly.

```python
# ✅ CORRECT - Proper transaction
@app.post("/defects")
def create_defect(defect: DefectCreate, db: Session = Depends(get_db)):
    try:
        db_defect = Defect(id=str(uuid.uuid4()), ...)
        db.add(db_defect)
        db.commit()
        db.refresh(db_defect)
        return db_defect
    except Exception as e:
        db.rollback()
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Creation failed")

# ❌ WRONG - No rollback
def create_defect(defect: DefectCreate, db: Session):
    db_defect = Defect(...)
    db.add(db_defect)
    db.commit()
    # If error occurs after add but before commit, state is corrupted
```

**Rule**: All database modifications must include proper transaction handling.

### 9. Endpoint Grouping

**RECOMMENDED**: Group related endpoints logically in code.

```python
# ✅ ORGANIZED
# Test Case Endpoints
@app.post("/test-cases", response_model=TestCaseResponse)
def create_test_case(...): pass

@app.get("/test-cases", response_model=List[TestCaseResponse])
def list_test_cases(...): pass

@app.get("/test-cases/{test_case_id}", response_model=TestCaseResponse)
def get_test_case(...): pass

# Test Result Endpoints
@app.post("/test-results", response_model=TestResultResponse)
def create_test_result(...): pass

# etc.
```

**Rule**: Group endpoints by resource type in the source code.

### 10. Documentation

**MANDATORY**: All endpoints must have docstrings.

```python
@app.post("/test-cases", response_model=TestCaseResponse)
def create_test_case(
    test_case: TestCaseCreate,
    db: Session = Depends(get_db)
) -> TestCaseResponse:
    """
    Create a new test case.
    
    - **name**: Unique test case name
    - **module**: Test module/category
    - **description**: Detailed description
    
    Returns the created test case with UUID.
    """
    existing = db.query(TestCase).filter(TestCase.name == test_case.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Test case already exists")
    
    db_test_case = TestCase(id=str(uuid.uuid4()), **test_case.dict())
    db.add(db_test_case)
    db.commit()
    db.refresh(db_test_case)
    return db_test_case
```

**Rule**: All endpoints must have clear docstrings explaining parameters and behavior.

---

## ✅ Pre-Deployment Checklist

- [ ] All endpoints have Pydantic schemas
- [ ] All database queries use ORM (no raw SQL)
- [ ] All errors return generic messages (logs get details)
- [ ] CORS origins are restricted
- [ ] Rate limiting is configured
- [ ] Foreign key relationships are validated
- [ ] HTTP status codes are correct
- [ ] Transactions include rollback handling
- [ ] All endpoints have docstrings
- [ ] Environment variables are configured (.env.production)
- [ ] Authentication is implemented (for production)
- [ ] Logging is configured
- [ ] No sensitive data in error messages

---

## 📝 Example: Adding a New Endpoint

Follow this template when adding endpoints:

```python
# 1. Define schema in schemas.py
class MyResourceCreate(BaseModel):
    field1: str
    field2: int

class MyResourceResponse(BaseModel):
    id: str
    field1: str
    field2: int
    created_at: datetime

# 2. Define model in models.py
class MyResource(Base):
    __tablename__ = "my_resources"
    id = Column(String, primary_key=True)
    field1 = Column(String)
    field2 = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

# 3. Add endpoint in main.py
@app.post("/my-resource", response_model=MyResourceResponse)
def create_my_resource(
    resource: MyResourceCreate,
    db: Session = Depends(get_db)
) -> MyResourceResponse:
    """Create a new resource."""
    db_resource = MyResource(id=str(uuid.uuid4()), **resource.dict())
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource

@app.get("/my-resource", response_model=List[MyResourceResponse])
def list_my_resources(db: Session = Depends(get_db)) -> List[MyResourceResponse]:
    """List all resources."""
    return db.query(MyResource).all()

@app.get("/my-resource/{resource_id}", response_model=MyResourceResponse)
def get_my_resource(resource_id: str, db: Session = Depends(get_db)) -> MyResourceResponse:
    """Get a specific resource by ID."""
    resource = db.query(MyResource).filter(MyResource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource
```

---

## 🔗 Related Documentation

- `CLAUDE.md` - General development guidelines
- `README.md` - Project setup and overview
- `DEVELOPMENT.md` - How to extend the system
